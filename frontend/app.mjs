import { createDemo, advanceDemo, displayState, validateTelemetry, stageProgress, explanation } from './telemetry.mjs';
import { Cell3D } from './cell3d.mjs';
import { BrickViews, BRICK_COLOURS, demoDefect } from './brickviews.mjs';
import { LatestImageLoader } from './image-loader.mjs';
import { InferenceWindow, mountPerformance } from './performance.mjs';
import { mountIntro } from './intro.mjs';
import { parseCommand, ACTIONS } from './command.mjs';
import { studioView, inspectionSnapshot, SessionRecorder, ageText } from './studio.mjs';

const $ = id => document.getElementById(id);
const cell = new Cell3D($('scene'), $('annotations'));
const brickViews = new BrickViews($('brick-canvas'));
const inferenceWindow = new InferenceWindow();
const recorder = new SessionRecorder({maxSeconds: 90});

let source = 'demo';          // demo | live | replay
let state = null;             // current v1 snapshot shown in the panels (null = idle)
let part = 0;
let timer = null;             // demo stepper
let studio = null;            // last /api/studio/state
let liveSeq = 0;
let tourIndex = -1;
let recording = false, recordTimer = null, replayTimer = null, replayStart = 0;

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

const toneOf = s => !s ? 'idle' : s.stage === 'fault' ? 'fault' : s.label;
const fmtMs = v => v === null || v === undefined ? '—' : v >= 1000 ? `${(v / 1000).toFixed(1)}s` : `${v.toFixed(1)}ms`;

function render() {
	const s = state;
	const panel = $('decision-panel');
	panel.className = `panel decision-panel ${toneOf(s)}`;
	if (!s) {
		$('decision-title').textContent = 'Ready_';
		$('destination').textContent = 'No part loaded';
		$('destination-dot').className = 'led';
		$('explanation').textContent = 'Press “Inspect next part”, type a command below, or take the guided tour.';
		$('decision-score').textContent = '—'; $('task').textContent = '—'; $('outcome').textContent = 'Not yet verified';
		$('score-value').textContent = '0.00'; $('score-value').className = 'big'; meterTarget = 0; meterZones({normal_below: .4, defective_above: .6});
		$('threshold-copy').textContent = 'Thresholds come from the active inspector.';
		document.querySelectorAll('[data-stage]').forEach(el => el.classList.remove('active', 'passed'));
		$('progress-text').textContent = 'Ready to inspect';
		renderButtons(); return;
	}
	const view = displayState(s);
	const demo = s.mode === 'demo', fault = s.stage === 'fault';
	const decided = ['reason', 'act', 'verify', 'complete', 'review', 'fault'].includes(s.stage);
	$('decision-title').textContent = decided ? (fault ? 'Stopped' : {normal: 'Pass', defective: 'Reject', uncertain: 'Review'}[s.label]) : s.stage === 'detect' ? 'Scoring_' : 'Scan_';
	$('destination').textContent = !decided ? 'Deciding' : fault ? 'Operator check required' : view.destination;
	$('destination-dot').className = `led ${decided ? (s.destination === 'green' ? 'green' : s.destination === 'pink' ? 'red' : 'amber') : ''}`;
	$('episode-tag').textContent = demo ? `PART ${String(part).padStart(3, '0')}` : s.episode_id.toUpperCase();
	$('explanation').textContent = decided ? explanation(s) : s.stage === 'detect' ? 'The anomaly model is scoring the brick crop.' : 'Capturing the part under the top camera.';
	const showScore = decided || s.stage === 'detect';
	$('decision-score').textContent = showScore ? view.score : '—';
	$('task').textContent = decided && s.task && !fault ? `${demo ? 'Demo: ' : ''}“${s.task}”` : decided ? 'No movement requested' : '—';
	$('outcome').textContent = s.stage === 'complete' && s.outcome ? `${demo ? 'Demo: ' : ''}${s.outcome} bowl · verified` : 'Not yet verified';
	meterZones(s.thresholds);
	meterTarget = showScore && Number.isFinite(s.score) ? s.score : 0;
	const big = $('score-value');
	big.textContent = showScore ? view.score.replace('—', '-.--') : '0.00';
	big.className = `big ${showScore && Number.isFinite(s.score) ? 'on' : ''}`;
	big.style.color = !showScore || !Number.isFinite(s.score) ? '' : s.label === 'defective' ? 'var(--red)' : s.label === 'uncertain' ? 'var(--amber)' : 'var(--g)';
	$('threshold-copy').textContent = s.thresholds ? `${demo ? 'Demo thresholds: ' : 'Inspector thresholds: '}pass below ${s.thresholds.normal_below.toFixed(2)}, reject above ${s.thresholds.defective_above.toFixed(2)}, a person decides in between.` : 'Thresholds unavailable.';
	const stages = stageProgress(s);
	document.querySelectorAll('[data-stage]').forEach((el, i) => { el.classList.toggle('active', stages[i].active); el.classList.toggle('passed', stages[i].passed); });
	$('reason-stage').textContent = decided ? (s.destination ? view.destination : 'Human review') : 'Decision';
	$('act-stage').textContent = view.actStatus; $('verify-stage').textContent = view.verifyStatus;
	const status = {perceive: 'Capturing the part', detect: 'Inspecting for defects', reason: 'Selecting the destination', act: 'Placing the part', verify: 'Checking placement', complete: 'Cycle complete', review: 'Waiting for human review', fault: 'Stopped · no automatic retry'};
	$('progress-text').textContent = `${demo ? 'Demo · ' : s.mode === 'replay' ? 'Replay · ' : 'Live · '}${status[s.stage]}`;
	inferenceWindow.add(s);
	const summary = inferenceWindow.summary();
	$('inference-median').textContent = fmtMs(summary.median); $('inference-p95').textContent = fmtMs(summary.p95);
	$('inference-samples').textContent = summary.count ? `${summary.count} measured ${summary.mode} cycles on ${summary.device ?? 'an unverified device'} · nearest-rank percentiles` : demo ? 'Demo parts carry no timings: only measured runs fill these numbers.' : 'No measured cycles yet.';
	$('inference-device').textContent = (s.device ?? 'unverified').toUpperCase();
	for (const row of document.querySelectorAll('[data-timing]')) {
		const v = s.timings_ms[row.dataset.timing];
		row.querySelector('strong').textContent = fmtMs(v);
		row.querySelector('.bar i').style.width = v === null ? '0' : `${Math.min(100, Math.max(3, Math.log10(1 + v) / 4.3 * 100))}%`;
	}
	if (demo) {
		const seed = part * 7 + 1;
		brickViews.show({label: decided ? s.label : 'none', colour: BRICK_COLOURS[part % BRICK_COLOURS.length], defect: decided || s.stage === 'detect' ? demoDefect(s.label, seed) : null});
		cell.setState(s, {brickColor: BRICK_COLOURS[part % BRICK_COLOURS.length], defect: s.label === 'normal' ? null : (demoDefect(s.label, seed)?.kind ?? null)});
	} else {
		cell.setState(s);
	}
	updatePitch(summary);
	renderButtons();
}

function renderButtons() {
	const busy = Boolean(timer);
	const live = source === 'live';
	$('inspect').disabled = source === 'replay' || busy || (live && !studio?.inspector);
	$('inspect').firstChild.textContent = live ? '> Inspect live part ' : busy ? '> Inspecting… ' : '> Inspect next part ';
	$('play').disabled = source !== 'demo';
	$('scenario').disabled = source !== 'demo';
	$('play').textContent = busy ? 'Pause demo' : 'Play demo';
}

function updatePitch(summary) {
	if (summary.count && summary.mode === 'real') {
		$('fact-npu').textContent = `${summary.median.toFixed(1)} ms`;
		$('fact-npu').previousElementSibling.textContent = `Live median · ${summary.device ?? 'device'}`;
		$('fact-npu-note').textContent = `measured on this laptop over ${summary.count} inspections`;
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
$('reset-view').addEventListener('click', () => cell.reset());
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
	const el = $(id); el.className = `badge ${tone}`;
	el.querySelector('i').className = blink ? 'blink' : '';
	el.querySelector('span').textContent = text;
}
function setSource(next) {
	if (next === 'replay' && !recorder.entries.length) { reply('refuse', 'Nothing recorded yet', 'Switch to Live and press Record first. Replay plays back the last 90 seconds you recorded.'); return; }
	source = next;
	document.querySelectorAll('[data-source]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.source === source)));
	stopReplay();
	if (source === 'demo') { $('brick-source').textContent = 'ILLUSTRATIVE'; $('brick-note').textContent = 'Defect marked where it sits on the part. Demo parts are illustrative.'; }
	if (source === 'live') { pause(); $('brick-source').textContent = 'LIVE INSPECTION'; $('brick-note').textContent = 'The crop is what the model scored. The 3D views show where a defect would be marked.'; }
	if (source === 'replay') { pause(); startReplay(); }
	updateBadges(); renderRunConfig(); render();
}
document.querySelectorAll('[data-source]').forEach(b => b.addEventListener('click', () => setSource(b.dataset.source)));

function updateBadges() {
	if (source === 'demo') setBadge('source-badge', 'warn', 'Demo · illustrative playback', true);
	else if (source === 'replay') setBadge('source-badge', 'warn', 'Replay · recorded, not live', true);
	else setBadge('source-badge', studio?.reachable ? 'bad' : 'off', studio?.reachable ? 'Live' : 'Live · waiting for Studio', Boolean(studio?.reachable));
	const v = studioView(studio);
	setBadge('studio-badge', v.status === 'connected' ? 'ok' : v.status === 'unreachable' ? 'bad' : 'off', v.status === 'connected' ? v.headline : v.status === 'unreachable' ? 'Studio unreachable' : 'Studio link off');
	const ins = studio?.inspector;
	setBadge('device-badge', ins ? 'ok' : 'off', ins ? `${ins.model ?? 'Inspector'} on ${ins.device ?? '?'}` : 'Inspector not connected');
	$('live-headline').textContent = v.status === 'off' ? 'Studio link off. Start the dashboard with --studio-url to see the cell’s cameras.' : v.headline;
	$('control-lock').textContent = studio?.control_enabled ? 'ARM CONTROL ENABLED' : 'ARM CONTROL LOCKED';
	$('control-lock').style.color = studio?.control_enabled ? 'var(--amber)' : '';
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
const STATE_TEXT = {live: 'LIVE', session: 'LIVE · RUN', stale: 'STALE', held: 'HELD BY STUDIO', error: 'ERROR', waiting: 'CONNECTING'};
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
		tile.el.querySelector('.state').textContent = replay ? 'REPLAY' : `${STATE_TEXT[st]}${['live', 'stale'].includes(st) ? ' · ' + camera.age : ''}`;
		const badge = tile.el.querySelector('.badge-live');
		badge.hidden = !(replay || st === 'live' || st === 'session');
		badge.className = `badge-live ${replay ? 'replay' : 'live'}`; badge.textContent = replay ? 'REPLAY' : '● LIVE';
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
			waiting.textContent = st === 'held' ? 'A Studio session is using this camera. Its frames appear here when the run is started from Armigo.' : st === 'error' ? camera.error : 'Connecting to the camera…';
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
	} catch { studio = studio ? {...studio, reachable: false, error: 'dashboard server not responding'} : null; }
	updateBadges();
	if (source !== 'replay') renderCameras(studioView(studio));
	renderRunConfig();
	renderRun();
	setTimeout(pollStudio, source === 'live' ? 700 : 2500);
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
	$('rec-status').innerHTML = `<i></i>REC ${ageText(recorder.duration())}`;
	$('replay-play').disabled = false;
}
$('rec-toggle').addEventListener('click', () => {
	if (source !== 'live' && !recording) { reply('refuse', 'Recording needs Live', 'Switch to Live first. Armigo records the camera tiles, the decision and the run status in this browser.'); return; }
	recording = !recording;
	if (recording) {
		let busy = false;
		recordTimer = setInterval(async () => { if (busy || source !== 'live') return; busy = true; try { await record(); } finally { busy = false; } }, 250);
	} else clearInterval(recordTimer);
	$('rec-status').className = `rec ${recording ? 'on' : ''}`;
	$('rec-toggle').textContent = recording ? '■ Stop rec' : '● Record';
	if (!recording) $('rec-status').innerHTML = `<i></i>${recorder.entries.length ? 'Saved ' + ageText(recorder.duration()) : 'REC off'}`;
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
	const info = ACTIONS[parsed.action];
	if (source === 'replay') { reply('refuse', 'Replay is read-only', 'Switch to Live or Demo to give commands.'); return; }
	if (parsed.action === 'STOP') {
		pause();
		if (source === 'live' && studio?.reachable) { const r = await post('/api/studio/stop', {}); reply('ok', 'Stop sent', r.data?.stopping ? 'Studio holds the arm where it is.' : 'No run was active.'); }
		else reply('ok', 'Stopped', 'Demo playback paused.');
		planSteps.forEach(s => { s.status = 'done'; }); drawPlan(); return;
	}
	if (source === 'demo') {
		reply('ok', `${info.title} · demo`, `${info.summary} This is the illustrative cell; switch to Live to run it on the robot.`);
		if (parsed.action === 'INSPECT') runDemo(pickScenario(), {stopAt: 'reason'});
		else if (parsed.action === 'INSPECT_AND_SORT') runDemo(pickScenario());
		else runDemo(parsed.action === 'SORT_GREEN' ? 'normal' : 'defective');
		return;
	}
	// Live
	if (!studio?.reachable) { reply('error', 'Studio not connected', studioView(studio).headline); return; }
	const cameraId = $('run-camera').value;
	if (parsed.action === 'INSPECT' || (parsed.action === 'INSPECT_AND_SORT' && !studio.control_enabled)) {
		if (!studio.inspector) { reply('error', 'No inspector', 'Start the dashboard with --anomaly-model (or --purity) to score live frames.'); return; }
		planProgress('perceive');
		const t0 = performance.now();
		const r = await post('/api/studio/inspect', {camera_id: cameraId});
		if (r.status !== 200) { reply('error', 'Inspection failed', r.data?.error ?? `HTTP ${r.status}`); planSteps.forEach(s => { if (s.status === 'active') s.status = 'failed'; }); drawPlan(); return; }
		showInspection(r.data, performance.now() - t0);
		if (parsed.action === 'INSPECT_AND_SORT') reply('refuse', `Scored · ${r.data.label}`, 'Arm control is locked, so Armigo inspected without moving. Restart the dashboard with --studio-control to allow runs.');
		return;
	}
	if (!studio.control_enabled) { reply('refuse', 'Arm control locked', 'This dashboard was started without --studio-control, so it cannot move the arm.'); return; }
	if (!$('operator-present').checked) { reply('refuse', 'Confirm the operator', 'Tick “Operator is at the cell” first. Someone must be able to reach the robot’s power.'); return; }
	const model = studio.models.find(m => m.id === $('run-model').value);
	const body = {action: parsed.action, camera_id: cameraId, environment_id: $('run-environment').value, model_id: model?.id, backend: model?.backends[0], device: $('run-device').value};
	planProgress(parsed.action === 'INSPECT_AND_SORT' ? 'perceive' : 'act');
	const t0 = performance.now();
	const r = await post('/api/studio/run', body);
	if (r.data?.inspection) showInspection(r.data.inspection, performance.now() - t0);
	if (r.status === 200 && r.data?.decision === 'review') { reply('refuse', 'Held for a person', 'The score is in the uncertain band, so the arm stays still. Check the part and sort it by hand or re-inspect.'); planProgress('review'); return; }
	if (r.status !== 202) { reply('error', 'Run refused', r.data?.error ?? `HTTP ${r.status}`); return; }
	reply('ok', `Running · ${r.data.decision} bowl`, `Studio is running “${r.data.task}”. Press STOP at any time; the run also stops itself after ${studio.max_run_s} s.`);
	planProgress('act');
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
	brickViews.show({label: result.label, colour: BRICK_COLOURS[0], defect: result.label === 'normal' ? null : {face: 'top', u: 0.1, v: 0.1, kind: 'tape'}});
	render();
	reply(result.label === 'uncertain' ? 'refuse' : 'ok', `${{normal: 'Pass', defective: 'Reject', uncertain: 'Review'}[result.label]} · score ${Number.isFinite(result.score) ? result.score.toFixed(2) : '—'}`,
		result.reason ?? `Inference ${result.timings_ms?.inference?.toFixed(1) ?? '—'} ms on ${result.device ?? 'an unverified device'} · frame was ${ageText(result.frame_age_ms)} old.`);
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
}

function renderRun() {
	const run = studioView(studio).run;
	$('run-bar').hidden = !run || source !== 'live';
	if (!run) return;
	$('run-text').textContent = `${run.text} · ${run.observations ?? 0} observations${run.timings_ms?.model ? ` · policy loaded in ${(run.timings_ms.model / 1000).toFixed(1)} s` : ''}`;
	$('run-progress').style.width = `${(run.progress * 100).toFixed(0)}%`;
	$('stop-run').disabled = !run.moving && !['starting', 'loading_environment', 'loading_model'].includes(run.phase);
}
$('stop-run').addEventListener('click', () => post('/api/studio/stop', {}).then(r => reply('ok', 'Stop sent', r.data?.stopping ? 'Studio holds the arm where it is.' : 'No run was active.')));

$('command-form').addEventListener('submit', e => { e.preventDefault(); execute(parseCommand($('command-input').value)); });
$('command-chips').addEventListener('click', e => {
	const prompt = e.target.closest('[data-prompt]')?.dataset.prompt; if (!prompt) return;
	$('command-input').value = prompt; execute(parseCommand(prompt));
});

// ------------------------------------------------------------------ guided tour
const TOUR = [
	{view: 'home', title: 'One cell, three outcomes', scenario: null,
		text: 'Parts arrive one by one. Today a person checks each one by eye: slow, tiring, and easy to miss a mark. Armigo checks every part the same way and sorts it.',
		metric: ['Outcomes per part', '3'],
		notes: [{anchor: 'spot', title: 'Part arrives', text: 'One brick at a time, under the camera.'}, {anchor: 'green', title: 'Pass', text: 'Good parts move on.'}, {anchor: 'pink', title: 'Reject', text: 'Defects are set aside.', tone: 'red'}, {anchor: 'review', title: 'Ask a person', text: 'When unsure, a human decides.', tone: 'amber'}]},
	{view: 'camera', title: 'Perceive', scenario: 'defective', stage: 'perceive',
		text: 'A fixed camera takes one frame of the part. Studio owns the cameras; Armigo reads the same feed and never opens a camera behind Studio’s back.',
		notes: [{anchor: 'camera', title: 'Top camera', text: 'One frame per part, from Physical AI Studio.'}, {anchor: 'spot', title: 'Inspection spot', text: 'The brick is isolated from the table before scoring.'}]},
	{view: 'laptop', title: 'Detect, on the NPU', scenario: 'defective', stage: 'detect',
		text: 'An Anomalib model learned what a good brick looks like from good examples only, so it flags any mark it has never seen. It runs with OpenVINO on the laptop’s NPU.',
		metric: ['Padim on the NPU (benchmark)', '8.5 ms'],
		notes: [{anchor: 'laptop', title: 'Intel Core Ultra', text: 'Anomalib + OpenVINO. Inference stays on the device.'}]},
	{view: 'bins', title: 'Reason: clear defect', scenario: 'defective', stage: 'reason',
		text: 'The score is compared with two thresholds. Above the upper one, the part is rejected. Watch the defect score meter and the decision panel change.',
		metric: ['Defect score', '0.90'],
		notes: [{anchor: 'pink', title: 'Reject · pink bowl', text: '0.90 is above 0.60.', tone: 'red'}]},
	{view: 'brick', title: 'When unsure, ask', scenario: 'uncertain', stage: 'review',
		text: 'Between the thresholds the model is not sure. Armigo does not guess: the arm stays still and a person takes a second look. Fewer false rejects, no silent misses.',
		metric: ['Defect score', '0.51'],
		notes: [{anchor: 'review', title: 'Human review', text: '0.51 is between 0.40 and 0.60.', tone: 'amber'}, {anchor: 'spot', title: 'Part waits', text: 'No movement until a person decides.', tone: 'amber'}]},
	{view: 'arm', title: 'Act', scenario: 'normal', stage: 'act',
		text: 'For a clear result the SO-101 arm runs one fixed task its policy was trained on, such as “place it in the green bowl”. A typed command can only choose from that closed set.',
		metric: ['Defect score', '0.21'],
		notes: [{anchor: 'arm', title: 'SO-101 policy', text: 'Runs through Physical AI Studio with its speed limits.'}, {anchor: 'green', title: 'Pass · green bowl', text: '0.21 is below 0.40.'}]},
	{view: 'laptop', title: 'Optimize at the edge', scenario: null,
		text: 'Everything above runs on one Intel laptop. Below, Edge performance shows live CPU cores, memory, GPU and NPU load, the busiest processes, and measured inference times.',
		metric: ['Cloud round trips', '0'],
		notes: [{anchor: 'laptop', title: 'One laptop', text: 'Camera feed, model, decisions and dashboard.'}], scroll: 'resource-title'},
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
	$('tour-step').textContent = `STEP ${tourIndex + 1} / ${TOUR.length}`;
	$('tour-title').textContent = step.title; $('tour-text').textContent = step.text;
	$('tour-metric').hidden = !step.metric;
	if (step.metric) { $('tour-metric-label').textContent = step.metric[0]; $('tour-metric-value').textContent = step.metric[1]; }
	$('tour-dots').replaceChildren(...TOUR.map((_, k) => Object.assign(document.createElement('i'), {className: k === tourIndex ? 'on' : ''})));
	$('tour-prev').disabled = tourIndex === 0;
	$('tour-next').textContent = tourIndex === TOUR.length - 1 ? 'Finish' : 'Next →';
	cell.focus(step.view);
	cell.annotate(step.notes);
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
function endTour() { tourIndex = -1; $('tour-card').hidden = true; $('scene').parentElement.classList.remove('touring'); cell.annotate([]); cell.reset(); }
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

// ------------------------------------------------------------------ start
render();
updateBadges();
mountIntro();
mountPerformance();
pollStudio();
