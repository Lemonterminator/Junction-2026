import test from 'node:test';
import assert from 'node:assert/strict';
import { LatestImageLoader } from '../image-loader.mjs';

class FakeImage extends EventTarget {
	hidden = true;
	assignments = [];
	_src = '';
	set src(value) { this._src = value; this.assignments.push(value); }
	get src() { return this._src; }
	removeAttribute(name) { if (name === 'src') this._src = ''; }
	finish(type = 'load') { this.dispatchEvent(new Event(type)); }
}

test('a slow image completes before the latest queued frame starts', () => {
	const image = new FakeImage();
	const loader = new LatestImageLoader(image);
	loader.setSource('/frame/1');
	loader.setSource('/frame/2');
	loader.setSource('/frame/3');
	assert.deepEqual(image.assignments, ['/frame/1']);
	image.finish();
	assert.deepEqual(image.assignments, ['/frame/1', '/frame/3']);
	assert.equal(image.hidden, false);
	image.finish();
	loader.setSource('/frame/3');
	assert.deepEqual(image.assignments, ['/frame/1', '/frame/3']);
});

test('a failed image reports the failure and continues to the latest queued frame', () => {
	const image = new FakeImage();
	const errors = [];
	const loader = new LatestImageLoader(image, url => errors.push(url));
	loader.setSource('/frame/1');
	loader.setSource('/frame/2');
	image.finish('error');
	assert.deepEqual(errors, ['/frame/1']);
	assert.deepEqual(image.assignments, ['/frame/1', '/frame/2']);
	assert.equal(image.hidden, true);
	image.finish();
	assert.equal(image.hidden, false);
});

test('reset removes the source and ignores late events without showing stale pending frames', () => {
	const image = new FakeImage();
	const errors = [];
	const loader = new LatestImageLoader(image, url => errors.push(url));
	loader.setSource('/frame/1');
	loader.setSource('/frame/2');
	loader.setSource(null);
	assert.equal(image.src, '');
	assert.equal(image.hidden, true);
	image.finish();
	image.finish('error');
	assert.equal(image.hidden, true);
	assert.deepEqual(image.assignments, ['/frame/1']);
	assert.deepEqual(errors, []);
	loader.setSource('/frame/3');
	image.finish();
	assert.equal(image.hidden, false);
});

test('the latest request for the in-flight frame cancels a superseded queued frame', () => {
	const image = new FakeImage();
	const loader = new LatestImageLoader(image);
	loader.setSource('/frame/1');
	loader.setSource('/frame/2');
	loader.setSource('/frame/1');
	image.finish();
	assert.deepEqual(image.assignments, ['/frame/1']);
});
