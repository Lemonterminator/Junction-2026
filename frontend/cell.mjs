/**
 * Display logic for the real cell: the hybrid sort cycle's steps, its inspection views, the table map from depth,
 * and the cycle as a v1 snapshot for the decision panel. Everything shown comes from /api/cell/state; nothing is
 * filled in when the backend has not measured it.
 */

export const CYCLE_STEPS = [
	{key: 'measure', title: 'Measure', sub: 'Top camera, colour + depth'},
	{key: 'hover', title: 'Hover', sub: 'Scripted, checked path'},
	{key: 'grasp', title: 'Grasp', sub: 'Learned policy'},
	{key: 'lift', title: 'Lift', sub: 'Scripted'},
	{key: 'show', title: 'Inspect', sub: 'Front camera, every side'},
	{key: 'decide', title: 'Decide', sub: 'All views, or a person'},
	{key: 'place', title: 'Place', sub: 'Over the chosen bowl'},
	{key: 'rest', title: 'Rest', sub: 'Back out of the way'},
	{key: 'verify', title: 'Verify', sub: 'Depth: is it in the bowl?'},
];
const ORDER = CYCLE_STEPS.map(s => s.key);
const GROUP = {measure: 'measure', hover: 'hover', grasp: 'grasp', missed: 'grasp', lift: 'lift', show: 'show',
	decide: 'decide', review: 'decide', place: 'place', released: 'place', rest: 'rest'};
const FINAL = new Set(['done', 'failed', 'stopped', 'held']);
const LABEL = {normal: 'Pass', defective: 'Reject', uncertain: 'Unsure'};
const TONE = {normal: 'green', defective: 'red', uncertain: 'amber'};
const SOURCE = {inspection: 'by inspection', operator: 'by the operator', command: 'as commanded'};

const minus = v => String(Math.round(v)).replace('-', '−');
const mm = p => `(${minus(p[0])}, ${minus(p[1])}) mm`;

function stepDetail(key, events, c) {
	if (!events.length && key !== 'measure') return '';
	const last = events.at(-1) ?? {};
	if (key === 'measure') {
		const bowls = c.bowls ? Object.keys(c.bowls).length : 0;
		return [bowls ? `${bowls} bowl${bowls > 1 ? 's' : ''}` : '', c.brick ? `brick at ${mm(c.brick.centre_mm)}` : ''].filter(Boolean).join(' · ');
	}
	if (key === 'hover') return Number.isFinite(last.tilt_deg) ? `${Math.round(last.tilt_deg)}° approach · ${last.steps} steps` : '';
	if (key === 'grasp') {
		const missed = events.filter(e => e.name === 'missed').length;
		const attempt = c.attempt ?? last.attempt;
		return [attempt ? `attempt ${attempt}` : '', missed ? `${missed} missed` : '', last.mode === 'script' ? 'scripted' : ''].filter(Boolean).join(' · ');
	}
	if (key === 'show') return c.views.length ? `${c.views.length} view${c.views.length > 1 ? 's' : ''} scored` : '';
	if (key === 'decide') {
		const d = c.decision;
		if (!d) return '';
		return d.bowl ? `${LABEL[d.label] ?? d.label} → ${d.bowl} ${SOURCE[d.source] ?? ''}`.trim() : d.reason ?? 'a person decides';
	}
	if (key === 'place') return c.released_bowl ? `released over ${c.released_bowl}` : last.bowl ? `${last.bowl} bowl` : '';
	return '';
}

/** What the cell panel shows: status, headline, the nine steps with their state, views and what the operator may do. */
export function cycleView(cell, {token = ''} = {}) {
	const lockText = cell && !cell.control_enabled ? 'Arm locked · start the dashboard with --cell-control to run the cycle' : '';
	const blank = status => CYCLE_STEPS.map(s => ({...s, status, seconds: null, detail: ''}));
	if (!cell) {
		return {status: 'off', headline: 'Cell link off · start the dashboard with --bridge and --hybrid-command', steps: blank('pending'),
			views: [], review: false, canPlan: false, canGo: false, canStop: false, lockText: '', decision: null, log: []};
	}
	const c = cell.cycle;
	const canPlan = Boolean(cell.configured) && !c?.active;
	const common = {canPlan, canGo: canPlan && Boolean(cell.control_enabled), canStop: Boolean(c?.active), lockText};
	if (!c) {
		const r = cell.table?.status === 'live' ? cell.table.reading : null;
		const seen = !r ? 'put a brick on the table' : !r.table ? `the top camera has no table frame: ${r.reason}`
			: r.bricks.length === 0 ? 'no loose brick on the table' : r.bricks.length === 1 ? `brick at ${mm(r.bricks[0].centre_mm)}`
			: `${r.bricks.length} bricks on the table; the cycle needs one (or --near)`;
		return {status: 'idle', steps: blank('pending'), views: [], review: false, decision: null, log: [], ...common,
			headline: cell.configured ? `Ready · ${seen}` : `Table view only · ${seen}`};
	}
	const final = FINAL.has(c.phase);
	const byKey = Object.fromEntries(ORDER.map(k => [k, []]));
	for (const event of c.steps) if (GROUP[event.name]) byKey[GROUP[event.name]].push(event);
	const lastEvent = c.steps.at(-1);
	const current = c.phase === 'review' ? 'decide' : lastEvent ? GROUP[lastEvent.name] ?? null : null;
	const at = current ? ORDER.indexOf(current) : final ? 0 : -1;
	const steps = CYCLE_STEPS.map((s, i) => {
		const events = byKey[s.key] ?? [];
		let status;
		if (s.key === 'verify') {
			const v = c.verify;
			status = v ? (v.confirmed === true ? 'done' : v.confirmed === false ? 'warn' : 'skipped')
				: final && c.released_bowl && c.end?.ok ? 'active' : final ? 'skipped' : 'pending';
			return {...s, status, seconds: null, detail: v?.text ?? (status === 'active' ? 'checking the bowl…' : '')};
		}
		if (!final) status = i < at ? 'done' : i === at ? (c.phase === 'review' ? 'held' : 'active') : 'pending';
		else if (c.end?.ok) status = i <= at ? 'done' : 'skipped';
		else status = i < at ? 'done' : i === at ? (c.phase === 'held' ? 'held' : 'failed') : 'skipped';
		let seconds = events.length ? events.reduce((sum, e) => sum + (Number.isFinite(e.seconds) ? e.seconds : 0), 0) : null;
		const open = events.at(-1);
		if (status === 'active' && open && !Number.isFinite(open.seconds)) seconds += Math.max(0, c.seconds - open.at_s);
		return {...s, status, seconds: seconds === null ? null : Math.round(seconds * 10) / 10, detail: stepDetail(s.key, events, c)};
	});
	const views = c.views.map((v, i) => ({...v, tone: TONE[v.label] ?? 'amber', crop: v.crop ? `/api/cell/view/${i}.jpg${token ? `?c=${token}` : ''}` : null,
		scoreText: Number.isFinite(v.score) ? v.score.toFixed(2) : '—'}));
	let status, headline;
	const reason = c.end?.reason ?? '';
	if (!final) {
		status = c.phase === 'review' || c.awaiting_review ? 'review' : 'running';
		const active = steps.find(s => s.status === 'active' || s.status === 'held');
		headline = status === 'review' ? 'Unsure brick · you decide; the arm holds it in front of the camera'
			: `${c.go ? '' : 'Plan check · '}${active ? active.title : 'Starting'}${active?.detail ? ' · ' + active.detail : ''}`;
	} else if (c.phase === 'done' && !c.go) {
		status = 'planned';
		headline = `Plan checked · nothing moved${steps[1].detail ? ' · ' + steps[1].detail : ''}`;
	} else if (c.phase === 'done') {
		status = 'done';
		const v = c.verify;
		headline = c.released_bowl
			? `Done · ${c.released_bowl} bowl${v?.confirmed === true ? ', verified by depth' : v?.confirmed === false ? ', not confirmed by the top camera' : ''}`
			: 'Done';
	} else {
		status = c.phase;
		headline = {stopped: 'Stopped', failed: 'Stopped on a fault', held: 'Holding the brick for review'}[c.phase] + (reason ? ` · ${reason}` : '');
	}
	return {status, headline, steps, views, review: Boolean(c.awaiting_review), decision: c.decision, log: c.log, ...common};
}

function median(values) {
	if (!values.length) return null;
	const s = [...values].sort((a, b) => a - b), m = Math.floor(s.length / 2);
	return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
const clamp01 = v => Number.isFinite(v) ? Math.min(1, Math.max(0, v)) : null;

/**
 * The cycle as a v1 snapshot for the decision panel, the pipeline strip and the illustrative 3D cell.
 * A dry run moves nothing and decides nothing, so it has no snapshot (null).
 */
export function cycleSnapshot(c, sequence, {device = null, thresholds = null} = {}) {
	if (!c || !c.go) return null;
	const d = c.decision;
	const scores = c.views.map(v => v.score).filter(Number.isFinite);
	let stage;
	if (c.phase === 'failed' || c.phase === 'stopped') stage = 'fault';
	else if (c.phase === 'held' || c.phase === 'review' || c.awaiting_review) stage = 'review';
	else if (c.phase === 'done') stage = 'complete';
	else if (c.phase === 'released' || c.phase === 'rest') stage = 'verify';
	else if (c.phase === 'place') stage = 'act';
	else if (c.phase === 'decide' && d) stage = 'reason';
	else if ((c.phase === 'show' || c.phase === 'decide') && c.views.length) stage = 'detect';
	else stage = 'perceive';
	const destination = ['green', 'pink'].includes(d?.bowl) ? d.bowl : null;
	const placeSeconds = c.steps.filter(s => s.name === 'place' || s.name === 'released').reduce((sum, s) => sum + (Number.isFinite(s.seconds) ? s.seconds : 0), 0);
	const inference = median(c.views.map(v => v.timings_ms?.inference).filter(Number.isFinite));
	return {
		schema_version: 1, episode_id: `cycle-${sequence}`, mode: 'real', timestamp: Date.now(), stage,
		label: d?.label ?? (scores.length ? (c.views.some(v => v.label === 'defective') ? 'defective' : 'uncertain') : 'uncertain'),
		score: clamp01(d?.score ?? (scores.length ? Math.max(...scores) : null)),
		thresholds, destination, task: destination ? `Place the brick in the ${destination} bowl.` : null,
		joints: null, joint_unit: null, frame_id: sequence, camera_url: null, heatmap_url: null,
		outcome: c.verify?.confirmed === true && ['green', 'pink'].includes(c.released_bowl) ? c.released_bowl : null,
		device, timings_ms: {capture: null, inference, placement: placeSeconds ? Math.round(placeSeconds * 1000) : null},
		fault: stage === 'fault' ? (c.end?.reason ?? 'The cycle stopped.') : null,
	};
}

/** Table-frame millimetres as SVG coordinates (y flipped: the camera side at the bottom) for the table map. */
export function mapLayout(reading) {
	const bowls = (reading?.bowls ?? []).map(b => ({colour: b.colour, x: b.centre_mm[0], y: -b.centre_mm[1], r: b.radius_mm,
		label: `${minus(b.centre_mm[0])}, ${minus(b.centre_mm[1])}`, inside: reading.in_bowl?.[b.colour] ?? null}));
	const bricks = (reading?.bricks ?? []).map(b => ({x: b.centre_mm[0], y: -b.centre_mm[1], w: b.size_mm[0], h: b.size_mm[1], rotate: -b.yaw_deg,
		label: `${minus(b.centre_mm[0])}, ${minus(b.centre_mm[1])}`}));
	const base = reading?.robot_base_mm ? {x: reading.robot_base_mm[0], y: -reading.robot_base_mm[1]} : null;
	const pts = [[0, 0], ...bowls.flatMap(b => [[b.x - b.r, b.y - b.r], [b.x + b.r, b.y + b.r]]),
		...bricks.flatMap(b => [[b.x - b.w, b.y - b.w], [b.x + b.w, b.y + b.w]]), ...(base ? [[base.x - 60, base.y - 60], [base.x + 60, base.y + 60]] : [])];
	const margin = 40;
	const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
	let [x0, x1, y0, y1] = [Math.min(...xs) - margin, Math.max(...xs) + margin, Math.min(...ys) - margin, Math.max(...ys) + margin];
	if (pts.length === 1) [x0, x1, y0, y1] = [-150, 450, -250, 350];
	return {bowls, bricks, base, origin: {x: 0, y: 0}, viewBox: [x0, y0, x1 - x0, y1 - y0]};
}

/** The cycle request for a typed action: sorting actions move the arm, and only a named bowl overrides the inspection. */
export function cycleRequest(action) {
	return {INSPECT_AND_SORT: {go: true, bowl: null}, SORT_GREEN: {go: true, bowl: 'green'}, SORT_PINK: {go: true, bowl: 'pink'}}[action] ?? null;
}
