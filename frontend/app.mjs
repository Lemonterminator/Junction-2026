import { createDemo, advanceDemo, displayState, validateTelemetry, stageProgress, explanation } from './telemetry.mjs';
import { Cell3D } from './cell3d.mjs';
import { BrickViews, BRICK_COLOURS, demoDefect } from './brickviews.mjs';
import { LatestImageLoader } from './image-loader.mjs';
import { InferenceWindow, mountPerformance } from './performance.mjs';
import { mountIntro } from './intro.mjs';
import { parseCommand, ACTIONS } from './command.mjs';
import { studioView, inspectionSnapshot, SessionRecorder, ageText, stopPlan, stopStatus, leavingLiveStops, liveBrickModel } from './studio.mjs';
import { cycleView, cycleSnapshot, mapLayout, cycleRequest } from './cell.mjs';

const $ = id => document.getElementById(id);
/** The 3D cell is illustrative; without WebGL (some laptops, remote desktops) the rest of the page must still work. */
function makeScene3d() {
	try { return new Cell3D($('scene'), $('annotations')); }
	catch (error) {
		const note = Object.assign(document.createElement('div'), {id: 'scene', className: 'scene-fallback', textContent: `3D view unavailable here (${error.message}). Everything else works.`});
		$('scene').replaceWith(note);
		return {setState() {}, focus() {}, annotate() {}, reset() {}};
	}
}
const scene3d = makeScene3d();
const brickViews = (() => {
	try { return new BrickViews($('brick-canvas')); }
	catch (error) {
		$('brick-canvas').replaceWith(Object.assign(document.createElement('div'), {id: 'brick-canvas', className: 'scene-fallback', textContent: '3D brick views unavailable here.'}));
		return {show() {}};
	}
})();
const inferenceWindow = new InferenceWindow();
const recorder = new SessionRecorder({maxSeconds: 90});

let source = 'demo';          // demo | live | replay
let studioLinked = false;     // the server answered /api/studio/state once: a backend run may exist
let stopRequested = false;    // a stop was sent and the server has not yet reported the arm held
let lastInspectionAt = null;
let state = null;             // current v1 snapshot shown in the panels (null = idle)
let part = 0;
let timer = null;             // demo stepper
let studio = null;            // last /api/studio/state
let liveSeq = 0;
let tourIndex = -1;
let recording = false, recordTimer = null, replayTimer = null, replayStart = 0;
let cell = null;              // last /api/cell/state (null = no cell link)
let cellLinked = false;       // the server has a cell link: a cycle may exist
let lastCycleKey = null;      // what of the cycle the decision panel last showed

// ------------------------------------------------------------------ decision, meter, timings
const SEGMENTS = 25;
const segs = Array.from({length: SEGMENTS}, () => { const s = document.createElement('div'); s.className = 'seg'; $('segs').append(s); return s; });
let meter = 0, meterTarget = 0;
function meterZones(th) {
	segs.forEach((s, i) => {
		const v = (i + .5) / SEGMENTS;
		s.classList.toggle('z1', Boolean(th) && v >= th.normal_below && v <= th.defective_above);
		s.classList.toggle('z2', Boolean(th) && v > th.defective_above);
	});
	const marks = th ? [[0, '0'], [th.normal_below, th.normal_below.toFixed(2).replace(/^0/, '')], ...(th.defective_above !== th.normal_below ? [[th.defective_above, th.defective_above.toFixed(2).replace(/^0/, '')]] : []), [1, '1']] : [[0, '0'], [1, '1']];
	$('scale').replaceChildren(...marks.map(([v, text]) => { const s = document.createElement('span'); s.style.left = `${v * 100}%`; s.textContent = text; return s; }));
}
function animateMeter() {
	meter += (meterTarget - meter) * 0.18;
	if (Math.abs(meterTarget - meter) < 0.002) meter = meterTarget;
	const lit = Math.round(meter * SEGMENTS);
	segs.forEach((s, i) => s.classList.toggle('on', i < lit));
	requestAnimationFrame(animateMeter);
}
requestAnimationFrame(animateMeter);

const toneOf = s => !s ? 'idle' : s.stage === 'fault' ? 'fault' : ['perceive', 'detect'].includes(s.stage) ? 'idle' : s.label;
const fmtMs = v => v === null || v === undefined ? '—' : v >= 1000 ? `${(v / 1000).toFixed(1)}s` : `${v.toFixed(1)}ms`;

function render() {
	const s = state;
	const panel = $('decision-panel');
	panel.className = `panel decision-panel ${toneOf(s)}`;
	if (!s) {
		$('decision-title').textContent = 'Ready';
		$('destination').textContent = 'No part yet';
		$('destination-dot').className = 'led';
		$('explanation').textContent = 'Inspect a part to see the decision.';
		$('decision-score').textContent = '—'; $('task').textContent = '—'; $('outcome').textContent = 'Not verified';
		$('score-value').textContent = '0.00'; $('score-value').className = 'big'; meterTarget = 0; meterZones({normal_below: .4, defective_above: .6});
		$('threshold-copy').textContent = '';
		document.querySelectorAll('[data-stage]').forEach(el => el.classList.remove('active', 'passed'));
		$('progress-text').textContent = 'Ready';
		renderButtons(); return;
	}
	const view = displayState(s);
	const demo = s.mode === 'demo', fault = s.stage === 'fault';
	const decided = ['reason', 'act', 'verify', 'complete', 'review', 'fault'].includes(s.stage);
	$('decision-title').textContent = decided ? (fault ? 'Stopped' : {normal: 'Pass', defective: 'Reject', uncertain: 'Review'}[s.label]) : s.stage === 'detect' ? 'Scoring…' : 'Inspecting…';
	$('destination').textContent = !decided ? 'Deciding' : fault ? 'Check the arm' : view.destination.replace('bowl', 'plate');
	$('destination-dot').className = `led ${decided ? (s.destination === 'green' ? 'green' : s.destination === 'pink' ? 'red' : 'amber') : ''}`;
	$('episode-tag').textContent = demo ? `Part ${part}` : s.episode_id;
	$('explanation').textContent = decided ? explanation(s).replace(/bowl/g, 'plate') : s.stage === 'detect' ? 'Scoring the brick.' : 'Taking a picture of the part.';
	const showScore = decided || s.stage === 'detect';
	$('decision-score').textContent = showScore ? view.score : '—';
	$('task').textContent = decided && s.task && !fault ? `“${s.task}”` : decided ? 'Nothing (arm stays still)' : '—';
	$('outcome').textContent = s.stage === 'complete' && s.outcome ? `In the ${s.outcome} plate` : 'Not verified';
	meterZones(s.thresholds);
	meterTarget = showScore && Number.isFinite(s.score) ? s.score : 0;
	const big = $('score-value');
	big.textContent = showScore ? view.score.replace('—', '-.--') : '0.00';
	big.className = `big ${showScore && Number.isFinite(s.score) ? 'on' : ''}`;
	big.style.color = !showScore || !Number.isFinite(s.score) ? '' : s.label === 'defective' ? 'var(--red)' : s.label === 'uncertain' ? 'var(--amber)' : 'var(--g)';
	$('threshold-copy').textContent = s.thresholds ? `Pass below ${s.thresholds.normal_below.toFixed(2)}, reject above ${s.thresholds.defective_above.toFixed(2)}, review in between.` : 'No thresholds.';
	const stages = stageProgress(s);
	document.querySelectorAll('[data-stage]').forEach((el, i) => { el.classList.toggle('active', stages[i].active); el.classList.toggle('passed', stages[i].passed); });
	$('reason-stage').textContent = decided ? (s.destination ? view.destination.replace('bowl', 'plate') : 'Review') : 'Decision';
	$('act-stage').textContent = view.actStatus; $('verify-stage').textContent = view.verifyStatus;
	const status = {perceive: 'Taking a picture', detect: 'Scoring', reason: 'Deciding', act: 'Placing the part', verify: 'Checking placement', complete: 'Done', review: 'Waiting for a person', fault: 'Stopped'};
	$('progress-text').textContent = `${demo ? 'Demo · ' : s.mode === 'replay' ? 'Replay · ' : 'Live · '}${status[s.stage]}`;
	inferenceWindow.add(s);
	const summary = inferenceWindow.summary();
	$('inference-median').textContent = fmtMs(summary.median); $('inference-p95').textContent = fmtMs(summary.p95);
	$('inference-samples').textContent = summary.count ? `${summary.count} measured cycles on ${summary.device ?? 'an unverified device'}` : demo ? 'Demo parts have no timings.' : 'No measured cycles yet.';
	$('inference-device').textContent = s.device ?? 'Unverified';
	for (const row of document.querySelectorAll('[data-timing]')) {
		const v = s.timings_ms[row.dataset.timing];
		row.querySelector('strong').textContent = fmtMs(v);
		row.querySelector('.bar i').style.width = v === null ? '0' : `${Math.min(100, Math.max(3, Math.log10(1 + v) / 4.3 * 100))}%`;
	}
	if (demo) {
		const seed = part * 7 + 1;
		brickViews.show({label: decided ? s.label : 'none', colour: BRICK_COLOURS[part % BRICK_COLOURS.length], defect: decided || s.stage === 'detect' ? demoDefect(s.label, seed) : null});
		scene3d.setState(s, {brickColor: BRICK_COLOURS[part % BRICK_COLOURS.length], defect: s.label === 'normal' ? null : (demoDefect(s.label, seed)?.kind ?? null)});
	} else {
		scene3d.setState(s);
	}
	updatePitch(summary);
	renderButtons();
}

function renderButtons() {
	const busy = Boolean(timer);
	const live = source === 'live';
	$('inspect').disabled = source === 'replay' || busy || (live && !studio?.inspector);
	$('inspect').firstChild.textContent = live ? 'Inspect live part ' : busy ? 'Playing… ' : 'Play a demo part ';
	$('inspect').title = live ? (studio?.inspector ? 'Score the newest frame of the chosen camera' : 'Needs the dashboard started with --studio-url and --purity or --anomaly-model')
		: 'Illustrative animation. Switch to Live to inspect a real part.';
	$('play').disabled = source !== 'demo';
	$('scenario').disabled = source !== 'demo';
	$('play').textContent = busy ? 'Pause demo' : 'Play demo';
}

function updatePitch(summary) {
	if (summary.count && summary.mode === 'real') {
		$('fact-npu').textContent = `${summary.median.toFixed(1)} ms`;
		$('fact-npu-note').textContent = `Inference on ${summary.device ?? 'this laptop'} (live median)`;
	}
}

// ------------------------------------------------------------------ demo
function pause() { clearInterval(timer); timer = null; renderButtons(); }
function runDemo(scenario, {stopAt = null} = {}) {
	pause();
	part++;
	state = createDemo(scenario);
	render();
	timer = setInterval(() => {
		const next = advanceDemo(state);
		if (next === state || (stopAt && state.stage === stopAt)) { pause(); planDone(); return; }
		state = next; render(); planProgress(state.stage);
		if (['complete', 'review', 'fault'].includes(state.stage)) { pause(); planDone(); }
	}, 1150);
	renderButtons();
}
function pickScenario() { const r = Math.random(); return r < 0.45 ? 'normal' : r < 0.82 ? 'defective' : 'uncertain'; }

$('inspect').addEventListener('click', () => {
	if (source === 'live') { execute(parseCommand('inspect')); return; }
	runDemo(part === 0 ? $('scenario').value : pickScenario());
});
$('play').addEventListener('click', () => timer ? pause() : runDemo($('scenario').value));
$('scenario').addEventListener('change', () => { pause(); runDemo($('scenario').value); });
$('reset-view').addEventListener('click', () => scene3d.reset());
document.addEventListener('keydown', e => {
	if ($('intro-dialog').open || e.code !== 'Space' || e.repeat || /^(INPUT|SELECT|TEXTAREA|BUTTON|A|CANVAS)$/.test(e.target.tagName)) return;
	e.preventDefault(); if (!$('inspect').disabled) $('inspect').click();
});

/** Snapshots from a backend file bridge still work; they switch the view to that source. */
window.addEventListener('sorter:telemetry', event => {
	if (!validateTelemetry(event.detail) || source === 'replay') return;
	pause(); state = structuredClone(event.detail); render();
});

// ------------------------------------------------------------------ source switch + badges
function setBadge(id, tone, text, blink = false) {
	const el = $(id); el.className = `status ${blink ? 'live' : tone}`;
	el.querySelector('span').textContent = text;
}
function setSource(next) {
	if (next === 'replay' && !recorder.entries.length) { reply('refuse', 'Nothing recorded yet', 'Record something in Live first.'); return; }
	// Leaving Live hides the cameras and the cell panel, so a run or cycle that may still move is stopped first.
	if (leavingLiveStops(source, next, studio?.run) || (source === 'live' && next !== 'live' && cell?.cycle?.active)) stopEverything();
	source = next;
	document.querySelectorAll('[data-source]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.source === source)));
	stopReplay();
	if (source === 'demo') { $('brick-source').textContent = 'Demo'; $('brick-note').textContent = 'The circle marks where the defect is.'; }
	if (source === 'live') { pause(); $('brick-source').textContent = 'Live'; $('brick-note').textContent = 'Left: what the model scored.'; }
	if (source === 'replay') { pause(); startReplay(); }
	updateBadges(); renderRunConfig(); renderCell(); render();
}
document.querySelectorAll('[data-source]').forEach(b => b.addEventListener('click', () => setSource(b.dataset.source)));

function updateBadges() {
	if (source === 'demo') setBadge('source-badge', 'warn', 'Demo');
	else if (source === 'replay') setBadge('source-badge', 'warn', 'Replay (recorded)');
	else setBadge('source-badge', '', studio?.reachable ? 'Live' : 'Waiting for Studio', Boolean(studio?.reachable));
	const v = studioView(studio);
	setBadge('studio-badge', v.status === 'connected' ? 'ok' : v.status === 'unreachable' ? 'bad' : '', v.status === 'connected' ? `Studio: ${studio.project?.name ?? 'connected'}` : v.status === 'unreachable' ? 'Studio unreachable' : 'Studio not connected');
	const ins = studio?.inspector;
	setBadge('device-badge', ins ? 'ok' : '', ins ? `Inspector on ${ins.device ?? '?'}` : 'No inspector');
	$('live-headline').textContent = v.status === 'off' ? 'Studio link off. Start the dashboard with --studio-url to see the cell’s cameras.' : v.headline;
	const unlocked = Boolean(studio?.control_enabled || cell?.control_enabled);
	$('control-lock').textContent = unlocked ? 'Arm unlocked' : 'Arm locked';
	$('control-lock').style.color = unlocked ? 'var(--amber)' : '';
}

// ------------------------------------------------------------------ live: Studio polling and camera tiles
const tiles = new Map();
function cameraTile(camera) {
	let tile = tiles.get(camera.id);
	if (!tile) {
		const el = document.createElement('article');
		el.className = 'cam';
		el.innerHTML = '<div class="frame"><div class="waiting"></div><img alt="" hidden><span class="badge-live" hidden></span></div><div class="meta"><b></b><span class="state"></span></div>';
		const img = el.querySelector('img');
		const loader = new LatestImageLoader(img, () => {});
		tile = {el, img, loader, lastSeq: null};
		tiles.set(camera.id, tile);
	}
	return tile;
}
const STATE_TEXT = {live: 'Live', session: 'Live (run)', stale: 'Stale', held: 'In use by Studio', error: 'Error', waiting: 'Connecting'};
function renderCameras(view, {replayFrames = null} = {}) {
	const grid = $('camera-grid');
	if (!view.cameras.length) {
		grid.replaceChildren(Object.assign(document.createElement('div'), {className: 'camera-empty', textContent: view.status === 'connected' ? 'This Studio project has no cameras yet.' : view.headline}));
		tiles.clear(); return;
	}
	const els = view.cameras.map(camera => {
		const tile = cameraTile(camera);
		const replay = replayFrames !== null;
		const st = replay ? (replayFrames[camera.id] ? 'live' : 'waiting') : camera.state;
		tile.el.className = `cam ${st}`;
		tile.el.querySelector('b').textContent = camera.name;
		tile.el.querySelector('.state').textContent = replay ? 'Replay' : `${STATE_TEXT[st]}${['live', 'stale'].includes(st) ? ' · ' + camera.age : ''}`;
		const badge = tile.el.querySelector('.badge-live');
		badge.hidden = !(replay || st === 'live' || st === 'session');
		badge.className = `badge-live ${replay ? 'replay' : 'live'}`; badge.textContent = replay ? 'Replay' : 'Live';
		const waiting = tile.el.querySelector('.waiting');
		if (replay) {
			const url = replayFrames[camera.id];
			tile.img.hidden = !url; if (url) tile.img.src = url;
			waiting.hidden = Boolean(url);
			waiting.textContent = url ? '' : 'Not recorded';
		} else {
			const showImage = ['live', 'stale', 'session'].includes(st) || camera.sequence !== null;
			tile.img.hidden = !showImage;
			waiting.hidden = showImage && st !== 'error';
			waiting.textContent = st === 'held' ? 'Studio is using this camera.' : st === 'error' ? camera.error : 'Connecting…';
		}
		return tile.el;
	});
	if (grid.children.length !== els.length || els.some((el, i) => grid.children[i] !== el)) grid.replaceChildren(...els);
}

let frameTick = 0;
function pumpFrames() {
	if (source === 'live' && studio?.reachable && !document.hidden) {
		frameTick++;
		for (const camera of studio.cameras) {
			const tile = tiles.get(camera.id);
			if (tile) tile.loader.setSource(`/api/studio/frame/${encodeURIComponent(camera.id)}.jpg?n=${frameTick}`);
		}
	}
	setTimeout(pumpFrames, 120);
}
pumpFrames();

async function pollStudio() {
	try {
		const response = await fetch('/api/studio/state', {cache: 'no-store', signal: AbortSignal.timeout(4000)});
		studio = response.status === 204 ? null : await response.json();
		if (studio) studioLinked = true;
	} catch { studio = studio ? {...studio, reachable: false, error: 'dashboard server not responding'} : null; }
	updateBadges();
	if (source !== 'replay') renderCameras(studioView(studio));
	renderRunConfig();
	renderRun();
	const inspection = studio?.inspection;
	// During a cycle each view is one inspection; the decision panel follows the cycle's decision over all views.
	if (cell?.cycle?.active && inspection) lastInspectionAt = inspection.timestamp;
	if (source === 'live' && inspection && inspection.timestamp !== lastInspectionAt) showInspection(inspection, inspection.frame_age_ms ?? 0);
	const busy = source === 'live' || stopRequested || Boolean(studioView(studio).run?.stoppable);
	setTimeout(pollStudio, busy ? 700 : 2500);
}

// ------------------------------------------------------------------ recording + replay
async function record() {
	const frames = {};
	await Promise.all((studio?.cameras ?? []).map(async camera => {
		try {
			const r = await fetch(`/api/studio/frame/${encodeURIComponent(camera.id)}.jpg?rec=${Date.now()}`, {cache: 'no-store'});
			if (r.status === 200) frames[camera.id] = URL.createObjectURL(await r.blob());
		} catch { /* a missing frame stays missing in the recording */ }
	}));
	const dropped = recorder.entries[0];
	recorder.add(Date.now(), {studio: structuredClone(studio), decision: state && structuredClone(state)}, frames);
	if (dropped && recorder.entries[0] !== dropped) Object.values(dropped.frames).forEach(u => URL.revokeObjectURL(u));
	$('rec-status').innerHTML = `<i></i>Recording ${ageText(recorder.duration())}`;
	$('replay-play').disabled = false;
}
$('rec-toggle').addEventListener('click', () => {
	if (source !== 'live' && !recording) { reply('refuse', 'Recording needs Live', 'Switch to Live first.'); return; }
	recording = !recording;
	if (recording) {
		let busy = false;
		recordTimer = setInterval(async () => { if (busy || source !== 'live') return; busy = true; try { await record(); } finally { busy = false; } }, 250);
	} else clearInterval(recordTimer);
	$('rec-status').className = `rec ${recording ? 'on' : ''}`;
	$('rec-toggle').textContent = recording ? 'Stop' : 'Record';
	if (!recording) $('rec-status').innerHTML = `<i></i>${recorder.entries.length ? 'Saved ' + ageText(recorder.duration()) : 'Not recording'}`;
});
$('replay-play').addEventListener('click', () => setSource('replay'));
function startReplay() {
	stopReplay();
	const seek = $('replay-seek');
	seek.disabled = false; seek.max = String(recorder.duration());
	replayStart = performance.now() - Number(seek.value || 0);
	replayTimer = setInterval(() => {
		let offset = performance.now() - replayStart;
		if (offset > recorder.duration()) { replayStart = performance.now(); offset = 0; }
		seek.value = String(offset);
		showReplay(recorder.at(offset));
	}, 150);
}
function stopReplay() { clearInterval(replayTimer); replayTimer = null; $('replay-seek').disabled = source !== 'replay'; }
$('replay-seek').addEventListener('input', e => { replayStart = performance.now() - Number(e.target.value); });
function showReplay(entry) {
	if (!entry) return;
	const v = studioView(entry.state.studio, entry.time);
	renderCameras(v, {replayFrames: entry.frames});
	if (entry.state.decision) { state = {...entry.state.decision, mode: 'replay', timestamp: Date.now()}; render(); }
}

// ------------------------------------------------------------------ command console
function reply(kind, title, text) {
	const out = $('command-out');
	const el = document.createElement('div');
	el.className = `reply ${kind}`;
	el.innerHTML = '<b></b><span></span>';
	el.querySelector('b').textContent = title; el.querySelector('span').textContent = text;
	out.replaceChildren(el);
}
let planSteps = [];
function showPlan(parsed) {
	planSteps = parsed.plan.map(step => ({...step, status: ''}));
	drawPlan();
}
function drawPlan() {
	$('plan').replaceChildren(...planSteps.map(step => {
		const li = document.createElement('li');
		li.className = step.status;
		li.innerHTML = '<span></span><em></em>';
		li.querySelector('span').textContent = step.text; li.querySelector('em').textContent = step.time ?? '';
		return li;
	}));
}
const STAGE_TO_STEP = {perceive: 'capture', detect: 'score', reason: 'decide', review: 'decide', act: 'act', verify: 'act', complete: 'act'};
function planProgress(stage) {
	const key = STAGE_TO_STEP[stage]; if (!key) return;
	let reached = false;
	planSteps.forEach(step => {
		if (step.key === key) { step.status = stage === 'review' ? 'held' : 'active'; reached = true; }
		else if (!reached && step.status !== 'held') step.status = 'done';
	});
	drawPlan();
}
function planDone() {
	planSteps.forEach(step => { if (step.status === 'active') step.status = state?.stage === 'review' ? 'held' : 'done'; });
	drawPlan();
}

async function post(path, body) {
	const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-Armigo-Request': '1'}, body: JSON.stringify(body)});
	let data = null; try { data = await response.json(); } catch { /* empty body */ }
	return {status: response.status, data};
}

async function execute(parsed) {
	showPlan(parsed);
	if (!parsed.action) { reply('refuse', 'Not understood', parsed.reason); return; }
	// STOP is handled before any view or health check: it must work from Demo, Replay and with Studio unreachable.
	if (parsed.action === 'STOP') { await stopEverything(); return; }
	const info = ACTIONS[parsed.action];
	if (source === 'replay') { reply('refuse', 'Replay is read-only', 'Switch to Live or Demo.'); return; }
	if (source === 'demo') {
		reply('ok', info.title, 'Running in the demo.');
		if (parsed.action === 'INSPECT') runDemo(pickScenario(), {stopAt: 'reason'});
		else if (parsed.action === 'INSPECT_AND_SORT') runDemo(pickScenario());
		else runDemo(parsed.action === 'SORT_GREEN' ? 'normal' : 'defective');
		return;
	}
	// Live: sorting runs the hybrid cycle when the dashboard has one; inspecting alone stays a Studio inspection.
	const request = cycleRequest(parsed.action);
	if (request && cell?.configured) { await startCycle(request); return; }
	if (!studio?.reachable) { reply('error', 'Studio not connected', studioView(studio).headline); return; }
	const cameraId = $('run-camera').value;
	if (parsed.action === 'INSPECT' || (parsed.action === 'INSPECT_AND_SORT' && !studio.control_enabled)) {
		if (!studio.inspector) { reply('error', 'No inspector', 'Start the dashboard with --anomaly-model or --purity.'); return; }
		planProgress('perceive');
		const t0 = performance.now();
		const r = await post('/api/studio/inspect', {camera_id: cameraId});
		if (r.status !== 200) { reply('error', 'Inspection failed', r.data?.error ?? `HTTP ${r.status}`); planSteps.forEach(s => { if (s.status === 'active') s.status = 'failed'; }); drawPlan(); return; }
		showInspection(r.data, performance.now() - t0);
		if (parsed.action === 'INSPECT_AND_SORT') reply('refuse', `Scored: ${r.data.label}`, 'The arm is locked, so nothing moved.');
		return;
	}
	if (!studio.control_enabled) { reply('refuse', 'Arm locked', 'Start the dashboard with --studio-control to allow runs.'); return; }
	if (!$('operator-present').checked) { reply('refuse', 'Confirm someone is at the robot', 'Tick the box first.'); return; }
	const model = studio.models.find(m => m.id === $('run-model').value);
	const body = {action: parsed.action, camera_id: cameraId, environment_id: $('run-environment').value, model_id: model?.id, backend: model?.backends[0], device: $('run-device').value};
	planProgress(parsed.action === 'INSPECT_AND_SORT' ? 'perceive' : 'act');
	const r = await post('/api/studio/run', body);
	if (r.status !== 202) { reply('error', 'Run refused', r.data?.error ?? `HTTP ${r.status}`); return; }
	stopRequested = false;
	if (r.data.decision === 'pending') reply('ok', 'Inspecting in the session', 'The arm moves only if the fresh result is pass or reject.');
	else { reply('ok', `Sorting to the ${r.data.decision} plate`, `Stops by itself after ${studio.max_run_s} s.`); planProgress('act'); }
}

async function stopEverything() {
	const plan = stopPlan({linked: studioLinked || cellLinked, demoRunning: Boolean(timer)});
	if (plan.demo) pause();
	planSteps.forEach(s => { if (s.status === 'active') s.status = 'held'; }); drawPlan();
	if (!plan.backend) { reply('ok', 'Stopped', 'Demo paused.'); return; }
	stopRequested = true;
	renderRun();
	try {
		const r = await post('/api/stop', {});
		if (r.status !== 200) throw new Error(r.data?.error ?? `HTTP ${r.status}`);
		if (r.data?.stopping) reply('ok', 'Stop requested', 'Waiting for Studio to confirm the arm is held.');
		else { stopRequested = false; reply('ok', 'Nothing was running', 'No run to stop.'); }
	} catch (error) {
		reply('error', 'Stop not delivered', `${error.message}. Use Studio’s stop or the robot’s power switch.`);
	}
	renderRun();
}

function showInspection(result, roundTripMs) {
	liveSeq++;
	state = inspectionSnapshot(result, liveSeq);
	planProgress('perceive'); planProgress('detect'); planProgress(state.stage === 'review' ? 'review' : 'reason');
	const step = planSteps.find(s => s.key === 'score');
	if (step && result.timings_ms?.inference) { step.time = `${result.timings_ms.inference.toFixed(1)} ms`; }
	const cap = planSteps.find(s => s.key === 'capture'); if (cap) cap.time = `${Math.round(roundTripMs)} ms`;
	drawPlan();
	$('crop-figure').hidden = false;
	$('crop-image').src = `/api/studio/inspection/crop.jpg?n=${liveSeq}`;
	lastInspectionAt = result.timestamp;
	const model = liveBrickModel(result);
	brickViews.show({label: model.label, colour: BRICK_COLOURS[0], defect: model.defect});
	$('brick-source').textContent = 'Illustrative';
	$('brick-note').textContent = model.note;
	$('brick-canvas').setAttribute('aria-label', 'Illustrative brick model. The live inspection does not locate defects; the crop shows what was scored.');
	render();
	reply(result.label === 'uncertain' ? 'refuse' : 'ok', `${{normal: 'Pass', defective: 'Reject', uncertain: 'Review'}[result.label]}, score ${Number.isFinite(result.score) ? result.score.toFixed(2) : '—'}`,
		result.reason ?? `${result.timings_ms?.inference?.toFixed(1) ?? '—'} ms on ${result.device ?? 'unverified device'}`);
}

function renderRunConfig() {
	const show = source === 'live' && studio?.reachable;
	$('run-config').hidden = !show;
	if (!show) return;
	const fill = (select, items, label) => {
		const keep = select.value;
		const key = items.map(i => i.id).join();
		if (select.dataset.key !== key) {
			select.replaceChildren(...items.map(i => Object.assign(document.createElement('option'), {value: i.id, textContent: label(i)})));
			select.dataset.key = key;
			if (items.some(i => i.id === keep)) select.value = keep;
		}
	};
	fill($('run-environment'), studio.environments, e => e.name);
	fill($('run-model'), studio.models, m => `${m.name} (${m.backends.join(', ') || 'no export'})`);
	fill($('run-camera'), studio.cameras, c => c.name);
	$('operator-present').disabled = !studio.control_enabled;
	// With the cell's cycle configured, sorting goes there: only the inspection camera matters here.
	const cycle = Boolean(cell?.configured);
	document.querySelectorAll('[data-studio-run]').forEach(el => { el.hidden = cycle; });
	$('cycle-route').hidden = !cycle;
	if (!$('run-camera').dataset.picked) {
		const front = studio.cameras.find(c => /front/i.test(c.name));
		if (front) $('run-camera').value = front.id;
	}
}
$('run-camera').addEventListener('change', () => { $('run-camera').dataset.picked = '1'; });

/** The run bar shows in every view while a run may exist, so STOP is always one click away. */
function renderRun() {
	const cycle = cell?.cycle;
	if (cycle && (cycle.active || (stopRequested && !studio?.run))) {
		const view = cycleView(cell);
		$('run-bar').hidden = false;
		const done = view.steps.filter(s => ['done', 'skipped'].includes(s.status)).length;
		let text = `Sort cycle · ${view.headline} · ${Math.round(cycle.seconds)} s`;
		if (stopRequested && cycle.active) text = `Stop requested · waiting for the cycle to hold the arm. ${text}`;
		if (stopRequested && !cycle.active) { stopRequested = false; text = `Stopped · ${cycle.end?.reason ?? 'the arm holds still'}`; }
		$('run-text').textContent = text;
		$('run-progress').style.width = `${Math.round(100 * done / view.steps.length)}%`;
		$('stop-run').disabled = !cycle.active;
		return;
	}
	const run = studioView(studio).run;
	const stop = stopStatus(studio?.run ?? null, stopRequested);
	$('run-bar').hidden = !run && stop !== 'requested';
	if ($('run-bar').hidden) return;
	let text = run ? `${run.text}${run.stoppable ? ` · ${run.observations ?? 0} observations` : ''}` : 'Run state unknown';
	if (stop === 'requested') text = `Stop requested · waiting for Studio to confirm. ${text}`;
	if (stop === 'confirmed') { stopRequested = false; text = `Stopped · the arm holds still (${run.reason ?? run.phase})`; }
	$('run-text').textContent = text;
	$('run-progress').style.width = `${((run?.progress ?? 0) * 100).toFixed(0)}%`;
	$('stop-run').disabled = !(run?.stoppable) && stop !== 'requested';
}
$('stop-run').addEventListener('click', () => stopEverything());

$('command-form').addEventListener('submit', e => { e.preventDefault(); execute(parseCommand($('command-input').value)); });
$('command-chips').addEventListener('click', e => {
	const prompt = e.target.closest('[data-prompt]')?.dataset.prompt; if (!prompt) return;
	$('command-input').value = prompt; execute(parseCommand(prompt));
});

// ------------------------------------------------------------------ guided tour
const TOUR = [
	{view: 'home', title: 'One cell, three outcomes', scenario: null,
		text: 'Each part is checked the same way and goes to one of three places.',
		metric: ['Outcomes per part', '3'],
		notes: [{anchor: 'spot', title: 'New part'}, {anchor: 'green', title: 'Pass'}, {anchor: 'pink', title: 'Reject', tone: 'red'}, {anchor: 'review', title: 'Review', tone: 'amber'}]},
	{view: 'camera', title: 'See the part', scenario: 'defective', stage: 'perceive',
		text: 'A depth camera above the table finds the brick and both bowls in millimetres. After the pick, the front camera sees the brick from every side.',
		notes: [{anchor: 'camera', title: 'Camera'}, {anchor: 'spot', title: 'Brick'}]},
	{view: 'laptop', title: 'Score it on the NPU', scenario: 'defective', stage: 'detect',
		text: 'Anomalib learned what good bricks look like and flags anything unusual. It runs on the laptop’s NPU.',
		metric: ['Inference time', '8.5 ms'],
		notes: [{anchor: 'laptop', title: 'Intel laptop', text: 'NPU'}]},
	{view: 'bins', title: 'Clear defect', scenario: 'defective', stage: 'reason',
		text: 'A high score means a defect. The part goes to the pink plate.',
		metric: ['Defect score', '0.90'],
		notes: [{anchor: 'pink', title: 'Reject', text: '0.90', tone: 'red'}]},
	{view: 'brick', title: 'Not sure? Ask', scenario: 'uncertain', stage: 'review',
		text: 'In the middle band the arm stays still and a person decides.',
		metric: ['Defect score', '0.51'],
		notes: [{anchor: 'review', title: 'Review', text: '0.51', tone: 'amber'}]},
	{view: 'arm', title: 'Sort it', scenario: 'normal', stage: 'act',
		text: 'A checked, scripted path brings the gripper over the brick, a learned policy grasps it, and the clear result picks the plate. A depth check then confirms the brick landed.',
		metric: ['Defect score', '0.21'],
		notes: [{anchor: 'arm', title: 'SO-101'}, {anchor: 'green', title: 'Pass', text: '0.21'}]},
	{view: 'laptop', title: 'All on one laptop', scenario: null,
		text: 'Everything runs locally. Edge performance below shows the live load.',
		metric: ['Cloud calls', '0'],
		notes: [{anchor: 'laptop', title: 'Intel laptop'}], scroll: 'resource-title'},
];
function stateAt(scenario, stage) {
	let s = createDemo(scenario);
	for (let i = 0; i < 6 && s.stage !== stage; i++) s = advanceDemo(s);
	return s;
}
function showTour(i) {
	tourIndex = Math.max(0, Math.min(TOUR.length - 1, i));
	const step = TOUR[tourIndex];
	$('tour-card').hidden = false;
	$('scene').parentElement.classList.add('touring');
	$('tour-step').textContent = `Step ${tourIndex + 1} of ${TOUR.length}`;
	$('tour-title').textContent = step.title; $('tour-text').textContent = step.text;
	$('tour-metric').hidden = !step.metric;
	if (step.metric) { $('tour-metric-label').textContent = step.metric[0]; $('tour-metric-value').textContent = step.metric[1]; }
	$('tour-dots').replaceChildren(...TOUR.map((_, k) => Object.assign(document.createElement('i'), {className: k === tourIndex ? 'on' : ''})));
	$('tour-prev').disabled = tourIndex === 0;
	$('tour-next').textContent = tourIndex === TOUR.length - 1 ? 'Finish' : 'Next';
	scene3d.focus(step.view);
	scene3d.annotate(step.notes);
	if (source === 'demo' && step.scenario) {
		pause();
		const target = stateAt(step.scenario, step.stage);
		if (state?.episode_id !== target.episode_id) part++;
		// Walk through the stages so the 3D cell animates them in order.
		let s = createDemo(step.scenario);
		state = s; render();
		const walk = () => { if (s.stage === step.stage) return; s = advanceDemo(s); state = s; render(); setTimeout(walk, 450); };
		setTimeout(walk, 450);
	}
	if (step.scroll) $(step.scroll).scrollIntoView({behavior: 'smooth', block: 'center'});
}
function endTour() { tourIndex = -1; $('tour-card').hidden = true; $('scene').parentElement.classList.remove('touring'); scene3d.annotate([]); scene3d.reset(); }
$('start-tour').addEventListener('click', () => { if (source === 'replay') setSource('demo'); $('scene').scrollIntoView({behavior: 'smooth', block: 'center'}); showTour(0); });
$('tour-next').addEventListener('click', () => tourIndex === TOUR.length - 1 ? endTour() : showTour(tourIndex + 1));
$('tour-prev').addEventListener('click', () => showTour(tourIndex - 1));
$('tour-close').addEventListener('click', endTour);
document.addEventListener('keydown', e => {
	if (tourIndex < 0 || $('intro-dialog').open || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
	if (e.key === 'ArrowRight') $('tour-next').click();
	if (e.key === 'ArrowLeft' && tourIndex > 0) $('tour-prev').click();
	if (e.key === 'Escape') endTour();
});
$('intro-enter').addEventListener('click', () => { $('start-tour').click(); });

// ------------------------------------------------------------------ the real cell: table from depth and the hybrid cycle
const tableLoader = new LatestImageLoader($('table-image'), () => { $('table-waiting').hidden = false; });
const SVG = 'http://www.w3.org/2000/svg';
function svg(tag, attrs, text) {
	const el = document.createElementNS(SVG, tag);
	for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
	if (text !== undefined) el.textContent = text;
	return el;
}
function drawMap(reading, target) {
	const layout = mapLayout(reading);
	const [x0, y0, w, h] = layout.viewBox;
	const map = $('table-map');
	map.setAttribute('viewBox', layout.viewBox.join(' '));
	map.setAttribute('preserveAspectRatio', 'xMidYMid meet');
	const fs = Math.max(w, h) / 26, items = [];
	for (let x = Math.ceil(x0 / 50) * 50; x <= x0 + w; x += 50) items.push(svg('line', {x1: x, y1: y0, x2: x, y2: y0 + h, class: x === 0 ? 'axis' : 'grid', 'stroke-width': fs / 10}));
	for (let y = Math.ceil(y0 / 50) * 50; y <= y0 + h; y += 50) items.push(svg('line', {x1: x0, y1: y, x2: x0 + w, y2: y, class: y === 0 ? 'axis' : 'grid', 'stroke-width': fs / 10}));
	if (layout.base) {
		items.push(svg('circle', {cx: layout.base.x, cy: layout.base.y, r: 45, class: 'base', 'stroke-width': fs / 6}));
		items.push(svg('text', {x: layout.base.x, y: layout.base.y + fs / 3, 'text-anchor': 'middle', 'font-size': fs}, 'Robot'));
	}
	for (const b of layout.bowls) {
		items.push(svg('circle', {cx: b.x, cy: b.y, r: b.r, class: `bowl-${b.colour}`, 'stroke-width': fs / 5}));
		items.push(svg('text', {x: b.x, y: b.y, 'text-anchor': 'middle', 'font-size': fs}, b.colour));
		items.push(svg('text', {x: b.x, y: b.y + fs * 1.2, 'text-anchor': 'middle', 'font-size': fs * .8}, b.label));
		if (Number.isFinite(b.inside)) items.push(svg('text', {x: b.x, y: b.y - fs * 1.2, 'text-anchor': 'middle', 'font-size': fs * .8}, `${b.inside} inside`));
	}
	for (const b of layout.bricks) {
		items.push(svg('rect', {x: b.x - b.w / 2, y: b.y - b.h / 2, width: b.w, height: b.h, rx: 2, class: 'brick', 'stroke-width': fs / 8, transform: `rotate(${b.rotate} ${b.x} ${b.y})`}));
		items.push(svg('text', {x: b.x, y: b.y - b.h / 2 - fs / 2, 'text-anchor': 'middle', 'font-size': fs * .8}, b.label));
	}
	if (target) items.push(svg('circle', {cx: target[0], cy: -target[1], r: 26, class: 'target', 'stroke-width': fs / 6}));
	items.push(svg('rect', {x: -10, y: -10, width: 20, height: 20, class: 'tag', 'stroke-width': fs / 8}));
	items.push(svg('text', {x: 14, y: fs * 1.2, 'font-size': fs * .8}, 'tag 16'));
	map.replaceChildren(...items);
}

const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
function renderCell() {
	$('cell-panel').hidden = !(source === 'live' && cell);
	if ($('cell-panel').hidden) return;
	const cycle = cell.cycle;
	const view = cycleView(cell, {token: cycle?.id ?? ''});
	const table = cell.table;
	const reading = table?.reading;
	const tableOk = table?.status === 'live' && table.age_ms !== null && table.age_ms < 5000;
	setBadge('table-badge', !table ? '' : tableOk ? (reading?.table ? 'ok' : 'warn') : table.status === 'error' ? 'bad' : '',
		!table ? 'No depth bridge (--bridge)' : tableOk ? (reading?.table ? `Top camera · ${plural(reading.bowls.length, "bowl")}, ${plural(reading.bricks.length, "brick")} · ${Math.round(reading.measure_ms)} ms` : 'Top camera · no table frame')
			: table.status === 'error' ? `Depth bridge: ${table.error}` : 'Top camera: waiting');
	const tone = {running: 'live', review: 'warn', done: 'ok', planned: 'ok', stopped: 'warn', failed: 'bad', held: 'warn'}[view.status] ?? '';
	setBadge('cycle-badge', tone === 'live' ? '' : tone, cycle ? `${cycle.go ? 'Cycle' : 'Plan check'} · ${view.status}${cycle.active ? ` · ${Math.round(cycle.seconds)} s` : ''}` : 'No cycle yet', tone === 'live');
	const headline = $('cycle-headline');
	headline.textContent = view.headline;
	headline.className = `cycle-headline ${view.status === 'review' || view.status === 'held' ? 'review' : ['failed', 'stopped'].includes(view.status) ? 'fault' : view.status === 'done' ? 'done' : ''}`;
	$('cycle-steps').replaceChildren(...view.steps.map(s => {
		const li = document.createElement('li');
		li.className = s.status;
		li.innerHTML = '<b><span></span><em></em></b><small></small>';
		li.querySelector('span').textContent = s.title;
		li.querySelector('em').textContent = Number.isFinite(s.seconds) ? `${s.seconds.toFixed(1)} s` : '';
		li.querySelector('small').textContent = s.detail || s.sub;
		li.title = `${s.title}: ${s.detail || s.sub}`;
		return li;
	}));
	$('cycle-review').hidden = !view.review;
	const tiles = view.views.map(v => {
		const el = document.createElement('article');
		el.className = `view-tile ${v.tone}`;
		el.innerHTML = '<div class="shot"></div><div class="meta"><span></span><strong></strong></div>';
		const shot = el.querySelector('.shot');
		if (v.crop) shot.append(Object.assign(document.createElement('img'), {src: v.crop, alt: `Crop scored for the ${v.name} view`}));
		else shot.textContent = v.reason ?? 'not scored';
		el.querySelector('span').textContent = v.name.replace('_', ' ');
		el.querySelector('strong').textContent = v.scoreText;
		const cams = Object.entries(v.cameras ?? {}).map(([cam, c]) => `${cam} ${Number.isFinite(c.score) ? c.score.toFixed(1) : '—'} / ${Number.isFinite(c.threshold) ? c.threshold.toFixed(1) : '—'} ${c.verdict}`);
		el.title = [`${v.label} · score ${v.scoreText}`, ...cams, v.reason].filter(Boolean).join('\n');
		return el;
	});
	const viewsEl = $('cycle-views');
	if (viewsEl.dataset.key !== `${cycle?.id}:${view.views.length}`) { viewsEl.replaceChildren(...tiles); viewsEl.dataset.key = `${cycle?.id}:${view.views.length}`; }
	$('cycle-log').replaceChildren(...view.log.slice(-40).map(line => {
		const li = document.createElement('li');
		li.innerHTML = '<span></span>';
		li.querySelector('span').textContent = `${line.t_s.toFixed(1)} s`;
		li.append(line.text);
		return li;
	}));
	$('cycle-plan').disabled = !view.canPlan;
	$('cycle-go').disabled = !view.canGo;
	$('cycle-stop').hidden = !view.canStop;
	$('cell-operator').disabled = !view.canGo && !view.canStop;
	$('cycle-lock').textContent = view.lockText || (cell.inspector ? '' : 'No inspector: start the dashboard with --anomaly-model or --purity, or every brick waits for you to choose.');
	$('table-note').textContent = reading?.table ? `Table frame, mm (${reading.table})` : reading?.reason ? `No table frame: ${reading.reason}` : 'Table frame, mm (tag 16 at the origin)';
	drawMap(reading?.table ? reading : null, cycle?.active ? cycle.brick?.centre_mm : null);
}

let reportedCycle = null;
function showCycle() {
	const cycle = cell?.cycle;
	if (source !== 'live' || !cycle) return;
	if (!cycle.active && cycle.end && reportedCycle !== cycle.id && !(cycle.released_bowl && cell.table && !cycle.verify && cycle.end.ok)) {
		reportedCycle = cycle.id;
		const view = cycleView(cell);
		reply({done: 'ok', planned: 'ok', failed: 'error'}[view.status] ?? 'refuse', view.status === 'planned' ? 'Plan checked' : `Cycle ${view.status}`, view.headline);
		planSteps.forEach(step => { if (step.status !== 'done') step.status = ['done', 'planned'].includes(view.status) ? 'done' : view.status === 'failed' ? 'failed' : 'held'; });
		drawPlan();
	}
	const key = JSON.stringify([cycle.id, cycle.phase, cycle.steps.length, cycle.views.length, cycle.decision, cycle.verify, cycle.awaiting_review]);
	if (key === lastCycleKey) return;
	lastCycleKey = key;
	const ins = cell.inspector;
	const t = ins?.thresholds;
	const thresholds = t && Number.isFinite(t.normal_below) && Number.isFinite(t.defective_above) && t.normal_below <= t.defective_above
		? {normal_below: Math.max(0, Math.min(1, t.normal_below)), defective_above: Math.max(0, Math.min(1, t.defective_above))} : null;
	const snapshot = cycleSnapshot(cycle, Math.floor((cycle.id ?? 0) / 1000) % 1e9, {device: ins?.device ?? null, thresholds});
	if (!snapshot) return;
	snapshot.episode_id = `Cycle ${new Date(cycle.id).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})}`;
	pause();
	state = snapshot;
	if (cycle.active) planProgress(snapshot.stage);
	$('crop-figure').hidden = !cycle.views.some(v => v.crop);
	const last = cycle.views.map((v, i) => [v, i]).filter(([v]) => v.crop).at(-1);
	if (last) $('crop-image').src = `/api/cell/view/${last[1]}.jpg?c=${cycle.id}`;
	render();
}

async function pollCell() {
	try {
		const response = await fetch('/api/cell/state', {cache: 'no-store', signal: AbortSignal.timeout(4000)});
		cell = response.status === 204 ? null : await response.json();
		if (cell) cellLinked = true;
	} catch { /* keep the last state; the run bar keeps STOP available */ }
	renderCell();
	showCycle();
	renderRun();
	const fast = source === 'live' && (cell?.cycle?.active || stopRequested);
	setTimeout(pollCell, fast ? 500 : 1500);
}

let tableTick = 0;
function pumpTable() {
	if (source === 'live' && cell?.table && !document.hidden) {
		tableTick++;
		tableLoader.setSource(`/api/cell/table.jpg?n=${tableTick}`);
		$('table-waiting').hidden = Boolean(tableLoader.displayed);
	}
	setTimeout(pumpTable, 1000);
}

async function startCycle(request) {
	if (request.go && !cell?.control_enabled) { reply('refuse', 'Arm locked', 'Start the dashboard with --cell-control to run the sort cycle. “Check plan” works without it.'); return; }
	if (request.go && !$('cell-operator').checked) { reply('refuse', 'Confirm someone is at the robot', 'Tick “Someone is at the robot” in the cell panel first.'); $('cell-operator').focus(); return; }
	const r = await post('/api/cell/cycle', request);
	if (r.status !== 202) { reply('error', request.go ? 'Cycle refused' : 'Plan check refused', r.data?.error ?? `HTTP ${r.status}`); return; }
	stopRequested = false;
	lastCycleKey = null;
	reply('ok', request.go ? (request.bowl ? `Sorting to the ${request.bowl} bowl` : 'Sort cycle started') : 'Checking the plan',
		request.go ? (request.bowl ? 'The views are still inspected and shown; the bowl was named in the command.' : 'Measure, pick, show it to the camera from every side, then the result picks the bowl.') : 'Measuring the table and planning the moves. The arm does not move.');
	cell = {...cell, cycle: {active: true, go: request.go, phase: 'starting', seconds: 0, steps: [], log: [], views: [], decision: null, awaiting_review: false, verify: null, end: null}};
	renderCell(); renderRun();
}
$('cycle-plan').addEventListener('click', () => startCycle({go: false, bowl: null}));
$('cycle-go').addEventListener('click', () => startCycle({go: true, bowl: null}));
$('cycle-stop').addEventListener('click', () => stopEverything());
$('cycle-review').addEventListener('click', async e => {
	const choice = e.target.closest('[data-review]')?.dataset.review; if (!choice) return;
	const r = await post('/api/cell/review', {bowl: choice === 'hold' ? null : choice});
	if (r.status !== 200) reply('error', 'Choice not taken', r.data?.error ?? `HTTP ${r.status}`);
	else reply('ok', choice === 'hold' ? 'Holding the brick' : `Sending it to the ${choice} bowl`, 'Chosen by you.');
});

// ------------------------------------------------------------------ start
render();
updateBadges();
mountIntro();
mountPerformance();
pollStudio();
pollCell();
pumpTable();
// The operator's screen at the cell opens straight in Live: http://<host>:8080/#live
if (location.hash === '#live') setSource('live');
