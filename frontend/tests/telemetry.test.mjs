import test from 'node:test';
import assert from 'node:assert/strict';
import { createDemo, advanceDemo, displayState, validateTelemetry, stageProgress, explanation } from '../telemetry.mjs';
import { CellScene } from '../scene.mjs';

test('demo cycles through inspection, movement and verified placement', () => {
	let state = createDemo('defective', 1000);
	assert.equal(state.mode, 'demo');
	assert.equal(state.stage, 'perceive');
	for (let i = 0; i < 5; i++) state = advanceDemo(state, 2000 + i);
	assert.equal(state.stage, 'complete');
	assert.equal(state.outcome, 'pink');
	assert.equal(advanceDemo(state, 9999), state);
});

test('uncertain inspection stops for review without entering movement', () => {
	let state = createDemo('uncertain', 1000);
	for (let i = 0; i < 5; i++) state = advanceDemo(state, 2000 + i);
	assert.equal(state.stage, 'review');
	assert.equal(state.task, null);
	assert.equal(state.outcome, null);
});

test('backend labels and destinations are authoritative; missing scores remain empty', () => {
	const state = { ...createDemo('normal', 1000), mode: 'real', score: null, destination: 'green', label: 'uncertain' };
	const view = displayState(state, 1001);
	assert.equal(view.score, '—');
	assert.equal(view.destination, 'Green bowl');
	assert.equal(view.label, 'Needs review');
	assert.equal(view.stale, false);
	assert.equal(displayState(state, 5001).stale, true);
});

test('contract rejects invalid stages, units, nonfinite scores and ambiguous sources', () => {
	assert.equal(validateTelemetry(createDemo('normal', 1)), true);
	for (const patch of [{ mode: 'unknown' }, { stage: 'moving' }, { score: NaN }, { timestamp: NaN }, { joint_unit: 'ticks' }, { joints: [1] }]) {
		assert.equal(validateTelemetry({ ...createDemo('normal', 1), ...patch }), false);
	}
});

test('normal demo uses configured green destination and fault state never claims placement', () => {
	let state = createDemo('normal', 1000);
	for (let i = 0; i < 5; i++) state = advanceDemo(state, 2000 + i);
	assert.equal(state.outcome, 'green');
	const fault = createDemo('fault', 1000);
	assert.equal(fault.stage, 'fault');
	assert.equal(fault.outcome, null);
	assert.equal(displayState(fault, 1000).label, 'Arm stopped');
});

test('image paths cannot escape the current origin and frame ids are nonnegative', () => {
	const state = createDemo('normal', 1000);
	for (const camera_url of ['//external.example/image', '/\\external.example/image', '/\n/external.example/image', '/\t/external.example/image']) {
		assert.equal(validateTelemetry({ ...state, camera_url }), false);
	}
	assert.equal(validateTelemetry({ ...state, camera_url: '/frames/top.jpg?frame=1' }), true);
	assert.equal(validateTelemetry({ ...state, frame_id: -1 }), false);
});

test('review never marks movement or verification as completed', () => {
	const stages = stageProgress({ ...createDemo('uncertain'), stage: 'review' });
	assert.equal(stages.find(s => s.stage === 'reason').active, true);
	for (const key of ['act', 'verify']) {
		assert.equal(stages.find(s => s.stage === key).passed, false);
	}
	assert.equal(stageProgress(createDemo('fault')).some(s => s.passed), false);
});

test('fault freezes the illustration at its current pose', () => {
	const scene = Object.create(CellScene.prototype);
	scene.tip = [.1, .8, .3];
	scene.target = [.5, .2, .1];
	scene.draw = () => {};
	scene.setState(createDemo('fault'));
	assert.deepEqual(scene.target, [.1, .8, .3]);
});

test('backend decision text does not infer a threshold comparison from the label', () => {
	const state = { ...createDemo('normal'), mode: 'real', score: .9 };
	assert.equal(explanation(state), 'The backend classified this part as normal and assigned it to the green bowl.');
});

test('completion does not claim placement or verification without an outcome', () => {
	const state = { ...createDemo('normal'), mode: 'real', stage: 'complete', outcome: null };
	assert.equal(validateTelemetry(state), true);
	assert.equal(displayState(state).actStatus, 'Not confirmed');
	assert.equal(displayState(state).verifyStatus, 'Not verified');
	assert.equal(stageProgress(state).find(s => s.stage === 'verify').passed, false);
	const verified = { ...state, outcome: 'pink' };
	assert.equal(displayState(verified).actStatus, 'Placed');
	assert.equal(displayState(verified).verifyStatus, 'Confirmed');
	assert.equal(stageProgress(verified).find(s => s.stage === 'verify').passed, true);
});

test('missing thresholds and joint readings are valid and remain explicitly unavailable', () => {
	const state = { ...createDemo('normal'), mode: 'replay', score: null, thresholds: null, joints: null, joint_unit: null };
	assert.equal(validateTelemetry(state), true);
	assert.equal(displayState(state).thresholdText, 'Inspection thresholds unavailable');
	assert.equal(validateTelemetry({ ...state, joints: [1, 2, 3, 4, 5, 6] }), false);
	assert.equal(validateTelemetry({ ...state, joint_unit: 'degrees_and_gripper_0_100' }), false);
	assert.equal(validateTelemetry({ ...state, thresholds: { normal_below: .8, defective_above: .2 } }), false);
});
