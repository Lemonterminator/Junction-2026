/** A captioned product story. Illustrations describe the concept, not measured results. */
export const STORY = [
	{key:'problem', audio:'assets/intro/problem.wav', label:'01 / THE PROBLEM', title:'Small defects. Expensive consequences.',
		caption:'Catch the problem before it becomes a return.', duration:10500,
		narration:'One small defect can mean a returned order, wasted material, and another inspection. Checking every part by hand takes time. For people doing repetitive work, it’s easy to miss something.'},
	{key:'inspect', audio:'assets/intro/inspect.wav', label:'02 / THE SOLUTION', title:'Give every part a second look.',
		caption:'See the part. Inspect it. Choose the next action.', duration:10000,
		narration:'Physic AI brings inspection and sorting into one cell. Cameras see the part. An anomaly model looks for defects. Then the system chooses the next action and asks the robot to sort it.'},
	{key:'human', audio:'assets/intro/human.wav', label:'03 / THE HUMAN', title:'When it’s unsure, people decide.',
		caption:'Good parts move on. Defects go aside. Uncertainty gets a human.', duration:9500,
		narration:'Good parts move on. Defective parts go aside. When the result is uncertain, sorting pauses for a person to take a second look. Your team keeps the judgment. The robot handles the repetition.'},
	{key:'edge', audio:'assets/intro/edge.wav', label:'04 / THE EDGE', title:'Intelligence, close to the work.',
		caption:'Designed for local Intel inference. Performance you can inspect.', duration:11000,
		narration:'The goal is practical automation on an Intel laptop, with inference close to the work. See measured inference time alongside processor and memory use. Start with one cell, measure the results, and build from there.'},
];

export class AudioNarrator {
	constructor(audio, onStatus = () => {}) {
		this.audio = audio; this.onStatus = onStatus; this.source = null; this.generation = 0;
	}
	stop() {
		this.generation++; this.audio.onended = null; this.audio.onerror = null; this.audio.pause();
	}
	rewind() { this.stop(); this.audio.currentTime = 0; this.source = null; }
	start(source, done, fallback) {
		this.stop();
		const generation = this.generation;
		if (source !== this.source) { this.audio.src = source; this.audio.currentTime = 0; this.source = source; }
		const failed = () => {
			if (generation !== this.generation) return;
			this.stop(); this.onStatus('Narration unavailable · playing captions'); fallback();
		};
		this.audio.onended = () => {if (generation === this.generation) done();};
		this.audio.onerror = failed;
		this.onStatus('Loading narration…');
		try {
			Promise.resolve(this.audio.play()).then(() => {
				if (generation === this.generation) this.onStatus('Narration playing · English');
			}).catch(failed);
		} catch { queueMicrotask(failed); }
		return true;
	}
}

export class IntroPlayer {
	constructor({onChange = () => {}, narrate = () => false, stopNarration = () => {},
		schedule = (fn, ms) => globalThis.setTimeout(fn, ms), cancel = id => globalThis.clearTimeout(id)} = {}) {
		Object.assign(this, {onChange, narrate, stopNarration, schedule, cancel});
		this.index = 0; this.playing = false; this.finished = false; this.generation = 0; this.timer = null;
	}
	pause() {
		this.playing = false; this.generation++;
		this.cancel(this.timer); this.timer = null; this.stopNarration(); this.onChange(this);
	}
	seek(index) {
		const wasPlaying = this.playing;
		this.pause(); this.index = Math.max(0, Math.min(STORY.length-1, index)); this.finished = false;
		if (wasPlaying) this.play(); else this.onChange(this);
	}
	play() {
		this.pause();
		if (this.finished) {this.index = 0; this.finished = false;}
		this.playing = true;
		const generation = this.generation;
		const done = () => {
			if (!this.playing || generation !== this.generation) return;
			this.cancel(this.timer); this.timer = null;
			if (this.index === STORY.length-1) {
				this.pause(); this.finished = true; this.onChange(this); return;
			}
			this.index++; this.play();
		};
		const chapter = STORY[this.index];
		const fallback = () => {
			if (!this.playing || generation !== this.generation) return;
			this.cancel(this.timer);
			this.timer = this.schedule(done, chapter.duration);
		};
		const voiced = this.narrate(chapter.narration, done, fallback);
		// A watchdog also advances if the media service loses its completion event.
		this.timer = this.schedule(done, voiced ? Math.max(25000, chapter.duration * 2) : chapter.duration);
		this.onChange(this);
	}
}

export function mountIntro(doc = document) {
	const $ = id => doc.getElementById(id);
	const dialog = $('intro-dialog');
	const narrator = new AudioNarrator($('intro-audio'), message => { $('intro-audio-status').textContent = message; });
	const player = new IntroPlayer({
		narrate(text, done, fallback) {
			if (!$('intro-narration').checked) {
				$('intro-audio-status').textContent = 'Narration off · playing captions'; return false;
			}
			return narrator.start(STORY[player.index].audio, done, fallback);
		},
		stopNarration: () => narrator.stop(),
		onChange(p) {
			const chapter = STORY[p.index];
			dialog.dataset.chapter = chapter.key;
			dialog.classList.toggle('intro-playing', p.playing);
			$('intro-label').textContent = chapter.label;
			$('intro-title').textContent = chapter.title;
			$('intro-caption').textContent = chapter.caption;
			$('intro-transcript').textContent = chapter.narration;
			$('intro-play').textContent = p.playing ? 'Pause' : p.finished ? 'Replay intro' : 'Play intro';
			if (!p.playing) $('intro-audio-status').textContent = p.finished ? 'Intro complete' : 'Press Play to begin or resume';
			doc.querySelectorAll('[data-chapter-index]').forEach((button, i) => {
				button.setAttribute('aria-current', i === p.index ? 'step' : 'false');
				button.classList.toggle('selected', i === p.index);
			});
		},
	});
	$('watch-intro').addEventListener('click', () => {dialog.showModal(); player.pause(); narrator.rewind(); player.seek(0);});
	$('intro-play').addEventListener('click', () => player.playing ? player.pause() : player.play());
	$('intro-close').addEventListener('click', () => dialog.close());
	$('intro-enter').addEventListener('click', () => dialog.close());
	dialog.addEventListener('close', () => player.pause());
	dialog.addEventListener('cancel', () => player.pause());
	$('intro-narration').addEventListener('change', () => {narrator.rewind(); if (player.playing) player.play();});
	doc.querySelectorAll('[data-chapter-index]').forEach(button => button.addEventListener('click', () => {narrator.rewind(); player.seek(Number(button.dataset.chapterIndex));}));
	player.onChange(player);
}
