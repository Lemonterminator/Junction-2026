import { createDemo, advanceDemo, displayState, validateTelemetry, stageProgress, explanation } from './telemetry.mjs';
import { CellScene, drawDemoCrop } from './scene.mjs';
import { LatestImageLoader } from './image-loader.mjs';

const $ = id => document.getElementById(id);
const scene = new CellScene($('scene'));
const imageLoader = new LatestImageLoader($('camera-image'), () => {
	document.querySelector('.camera-foot').textContent = 'Camera frame unavailable';
});
let state = createDemo('defective');
for (let i = 0; i < 5; i++) state = advanceDemo(state);
let timer = null;
let part = 1;
const terminal = () => ['complete','review','fault'].includes(state.stage);

function arc(start, end) {
	const point = value => [150 - Math.cos(Math.PI*value)*110, 140 - Math.sin(Math.PI*value)*110];
	const a = point(start), b = point(end);
	return `M${a[0]} ${a[1]} A110 110 0 ${end-start > .5 ? 1 : 0} 1 ${b[0]} ${b[1]}`;
}

function render() {
	const view = displayState(state);
	const demo = state.mode === 'demo';
	const fault = state.stage === 'fault';
	const isDecision = ['reason','act','verify','complete','review','fault'].includes(state.stage);
	const color = fault ? 'fault' : state.label;
	$('decision-panel').className = `panel decision-panel ${color}`;
	$('decision-title').textContent = view.label;
	$('destination').textContent = fault ? 'Operator check required' : view.destination;
	$('destination-dot').className = `dot ${state.destination === 'green' ? 'green' : state.destination === 'pink' ? 'pink' : 'amber'}`;
	$('episode-tag').textContent = demo ? `PART ${String(part).padStart(3,'0')}` : state.episode_id;
	$('decision-score').textContent = view.score;
	$('score-value').textContent = view.score;
	$('task').textContent = isDecision && state.task && !fault ? `${demo ? 'Demo: ' : ''}“${state.task}”` : 'No movement requested';
	$('outcome').textContent = state.stage === 'complete' && state.outcome ? `${demo ? 'Demo: ' : ''}${state.outcome} bowl · verified` : 'Not yet verified';
	$('explanation').textContent = explanation(state);
	$('threshold-copy').textContent = view.thresholdText;
	const low = state.thresholds?.normal_below, high = state.thresholds?.defective_above;
	$('gauge-green').setAttribute('d', state.thresholds ? arc(0, Math.max(0,low-.006)) : '');
	$('gauge-yellow').setAttribute('d', state.thresholds ? arc(low+.006, Math.max(low+.006,high-.006)) : '');
	$('gauge-red').setAttribute('d', state.thresholds ? arc(Math.min(1,high+.006),1) : '');
	$('needle').style.transform = `rotate(${-180 + (state.score ?? 0)*180}deg)`;
	$('needle').style.visibility = state.score === null ? 'hidden' : 'visible';
	$('gauge-title').textContent = state.score === null ? 'Anomaly score unavailable' : `${demo ? 'Demo ' : ''}anomaly score ${view.score}`;
	const stages = stageProgress(state);
	document.querySelectorAll('[data-stage]').forEach((el, index) => {
		const { active, passed } = stages[index];
		el.classList.toggle('active',active);
		el.classList.toggle('passed',passed);
		if (active) el.setAttribute('aria-current','step'); else el.removeAttribute('aria-current');
	});
	$('reason-stage').textContent = isDecision ? (state.destination ? view.destination : 'Human review') : 'Decision';
	$('act-stage').textContent = view.actStatus;
	$('verify-stage').textContent = view.verifyStatus;
	const status = {perceive:'Capturing the part',detect:'Inspecting for defects',reason:'Selecting the destination',act:'Placing the part',verify:'Checking placement',complete:'Cycle complete',review:'Waiting for human review',fault:'Stopped · no automatic retry'};
	$('progress-text').textContent = `${demo ? 'Demo · ' : ''}${status[state.stage]}`;
	$('inspect').disabled = !demo || Boolean(timer);
	$('inspect').firstChild.textContent = !demo ? 'Live controls not connected ' : timer ? 'Inspecting demo part… ' : 'Inspect next part ';
	$('play').disabled = !demo;
	$('scenario').disabled = !demo;
	$('play').textContent = timer ? 'Pause demo' : terminal() ? 'Play demo' : 'Resume demo';
	$('connection').textContent = demo ? 'Illustrative playback' : `${state.mode.toUpperCase()} · ${view.stale ? 'data stale' : 'receiving data'}`;
	document.querySelector('.demo-badge').textContent = demo ? 'Demo · no hardware connected' : `${state.mode.toUpperCase()} · display only`;
	$('source-status').textContent = demo ? 'Local demo · backend not connected' : `${state.mode} · ${view.stale ? 'last update over 3 seconds ago' : 'telemetry connected'}`;
	$('inference-device').textContent = state.device ?? 'Unverified';
	for (const row of document.querySelectorAll('[data-timing]')) {
		const value = state.timings_ms[row.dataset.timing];
		row.querySelector('strong').textContent = value === null ? '—' : value >= 1000 ? `${(value/1000).toFixed(1)} s` : `${value.toFixed(1)} ms`;
		row.querySelector('.bar i').style.width = value === null ? '0' : `${Math.min(100,Math.log10(1+value)/4.3*100)}%`;
	}
	document.querySelector('.timing-note').textContent = Object.values(state.timings_ms).every(v=>v===null)
		? 'Waiting for measured timings. No device performance is claimed in demo mode.'
		: 'Bar length uses a log scale, so fast inference stays visible beside robot motion.';
	$('crop').hidden = !demo;
	if (!demo && state.camera_url) {
		const url = new URL(state.camera_url, location.origin);
		url.searchParams.set('frame_id',String(state.frame_id));
		imageLoader.setSource(url.href);
	} else { imageLoader.setSource(null); }
	document.querySelector('.camera-panel .micro-label').textContent = demo ? 'DEMO IMAGE' : 'INSPECTION CROP';
	document.querySelector('.camera-foot').textContent = demo ? 'Synthetic preview · not a live feed' : state.camera_url ? 'Backend camera frame' : 'Waiting for camera frame';
	document.querySelector('.scene-caption').lastChild.textContent = demo ? ' illustrative cell' : ' live pose integration pending';
	if(demo) drawDemoCrop($('crop'),state.label);
	scene.setState(state);
}

function pause() { clearInterval(timer); timer = null; }
function play() {
	if (state.mode !== 'demo') return;
	if (terminal()) { state = createDemo($('scenario').value); part++; }
	if (terminal()) { render(); return; }
	timer = setInterval(() => {
		state = advanceDemo(state);
		if(terminal()) pause();
		render();
	}, 1150);
	render();
}

$('inspect').addEventListener('click', () => { if (!timer && state.mode === 'demo') play(); });
$('play').addEventListener('click', () => { if(timer) { pause(); render(); } else play(); });
$('scenario').addEventListener('change', () => { pause(); state = createDemo($('scenario').value); render(); });
$('reset-view').addEventListener('click', () => scene.reset());
document.addEventListener('keydown', e => {
	if(e.code !== 'Space' || e.repeat || /^(INPUT|SELECT|TEXTAREA|BUTTON|A|CANVAS)$/.test(e.target.tagName) || e.target.isContentEditable) return;
	e.preventDefault(); if(!$('inspect').disabled) $('inspect').click();
});

/** Future transport adapters dispatch snapshots; this UI never sends hardware commands. */
window.addEventListener('sorter:telemetry', event => {
	if (!validateTelemetry(event.detail)) {
		$('connection').textContent = 'Invalid telemetry · update rejected';
		return;
	}
	pause();
	state = structuredClone(event.detail);
	render();
});
setInterval(() => {
	if(state.mode !== 'demo') {
		const stale=displayState(state).stale;
		$('connection').textContent = `${state.mode.toUpperCase()} · ${stale ? 'data stale' : 'receiving data'}`;
		$('source-status').textContent = `${state.mode} · ${stale ? 'last update over 3 seconds ago' : 'telemetry connected'}`;
	}
},1000);
render();
