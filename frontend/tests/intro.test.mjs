import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { STORY, IntroPlayer, AudioNarrator } from '../intro.mjs';

test('default playback calls browser timers with the browser receiver', t => {
	t.mock.method(globalThis, 'setTimeout', function () {
		assert.equal(this, globalThis, 'Illegal invocation: setTimeout receiver'); return 42;
	});
	t.mock.method(globalThis, 'clearTimeout', function () {
		assert.equal(this, globalThis, 'Illegal invocation: clearTimeout receiver');
	});
	const player = new IntroPlayer();
	player.play();
	assert.equal(player.playing, true);
	player.pause();
});

test('story explains the business problem, local solution and human review without claimed ROI', () => {
	assert.equal(STORY.length, 4);
	assert.match(STORY.map(s => s.narration).join(' '), /manual|people/i);
	assert.match(STORY.map(s => s.narration).join(' '), /human|person/i);
	assert.ok(STORY.every(s => s.duration > 0 && s.title && s.narration));
});

test('intro advances with narration and cancels stale callbacks when closed or paused', () => {
	const callbacks = [], pending = new Map();
	let stops = 0;
	const player = new IntroPlayer({narrate: (text, done) => {callbacks.push(done); return true;},
		stopNarration: () => stops++, schedule: (fn) => {pending.set(fn, fn); return fn;}, cancel: id => pending.delete(id)});
	player.play();
	assert.equal(player.index, 0);
	callbacks[0]();
	assert.equal(player.index, 1);
	player.pause();
	callbacks[1]();
	assert.equal(player.index, 1);
	assert.equal(player.playing, false);
	player.seek(3); player.play(); callbacks.at(-1)();
	assert.equal(player.playing, false);
	assert.equal(player.finished, true);
	assert.ok(stops > 0);
	assert.equal(pending.size, 0);
});

test('silent playback uses chapter durations', () => {
	let due;
	const player = new IntroPlayer({schedule: (fn, ms) => {due = {fn,ms}; return 1;}, cancel: () => {}});
	player.play();
	assert.equal(due.ms, STORY[0].duration);
	due.fn();
	assert.equal(player.index, 1);
});

test('speech failure keeps captions on the current chapter for silent playback', () => {
	let fail, due;
	const player = new IntroPlayer({narrate: (text, done, fallback) => {fail = fallback; return true;},
		schedule: (fn, ms) => {due = {fn,ms}; return 1;}, cancel: () => {}});
	player.play(); fail();
	assert.equal(player.index, 0);
	assert.equal(due.ms, STORY[0].duration);
	due.fn();
	assert.equal(player.index, 1);
});

test('each chapter has bundled PCM narration, with no browser voice dependency', () => {
	for (const chapter of STORY) {
		const data = readFileSync(new URL('../' + chapter.audio, import.meta.url));
		assert.equal(data.toString('ascii', 0, 4), 'RIFF');
		assert.equal(data.toString('ascii', 8, 12), 'WAVE');
		assert.ok(data.length > 10000);
	}
});

function fakeAudio(play = () => Promise.resolve()) {
	return {src:'', currentTime:0, onended:null, onerror:null, pauses:0, play, pause() {this.pauses++;}};
}

test('fixed narration resumes paused audio, rewinds navigation and ends the current chapter', async () => {
	const audio = fakeAudio();
	const narrator = new AudioNarrator(audio);
	let ended = 0;
	narrator.start('assets/intro/problem.wav', () => ended++, () => assert.fail('Playback failed'));
	await Promise.resolve();
	audio.currentTime = 4;
	const lateEnd = audio.onended;
	narrator.stop(); lateEnd();
	assert.equal(ended, 0);
	narrator.start('assets/intro/problem.wav', () => ended++, () => {});
	assert.equal(audio.currentTime, 4);
	audio.onended();
	assert.equal(ended, 1);
	narrator.rewind();
	assert.equal(audio.currentTime, 0);
	narrator.start('assets/intro/inspect.wav', () => {}, () => {});
	assert.equal(audio.src, 'assets/intro/inspect.wav');
});

test('audio permission failures fall back and cancelled play promises cannot advance chapters', async () => {
	let reject;
	const audio = fakeAudio(() => new Promise((resolve, fail) => {reject = fail;}));
	const narrator = new AudioNarrator(audio);
	let failures = 0;
	narrator.start('problem.wav', () => assert.fail('Unexpected end'), () => failures++);
	reject(new Error('NotAllowedError'));
	await new Promise(resolve => setImmediate(resolve));
	assert.equal(failures, 1);
	narrator.start('inspect.wav', () => {}, () => failures++);
	narrator.stop(); reject(new Error('AbortError'));
	await new Promise(resolve => setImmediate(resolve));
	assert.equal(failures, 1);
});
