/** Measured resources and inference timings have independent provenance. */
const optionalNumber = (v, max = Infinity) => v === null || (Number.isFinite(v) && v >= 0 && v <= max);
export function validateSystem(s) {
	return Boolean(s && s.schema_version === 1 && (s.source === 'linux-proc-sysfs'
		|| (s.source === 'psutil' && ['Darwin','Windows','FreeBSD','OpenBSD','NetBSD','SunOS','AIX'].includes(s.platform)))
		&& Number.isFinite(s.timestamp) && optionalNumber(s.interval_ms)
		&& (s.cpu_model === null || typeof s.cpu_model === 'string')
		&& Number.isInteger(s.logical_cpus) && s.logical_cpus >= 0 && typeof s.gpu_scope === 'string'
		&& ['cpu_percent','memory_percent','gpu_percent','npu_percent'].every(k => optionalNumber(s[k], 100))
		&& ['memory_used_bytes','memory_total_bytes','package_power_w'].every(k => optionalNumber(s[k])));
}

export class ResourceHistory {
	constructor(limit = 60) { this.limit = limit; this.samples = []; }
	add(sample) {
		if (!validateSystem(sample) || sample.timestamp <= (this.samples.at(-1)?.timestamp ?? -Infinity)) return false;
		this.samples.push(structuredClone(sample));
		if (this.samples.length > this.limit) this.samples.shift();
		return true;
	}
	view(now = Date.now()) {
		const latest = this.samples.at(-1);
		const stale = !latest || now - latest.timestamp > 3500 || latest.timestamp - now > 3500;
		return { ...latest, stale, ...Object.fromEntries(['cpu_percent','memory_percent','gpu_percent','npu_percent','package_power_w']
			.map(k => [k, stale ? null : latest[k]])) };
	}
}

export class InferenceWindow {
	constructor(limit = 60) { this.limit = limit; this.values = new Map(); this.mode = null; this.device = null; }
	add(s) {
		const value = s.timings_ms?.inference;
		if (s.mode === 'demo' || s.stage !== 'complete' || !Number.isFinite(value) || value < 0) return;
		if (s.mode !== this.mode || s.device !== this.device) {
			this.values.clear(); this.mode = s.mode; this.device = s.device;
		}
		this.values.set(s.episode_id, value);
		if (this.values.size > this.limit) this.values.delete(this.values.keys().next().value);
	}
	summary() {
		const values = [...this.values.values()], sorted = [...values].sort((a,b) => a-b);
		const quantile = q => sorted[Math.ceil(sorted.length*q)-1] ?? null;
		return {count:sorted.length, median:quantile(.5), p95:quantile(.95), latest:values.at(-1) ?? null, mode:this.mode, device:this.device};
	}
}

export function mountPerformance(browser = window, doc = document) {
	const history = new ResourceHistory();
	const $ = id => doc.getElementById(id);
	let failure = null;
	function render() {
		const view = history.view();
		const hasCounters = Boolean(view.cpu_model || view.memory_total_bytes || view.gpu_percent !== null || view.npu_percent !== null);
		const platform = view.platform === 'Darwin' ? 'macOS' : view.platform ?? 'Linux';
		$('resource-status').textContent = view.stale ? (failure ?? 'Monitor data stale') : hasCounters ? 'Live host counters' : 'Host counters unavailable';
		$('resource-status').classList.toggle('resource-live', !view.stale && hasCounters);
		if (!view.stale) $('resource-host').textContent = `${platform} · ${view.cpu_model ?? 'Processor'} · ${view.logical_cpus} logical cores · dashboard server host`;
		for (const card of doc.querySelectorAll('[data-resource]')) {
			const key = `${card.dataset.resource}_percent`, value = view[key];
			if (['gpu','npu'].includes(card.dataset.resource)) {
				const linux = view.source === 'linux-proc-sysfs';
				card.querySelector('h3').textContent = `${linux ? 'Intel ' : ''}${card.dataset.resource.toUpperCase()}`;
				card.querySelector('p').textContent = linux ? (card.dataset.resource === 'gpu' ? 'Visible clients · busiest engine' : 'Device job activity') : `Counter unavailable${view.platform ? ' on ' + platform : ''}`;
			}
			card.querySelector('strong').textContent = value === null ? '—' : `${value.toFixed(1)}%`;
			card.classList.toggle('unavailable', value === null);
			const samples = history.samples;
			let drawing = false;
			const segments = view.stale ? [] : samples.map((s,i) => {
				if (s[key] === null) {drawing = false; return '';}
				const x = 280 * (60 - samples.length + i) / 59;
				const path = `${drawing ? 'L' : 'M'}${x.toFixed(1)} ${(58 - s[key]*.56).toFixed(1)}`;
				drawing = true; return path;
			});
			card.querySelector('path').setAttribute('d', segments.join(' '));
			card.querySelector('svg').setAttribute('aria-label', `${card.dataset.resource} history, ${value === null ? 'unavailable' : value.toFixed(1) + ' percent currently'}`);
		}
		$('resource-memory').textContent = !view.stale && view.memory_total_bytes
			? `${(view.memory_used_bytes/2**30).toFixed(1)} / ${(view.memory_total_bytes/2**30).toFixed(1)} GiB used` : 'Used / total RAM · unavailable';
		$('resource-power').textContent = `CPU package power: ${view.package_power_w === null ? '—' : view.package_power_w.toFixed(1) + ' W'}`;
		$('resource-note').textContent = 'Host resources include other workloads; GPU coverage depends on readable process counters. Missing or restricted counters stay empty. Model device and latency come from sorting telemetry.';
	}
	async function pollSystem() {
		try {
			const response = await browser.fetch('/api/system', {cache:'no-store', signal:AbortSignal.timeout(2500)});
			if (!response.ok || !history.add(await response.json())) throw new Error('Unavailable');
			failure = null;
		} catch {failure = 'Monitor unavailable';}
		render();
		browser.setTimeout(pollSystem, 1000);
	}
	async function pollSorting() {
		try {
			const response = await browser.fetch('/api/telemetry', {cache:'no-store', signal:AbortSignal.timeout(2500)});
			if (response.ok && response.status !== 204) {
				browser.dispatchEvent(new CustomEvent('sorter:telemetry', {detail:await response.json()}));
			}
		} catch { /* The sorting display retains its last snapshot and marks it stale. */ }
		browser.setTimeout(pollSorting, 1000);
	}
	pollSystem(); pollSorting();
}
