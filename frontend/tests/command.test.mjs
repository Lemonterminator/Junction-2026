import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCommand, ACTIONS } from '../command.mjs';

const action = text => parseCommand(text).action;

test('sorting requests inspect first and let the measured label choose the bowl', () => {
	for (const text of ['Sort this brick', 'Inspect it and put it where it belongs', 'next part please', 'check the part and sort it']) {
		assert.equal(action(text), 'INSPECT_AND_SORT', text);
	}
	assert.deepEqual(parseCommand('sort it').plan.map(step => step.key), ['capture', 'score', 'decide', 'act']);
});

test('an explicit bowl is a direct fixed task', () => {
	assert.equal(action('Put the brick in the green bowl'), 'SORT_GREEN');
	assert.equal(action('move it to the GOOD bin'), 'SORT_GREEN');
	assert.equal(action('reject this one'), 'SORT_PINK');
	assert.equal(action('place it in the pink bowl'), 'SORT_PINK');
	assert.equal(parseCommand('place it in the pink bowl').task, 'Pick up the brick and place it in the pink bowl.');
});

test('inspection only never moves the arm', () => {
	for (const text of ['Is this brick defective?', 'inspect', 'look at the part', 'scan it']) {
		const parsed = parseCommand(text);
		assert.equal(parsed.action, 'INSPECT', text);
		assert.equal(parsed.moves, false);
	}
});

test('stop wins over everything else', () => {
	assert.equal(action('stop'), 'STOP');
	assert.equal(action('STOP sorting into the green bowl'), 'STOP');
	assert.equal(action('emergency halt!'), 'STOP');
});

test('ambiguous, negated or unknown prompts are refused with a reason instead of guessed', () => {
	for (const text of ['put it in the green or the pink bowl', "don't sort it", 'do not move', 'make me a sandwich', '', '   ']) {
		const parsed = parseCommand(text);
		assert.equal(parsed.action, null, text);
		assert.equal(typeof parsed.reason, 'string');
		assert.ok(parsed.reason.length > 0);
	}
});

test('every recognised action is in the closed set and says whether it moves the arm', () => {
	assert.deepEqual(Object.keys(ACTIONS).sort(), ['INSPECT', 'INSPECT_AND_SORT', 'SORT_GREEN', 'SORT_PINK', 'STOP']);
	assert.equal(parseCommand('sort it').moves, true);
	assert.equal(parseCommand('stop').moves, false);
});
