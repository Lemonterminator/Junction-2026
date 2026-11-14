/** UI contract. Decisions belong to the backend; only the demo creates illustrative values. */
export const STAGES = ['perceive', 'detect', 'reason', 'act', 'verify', 'complete', 'review', 'fault'];
const LABELS = { normal: 'Perfect', defective: 'Defective', uncertain: 'Needs review' };

export function createDemo(scenario = 'defective', now = Date.now()) {
	const label = scenario === 'fault' ? 'uncertain' : scenario;
	const destination = label === 'normal' ? 'green' : label === 'defective' ? 'pink' : null;
	return {
		schema_version: 1, episode_id: `demo-${scenario}`, mode: 'demo', timestamp: now,
		stage: scenario === 'fault' ? 'fault' : 'perceive', label,
		score: scenario === 'fault' ? null : { normal: 0.21, defective: 0.90, uncertain: 0.51 }[label],
		thresholds: { normal_below: 0.40, defective_above: 0.60 }, destination,
		task: destination ? `Pick up the brick and place it in the ${destination} bowl.` : null,
		joints: [0, -80, 50, 90, 0, 100], joint_unit: 'degrees_and_gripper_0_100',
		frame_id: 0, camera_url: null, heatmap_url: null, outcome: null,
		device: null, timings_ms: { capture: null, inference: null, placement: null },
		fault: scenario === 'fault' ? 'Demo fault: servo communication lost. Operator check required.' : null,
	};
}

export function advanceDemo(state, now = Date.now()) {
	if (['complete', 'review', 'fault'].includes(state.stage)) return state;
	let stage = STAGES[STAGES.indexOf(state.stage) + 1];
	if (state.stage === 'reason' && state.label === 'uncertain') stage = 'review';
	return { ...state, stage, timestamp: now, frame_id: state.frame_id + 1,
		outcome: stage === 'complete' ? state.destination : null };
}

export function displayState(state, now = Date.now()) {
	return {
		label: state.stage === 'fault' ? 'Arm stopped' : LABELS[state.label],
		score: Number.isFinite(state.score) ? state.score.toFixed(2) : '—',
		destination: state.destination ? `${state.destination[0].toUpperCase()}${state.destination.slice(1)} bowl` : 'Human review',
		stale: now - state.timestamp > 3000,
	};
}

export function stageProgress(state) {
	const current = state.stage === 'review' ? 2 : state.stage === 'fault' ? -1 : STAGES.indexOf(state.stage);
	return STAGES.slice(0, 5).map((stage, index) => ({ stage,
		active: index === current || (state.stage === 'complete' && index === 4),
		passed: index < current,
	}));
}

export function explanation(state) {
	if (state.stage === 'fault') return state.fault || 'The arm stopped. An operator must check the cell.';
	if (state.label === 'uncertain') return 'This part needs a second look. Sorting is paused for human review.';
	if (state.score === null) return 'No anomaly score is available. Waiting for inspection evidence.';
	if (state.mode !== 'demo') return `The backend classified this part as ${state.label}${state.destination ? ` and assigned it to the ${state.destination} bowl` : ''}.`;
	return `Demo score ${state.score.toFixed(2)} is ${state.label === 'normal' ? `below ${state.thresholds.normal_below.toFixed(2)}` : `above ${state.thresholds.defective_above.toFixed(2)}`}, so the part is assigned to the ${state.destination} bowl.`;
}

/** Validate the documented v1 snapshot before it enters the presentation layer. */
export function validateTelemetry(s) {
	return Boolean(s && s.schema_version === 1 && ['demo', 'twin', 'replay', 'real'].includes(s.mode)
		&& typeof s.episode_id === 'string' && Number.isFinite(s.timestamp) && STAGES.includes(s.stage)
		&& Object.hasOwn(LABELS, s.label) && (s.score === null || (Number.isFinite(s.score) && s.score >= 0 && s.score <= 1))
		&& s.thresholds && Number.isFinite(s.thresholds.normal_below) && Number.isFinite(s.thresholds.defective_above)
		&& s.thresholds.normal_below >= 0 && s.thresholds.normal_below <= s.thresholds.defective_above && s.thresholds.defective_above <= 1
		&& [null, 'green', 'blue', 'pink'].includes(s.destination) && [null, 'green', 'blue', 'pink'].includes(s.outcome)
		&& (s.task === null || typeof s.task === 'string') && (s.fault === null || typeof s.fault === 'string')
		&& Array.isArray(s.joints) && s.joints.length === 6 && s.joints.every(Number.isFinite)
		&& s.joint_unit === 'degrees_and_gripper_0_100' && Number.isInteger(s.frame_id) && s.frame_id >= 0
		&& [s.camera_url, s.heatmap_url].every(url => url === null || (typeof url === 'string' && url.startsWith('/') && !url.startsWith('//') && !/[\\\u0000-\u0020\u007f]/.test(url)))
		&& (s.device === null || typeof s.device === 'string') && s.timings_ms
		&& ['capture', 'inference', 'placement'].every(key => s.timings_ms[key] === null || (Number.isFinite(s.timings_ms[key]) && s.timings_ms[key] >= 0)));
}
