import test from 'node:test';
import assert from 'node:assert/strict';
import { validateSystem, ResourceHistory, InferenceWindow } from '../performance.mjs';
import { createDemo } from '../telemetry.mjs';

const sample = (timestamp = 1000) => ({ schema_version: 1, timestamp, interval_ms: 1000,
	cpu_model: 'Test CPU', logical_cpus: 2, cpu_percent: 30, memory_percent: 25,
	memory_used_bytes: 1024, memory_total_bytes: 4096, gpu_percent: null, npu_percent: null,
	package_power_w: null, gpu_scope: 'Intel DRM visible clients · busiest engine', source: 'linux-proc-sysfs' });

test('system data rejects invalid percentages, times, sources and nonfinite measurements', () => {
	assert.equal(validateSystem(sample()), true);
	for (const patch of [{cpu_percent: 101}, {gpu_percent: -1}, {memory_percent: NaN}, {timestamp: null},
		{package_power_w: Infinity}, {source:'demo'}, {memory_total_bytes: -1}, {interval_ms:-1}]) {
		assert.equal(validateSystem({...sample(), ...patch}), false);
	}
});

test('native macOS and Windows snapshots are accepted without fabricated accelerator data', () => {
	for (const platform of ['Darwin','Windows']) {
		assert.equal(validateSystem({...sample(), source:'psutil', platform}), true);
	}
	assert.equal(validateSystem({...sample(), source:'psutil', platform:'demo'}), false);
});

test('resource history bounds samples, rejects repeats, and clears live values when stale', () => {
	const history = new ResourceHistory(2);
	history.add(sample()); history.add(sample()); history.add(sample(2000)); history.add(sample(3000));
	assert.equal(history.samples.length, 2);
	assert.equal(history.view(3001).cpu_percent, 30);
	assert.equal(history.view(9000).cpu_percent, null);
	assert.equal(history.view(9000).stale, true);
	assert.equal(history.add({...sample(4000), npu_percent: 999}), false);
});

test('inference statistics count measured completed episodes once and separate provenance and devices', () => {
	const window = new InferenceWindow();
	const base = {...createDemo(), mode:'real', stage:'complete', device:'OpenVINO GPU', timestamp:1000};
	window.add({...base, timings_ms:{capture:null,inference:999,placement:null}, mode:'demo'});
	assert.equal(window.summary().count, 0);
	for (let i = 1; i <= 20; i++) {
		const s = {...base, episode_id:String(i), timings_ms:{capture:null,inference:i,placement:null}};
		window.add(s); window.add({...s, timestamp:2000});
	}
	assert.deepEqual(window.summary(), {count:20, median:10, p95:19, latest:20, mode:'real', device:'OpenVINO GPU'});
	window.add({...base, mode:'twin', episode_id:'new', timings_ms:{inference:2}});
	assert.equal(window.summary().count, 1);
	assert.equal(window.summary().mode, 'twin');
});
