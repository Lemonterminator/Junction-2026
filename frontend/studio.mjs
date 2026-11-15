/** Display logic for the Physical AI Studio link: camera feed states, run text, live inspection snapshots, replay. */
import { TASKS } from './command.mjs';

export function ageText(ms) {
	if (!Number.isFinite(ms)) return '—';
	if (ms < 1000) return `${Math.round(ms)} ms`;
	if (ms < 10_000) return `${(ms / 1000).toFixed(1)} s`;
	return `${Math.round(ms / 1000)} s`;
}

const MOVING = new Set(['starting_control', 'running', 'stopping']);
/** Phases in which a run exists on the server and STOP still has something to cancel. */
const ACTIVE = new Set(['starting', 'loading_environment', 'loading_model', 'checking', 'starting_control', 'running', 'stopping']);
const PHASE_TEXT = {
	starting: 'Connecting to Studio', loading_environment: 'Loading the robot and cameras', loading_model: 'Loading the policy',
	checking: 'Inspecting the part', starting_control: 'Handing the arm to the policy', running: 'Running',
	stopping: 'Holding the arm', stopped: 'Stopped', failed: 'Stopped on a fault', held: 'Held still',
};

function runView(r, reachable) {
	const progress = Number.isFinite(r.running_s) && r.max_s > 0 ? Math.min(1, r.running_s / r.max_s) : 0;
	const detail = r.reason ? ` · ${r.reason}` : Number.isFinite(r.running_s) ? ` · ${r.running_s.toFixed(0)} of ${r.max_s} s` : '';
	const stoppable = ACTIVE.has(r.phase);
	const text = !reachable && stoppable
		? `Studio not answering · last seen: ${PHASE_TEXT[r.phase] ?? r.phase}. Press Stop to make sure the arm holds.`
		: `${PHASE_TEXT[r.phase] ?? r.phase}${detail}`;
	return {...r, moving: MOVING.has(r.phase), stoppable, progress, text};
}
export const STALE_FRAME_MS = 2000;

export function studioView(state, now = Date.now()) {
	if (!state || !state.configured) return {status: 'off', headline: 'Studio link off · start the dashboard with --studio-url', cameras: [], run: null};
	if (!state.reachable) {
		// The REST lists can fail while the runtime socket still drives the arm: keep the last run and its stop control.
		return {status: 'unreachable', headline: `Studio unreachable · ${state.error ?? 'no response'}`, cameras: [], run: state.run ? runView(state.run, false) : null};
	}
	const runFrames = state.run?.phase === 'running' ? state.run.frames ?? {} : {};
	const sessionFresh = Object.values(runFrames).some(f => now - f.received_at * 1000 < STALE_FRAME_MS);
	const cameras = state.cameras.map(camera => {
		let cameraState = 'waiting';
		if (camera.status === 'error' && /in use|runtime session/i.test(camera.error ?? '')) cameraState = sessionFresh ? 'session' : 'held';
		else if (camera.status === 'error') cameraState = 'error';
		else if (Number.isFinite(camera.age_ms)) cameraState = camera.age_ms > STALE_FRAME_MS ? 'stale' : 'live';
		return {...camera, state: cameraState, age: ageText(camera.age_ms)};
	});
	return {status: 'connected', headline: `Studio · ${state.project?.name ?? 'project'}`, cameras, run: state.run ? runView(state.run, true) : null};
}

/**
 * Where a STOP goes. It is routed before any view or health check: whenever the dashboard has a Studio link a
 * backend run may exist, so the stop request is always sent; the demo is paused as well when it is playing.
 */
export function stopPlan({linked, demoRunning}) {
	return {backend: Boolean(linked), demo: Boolean(demoRunning)};
}

/** 'requested' until the server reports a run that can no longer move; 'none' when no stop was asked for. */
export function stopStatus(run, requested) {
	if (!requested) return 'none';
	return run && !ACTIVE.has(run.phase) ? 'confirmed' : 'requested';
}

/** Leaving Live hides the cameras, so a run that may still move is stopped. */
export function leavingLiveStops(from, to, run) {
	return from === 'live' && to !== 'live' && Boolean(run) && ACTIVE.has(run.phase);
}

/**
 * The four-view brick for a live result. Inspection returns a score and a crop, not a defect location, so the
 * model stays illustrative and carries no defect mark; the crop is the evidence.
 */
export function liveBrickModel(result) {
	const scored = Number.isFinite(result?.score);
	const note = !scored
		? `Nothing scored: ${result?.reason ?? 'no result'}.`
		: 'The model does not locate defects; the crop on the left is what it scored.';
	return {label: scored ? result.label : 'none', defect: null, illustrative: true, note};
}

/** A live inspection as a v1 snapshot for the decision panel; timings are the measured ones only. */
export function inspectionSnapshot(inspection, sequence) {
	const label = inspection.label;
	const destination = label === 'normal' ? 'green' : label === 'defective' ? 'pink' : null;
	return {
		schema_version: 1, episode_id: `live-${sequence}`, mode: 'real', timestamp: inspection.timestamp,
		stage: destination ? 'reason' : 'review', label, score: Number.isFinite(inspection.score) ? Math.min(1, Math.max(0, inspection.score)) : null,
		thresholds: inspection.thresholds ?? null, destination, task: destination ? TASKS[destination] : null,
		joints: null, joint_unit: null, frame_id: sequence, camera_url: null, heatmap_url: null, outcome: null,
		device: inspection.device ?? null,
		timings_ms: {capture: inspection.frame_age_ms ?? null, inference: inspection.timings_ms?.inference ?? null, placement: null},
		fault: null,
	};
}

/** In-browser recording of the live view for replay when the venue link or the hardware lets the demo down. */
export class SessionRecorder {
	constructor({maxSeconds = 120} = {}) { this.maxMs = maxSeconds * 1000; this.entries = []; }
	add(time, state, frames = {}) {
		this.entries.push({time, state, frames});
		while (this.entries.length && time - this.entries[0].time > this.maxMs) this.entries.shift();
	}
	duration() { return this.entries.length ? this.entries.at(-1).time - this.entries[0].time : 0; }
	at(offset) {
		if (!this.entries.length) return null;
		const target = this.entries[0].time + offset;
		let found = this.entries[0];
		for (const entry of this.entries) { if (entry.time <= target) found = entry; else break; }
		return found;
	}
	clear() { this.entries = []; }
}
