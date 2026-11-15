import test from 'node:test';
import assert from 'node:assert/strict';
import { studioView, inspectionSnapshot, SessionRecorder, ageText } from '../studio.mjs';

const NOW = 1_000_000;
const base = (extra = {}) => ({
	configured: true, reachable: true, error: null, project: {id: 'p1', name: 'Sorting'},
	cameras: [], environments: [], models: [], control_enabled: false, max_run_s: 60,
	inspector: null, inspection: null, run: null, timestamp: NOW, ...extra,
});

test('a missing or unreachable Studio is reported, never shown as live', () => {
	assert.equal(studioView(null, NOW).status, 'off');
	const down = studioView(base({reachable: false, error: 'connection refused'}), NOW);
	assert.equal(down.status, 'unreachable');
	assert.match(down.headline, /connection refused/);
	assert.equal(studioView(base(), NOW).status, 'connected');
});

test('camera tiles separate live, stale, held-by-session and waiting feeds', () => {
	const view = studioView(base({cameras: [
		{id: 'a', name: 'Top', status: 'live', error: null, age_ms: 120, sequence: 4},
		{id: 'b', name: 'Wrist', status: 'live', error: null, age_ms: 4200, sequence: 9},
		{id: 'c', name: 'Depth', status: 'error', error: "Camera 'Depth' is in use by a runtime session in project 'Sorting'", age_ms: null, sequence: null},
		{id: 'd', name: 'Side', status: 'connecting', error: null, age_ms: null, sequence: null},
	]}), NOW);
	assert.deepEqual(view.cameras.map(c => c.state), ['live', 'stale', 'held', 'waiting']);
	assert.equal(view.cameras[0].age, '120 ms');
	assert.equal(view.cameras[1].age, '4.2 s');
});

test('frames from an active run count as live even while the preview relay is held', () => {
	const view = studioView(base({
		cameras: [{id: 'c', name: 'Top', status: 'error', error: 'in use by a runtime session', age_ms: null, sequence: null}],
		run: {phase: 'running', frames: {top: {sequence: 3, received_at: NOW / 1000 - 0.05}}},
	}), NOW);
	assert.equal(view.cameras[0].state, 'session');
});

test('run phases become operator text and arm-moving phases are flagged', () => {
	const running = studioView(base({control_enabled: true, run: {phase: 'running', running_s: 12, max_s: 60, task: 'Pick up the brick and place it in the green bowl.', reason: null}}), NOW);
	assert.equal(running.run.moving, true);
	assert.equal(running.run.progress, 0.2);
	assert.match(running.run.text, /Running/);
	const failed = studioView(base({run: {phase: 'failed', reason: 'environment/follower: overload', running_s: 3, max_s: 60}}), NOW);
	assert.equal(failed.run.moving, false);
	assert.match(failed.run.text, /overload/);
	assert.equal(studioView(base(), NOW).run, null);
});

test('a live inspection becomes a v1-shaped snapshot with measured timings only', () => {
	const snap = inspectionSnapshot({
		label: 'defective', score: 0.83, reason: null, thresholds: {normal_below: 0.5, defective_above: 0.5},
		device: 'NPU', model: 'padim@NPU', timings_ms: {decode: 1.2, isolate: 3.4, inference: 8.6},
		camera_id: 'c1', frame_age_ms: 40, timestamp: NOW,
	}, 7);
	assert.equal(snap.mode, 'real');
	assert.equal(snap.stage, 'reason');
	assert.equal(snap.destination, 'pink');
	assert.equal(snap.task, 'Pick up the brick and place it in the pink bowl.');
	assert.deepEqual(snap.timings_ms, {capture: 40, inference: 8.6, placement: null});
	assert.equal(snap.device, 'NPU');
	assert.equal(snap.episode_id, 'live-7');
	const review = inspectionSnapshot({label: 'uncertain', score: null, reason: 'no brick found in the frame', thresholds: {normal_below: 0.4, defective_above: 0.6}, device: 'CPU', model: 'm', timings_ms: {decode: 1, isolate: 2, inference: null}, camera_id: 'c', frame_age_ms: 10, timestamp: NOW}, 8);
	assert.equal(review.stage, 'review');
	assert.equal(review.destination, null);
	assert.equal(review.score, null);
});

test('the recorder keeps a bounded window and replays by elapsed time', () => {
	const recorder = new SessionRecorder({maxSeconds: 10});
	for (let t = 0; t <= 15_000; t += 1000) recorder.add(t, {n: t});
	assert.equal(recorder.duration(), 10_000);
	assert.equal(recorder.at(0).state.n, 5000, 'oldest kept entry');
	assert.equal(recorder.at(2500).state.n, 7000, 'latest entry at or before the offset');
	assert.equal(recorder.at(99_000).state.n, 15_000);
	recorder.clear();
	assert.equal(recorder.at(0), null);
});

test('age text', () => {
	assert.equal(ageText(null), '—');
	assert.equal(ageText(999), '999 ms');
	assert.equal(ageText(65_000), '65 s');
});
