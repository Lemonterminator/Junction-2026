import test from 'node:test';
import assert from 'node:assert/strict';
import { cycleView, cycleSnapshot, mapLayout, CYCLE_STEPS } from '../cell.mjs';
import { validateTelemetry } from '../telemetry.mjs';

const cell = (cycle, extra = {}) => ({configured: true, control_enabled: true, inspector: true, table: null, cycle, ...extra});
const cycle = (extra = {}) => ({
	active: true, go: true, phase: 'measure', seconds: 3, steps: [], log: [], bowls: null, brick: null, attempt: null,
	views: [], decision: null, awaiting_review: false, released_bowl: null, end: null, stop_requested: false, verify: null,
	preset_bowl: null, ...extra,
});
const step = (name, at_s, seconds, extra = {}) => ({name, at_s, seconds, ...extra});
const statuses = view => Object.fromEntries(view.steps.map(s => [s.key, s.status]));

test('without a cell link the panel explains how to start it', () => {
	const off = cycleView(null);
	assert.equal(off.status, 'off');
	assert.match(off.headline, /--bridge/);
	assert.equal(off.canPlan, false);
	assert.equal(off.canGo, false);
});

test('an idle cell can check a plan; running it needs control from the command line', () => {
	const idle = cycleView(cell(null));
	assert.equal(idle.status, 'idle');
	assert.equal(idle.canPlan, true);
	assert.equal(idle.canGo, true);
	const locked = cycleView(cell(null, {control_enabled: false}));
	assert.equal(locked.canGo, false);
	assert.match(locked.lockText, /--cell-control/);
	const noCycle = cycleView(cell(null, {configured: false}));
	assert.equal(noCycle.canPlan, false);
});

test('a running cycle marks finished steps, the current one and their times', () => {
	const view = cycleView(cell(cycle({phase: 'grasp', attempt: 1, steps: [
		step('measure', 0, 2.1), step('hover', 2.1, 11.0, {attempt: 1, tilt_deg: 15, steps: 220}), step('grasp', 13.1, null, {attempt: 1, mode: 'policy'}),
	]})));
	assert.equal(view.status, 'running');
	assert.deepEqual(Object.values(statuses(view)).slice(0, 4), ['done', 'done', 'active', 'pending']);
	assert.equal(view.steps[1].seconds, 11.0);
	assert.match(view.steps[1].detail, /15°/);
	assert.match(view.headline, /Grasp/);
	assert.equal(view.canPlan, false, 'one cycle at a time');
	assert.equal(view.canStop, true);
});

test('a missed grasp and the retry are counted in the grasp step', () => {
	const view = cycleView(cell(cycle({phase: 'grasp', attempt: 2, steps: [
		step('measure', 0, 2), step('hover', 2, 10, {attempt: 1}), step('grasp', 12, 12, {attempt: 1}),
		step('missed', 24, 8, {attempt: 1, outcome: 'timeout'}), step('hover', 32, 9, {attempt: 2}), step('grasp', 41, null, {attempt: 2}),
	]})));
	const grasp = view.steps.find(s => s.key === 'grasp');
	assert.equal(grasp.status, 'active');
	assert.match(grasp.detail, /attempt 2/);
	assert.match(grasp.detail, /1 missed/);
});

test('an unsure brick waits for a person at the decide step', () => {
	const view = cycleView(cell(cycle({phase: 'review', awaiting_review: true,
		steps: [step('measure', 0, 2), step('hover', 2, 9), step('grasp', 11, 4), step('lift', 15, 2), step('show', 17, 8), step('decide', 25, null)],
		views: [{name: 'level', label: 'uncertain', score: 0.52, reason: null, crop: true}],
		decision: {bowl: null, label: 'uncertain', score: 0.52, reason: 'unsure in level: a person decides', source: 'inspection'}})));
	assert.equal(view.status, 'review');
	assert.equal(view.review, true);
	assert.equal(statuses(view).decide, 'held');
	assert.match(view.headline, /you/i);
	assert.equal(view.views[0].crop, '/api/cell/view/0.jpg');
	assert.equal(view.views[0].tone, 'amber');
});

test('a finished, verified cycle is done end to end', () => {
	const view = cycleView(cell(cycle({active: false, phase: 'done', seconds: 61, released_bowl: 'pink', end: {ok: true, reason: null},
		steps: ['measure', 'hover', 'grasp', 'lift', 'show', 'decide', 'place', 'released', 'rest'].map((n, i) => step(n, i * 5, 5)),
		decision: {bowl: 'pink', label: 'defective', score: 0.81, reason: 'defect seen in bottom', source: 'inspection'},
		verify: {confirmed: true, text: 'the top camera sees one more object in the pink bowl'}})));
	assert.equal(view.status, 'done');
	assert.ok(view.steps.every(s => s.status === 'done'), JSON.stringify(statuses(view)));
	assert.match(view.headline, /pink/);
	assert.match(view.headline, /verified/i);
	assert.equal(view.canPlan, true);
});

test('a drop the top camera could not confirm is a warning, not a pass', () => {
	const view = cycleView(cell(cycle({active: false, phase: 'done', released_bowl: 'green', end: {ok: true, reason: null},
		steps: [step('place', 0, 5, {bowl: 'green'}), step('released', 5, 1), step('rest', 6, 4)],
		verify: {confirmed: false, text: 'no new object seen in the green bowl'}})));
	assert.equal(statuses(view).verify, 'warn');
	assert.match(view.steps.at(-1).detail, /no new object/);
});

test('a dry run that only planned skips everything after the hover', () => {
	const view = cycleView(cell(cycle({active: false, go: false, phase: 'done', end: {ok: true, reason: null},
		steps: [step('measure', 0, 2), step('hover', 2, 0.3, {tilt_deg: 30, steps: 180})]})));
	assert.equal(view.status, 'planned');
	assert.match(view.headline, /nothing moved/i);
	assert.deepEqual(Object.values(statuses(view)), ['done', 'done', ...Array(CYCLE_STEPS.length - 2).fill('skipped')]);
});

test('a stop or a fault marks the step it happened in', () => {
	const stopped = cycleView(cell(cycle({active: false, phase: 'stopped', stop_requested: true,
		end: {ok: false, reason: 'stopped by the operator: the arm holds where it is'},
		steps: [step('measure', 0, 2), step('hover', 2, 10), step('grasp', 12, 4), step('lift', 16, 2), step('show', 18, 3)]})));
	assert.equal(stopped.status, 'stopped');
	assert.equal(statuses(stopped).show, 'failed');
	assert.match(stopped.headline, /holds where it is/);
	const failed = cycleView(cell(cycle({active: false, phase: 'failed', end: {ok: false, reason: 'refused: hover: reach'}, steps: [step('measure', 0, 2)]})));
	assert.equal(failed.status, 'failed');
	assert.equal(statuses(failed).measure, 'failed');
});

test('the cycle as a v1 snapshot drives the decision panel without inventing values', () => {
	const running = cycleSnapshot(cycle({phase: 'grasp', steps: [step('measure', 0, 2), step('grasp', 2, null)]}), 4);
	assert.ok(validateTelemetry(running));
	assert.equal(running.stage, 'perceive');
	assert.equal(running.score, null);
	assert.equal(running.destination, null);

	const scoring = cycleSnapshot(cycle({phase: 'show', views: [{name: 'level', label: 'normal', score: 0.2, timings_ms: {inference: 8}}]}), 5);
	assert.ok(validateTelemetry(scoring));
	assert.equal(scoring.stage, 'detect');

	const review = cycleSnapshot(cycle({phase: 'review', awaiting_review: true, decision: {bowl: null, label: 'uncertain', score: 0.5, source: 'inspection'}}), 6);
	assert.ok(validateTelemetry(review));
	assert.equal(review.stage, 'review');

	const done = cycleSnapshot(cycle({active: false, phase: 'done', released_bowl: 'pink', end: {ok: true, reason: null},
		steps: [step('place', 0, 6), step('released', 6, 1), step('rest', 7, 4)],
		views: [{name: 'level', label: 'normal', score: 0.2, timings_ms: {inference: 8}}, {name: 'bottom', label: 'defective', score: 1.4, timings_ms: {inference: 10}}],
		decision: {bowl: 'pink', label: 'defective', score: 1.4, source: 'inspection'}, verify: {confirmed: true, text: ''}}), 7, {device: 'NPU'});
	assert.ok(validateTelemetry(done));
	assert.equal(done.stage, 'complete');
	assert.equal(done.outcome, 'pink');
	assert.equal(done.score, 1, 'scores are clamped to the meter');
	assert.equal(done.timings_ms.inference, 9);
	assert.equal(done.timings_ms.placement, 7000);
	assert.equal(done.device, 'NPU');

	const unverified = cycleSnapshot(cycle({active: false, phase: 'done', released_bowl: 'pink', end: {ok: true, reason: null},
		decision: {bowl: 'pink', label: 'defective', score: 0.9, source: 'inspection'}, verify: {confirmed: false, text: ''}}), 8);
	assert.equal(unverified.outcome, null, 'an unconfirmed drop is never reported as placed');

	const fault = cycleSnapshot(cycle({active: false, phase: 'failed', end: {ok: false, reason: 'STOPPED: lagged'}}), 9);
	assert.ok(validateTelemetry(fault));
	assert.equal(fault.stage, 'fault');
	assert.equal(fault.fault, 'STOPPED: lagged');
});

test('the table map flips y so the camera side is at the bottom and fits everything', () => {
	const layout = mapLayout({bowls: [{colour: 'green', centre_mm: [7, -235, 10], radius_mm: 90}],
		bricks: [{centre_mm: [81, -81, 19], yaw_deg: 30, size_mm: [31, 26]}], robot_base_mm: [158, 190, -20], in_bowl: {green: 2}});
	assert.deepEqual(layout.bowls[0], {colour: 'green', x: 7, y: 235, r: 90, label: '7, −235', inside: 2});
	assert.equal(layout.bricks[0].x, 81);
	assert.equal(layout.bricks[0].y, 81);
	assert.equal(layout.bricks[0].rotate, -30);
	assert.deepEqual([layout.base.x, layout.base.y], [158, -190]);
	const [x, y, w, h] = layout.viewBox;
	assert.ok(x <= 7 - 90 && x + w >= 158 && y <= -190 && y + h >= 235 + 90);
	const empty = mapLayout(null);
	assert.equal(empty.bowls.length, 0);
	assert.equal(empty.viewBox.length, 4);
});

test('typed sorting commands become cycle requests; the inspection picks the bowl unless one was named', async () => {
	const {cycleRequest} = await import('../cell.mjs');
	assert.deepEqual(cycleRequest('INSPECT_AND_SORT'), {go: true, bowl: null});
	assert.deepEqual(cycleRequest('SORT_GREEN'), {go: true, bowl: 'green'});
	assert.deepEqual(cycleRequest('SORT_PINK'), {go: true, bowl: 'pink'});
	assert.equal(cycleRequest('INSPECT'), null, 'inspecting alone never starts the arm');
	assert.equal(cycleRequest('STOP'), null);
});

test('the idle headline says what the top camera sees on the table', () => {
	const table = reading => ({status: 'live', reading, age_ms: 200});
	const one = cycleView(cell(null, {table: table({table: 'anchors 16->17', bricks: [{centre_mm: [150, -140, 19], yaw_deg: 20, size_mm: [32, 31]}], bowls: []})}));
	assert.match(one.headline, /brick at \(150, −140\) mm/);
	const none = cycleView(cell(null, {table: table({table: 'anchors 16->17', bricks: [], bowls: []})}));
	assert.match(none.headline, /no loose brick/i);
	const two = cycleView(cell(null, {table: table({table: 'anchors 16->17', bricks: [{centre_mm: [0, 0, 19]}, {centre_mm: [50, 0, 19]}], bowls: []})}));
	assert.match(two.headline, /2 bricks/);
	const blind = cycleView(cell(null, {table: table({table: null, reason: 'anchors 16 and 17 not seen (saw [])', bricks: [], bowls: []})}));
	assert.match(blind.headline, /anchors 16 and 17 not seen/);
});
