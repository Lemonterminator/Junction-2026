/**
 * Turn an operator's typed prompt into one action from a closed set. Nothing outside the set reaches the robot:
 * sorting runs one of the fixed task texts the policy was trained on, and the server checks the action again.
 * Unclear prompts are refused with a reason rather than guessed.
 */
export const TASKS = {
	green: 'Pick up the brick and place it in the green bowl.',
	pink: 'Pick up the brick and place it in the pink bowl.',
};

export const ACTIONS = {
	INSPECT_AND_SORT: {moves: true, title: 'Inspect, then sort', summary: 'Score the brick, then let the measured result choose the bowl. An uncertain result waits for a person.'},
	SORT_GREEN: {moves: true, title: 'Sort to the green plate', summary: 'Run the fixed green-bowl task without inspecting first.'},
	SORT_PINK: {moves: true, title: 'Sort to the pink plate', summary: 'Run the fixed pink-bowl task without inspecting first.'},
	INSPECT: {moves: false, title: 'Inspect only', summary: 'Score the brick and show the decision. The arm stays still.'},
	STOP: {moves: false, title: 'Stop', summary: 'Hold the arm where it is and end the run.'},
};

const PLANS = {
	INSPECT_AND_SORT: [['capture', 'Take a picture'], ['score', 'Score it'], ['decide', 'Decide'], ['act', 'Sort it, or wait for a person']],
	SORT_GREEN: [['act', 'Put it on the green plate']],
	SORT_PINK: [['act', 'Put it on the pink plate']],
	INSPECT: [['capture', 'Take a picture'], ['score', 'Score it'], ['decide', 'Decide']],
	STOP: [['hold', 'Hold the arm still']],
};

const has = (text, words) => words.some(word => new RegExp(`\\b${word}\\b`).test(text));
const GREEN = ['green', 'good', 'pass', 'passed', 'perfect', 'ok', 'okay', 'accept'];
const PINK = ['pink', 'defect', 'defective', 'reject', 'bad', 'faulty', 'broken', 'damaged'];
const PLACE = ['put', 'place', 'move', 'drop', 'sort', 'send', 'reject', 'accept', 'pass'];
const SORT = ['sort', 'next', 'handle', 'process', 'belongs', 'pick', 'deal', 'run', 'go', 'start'];
const INSPECT = ['inspect', 'check', 'look', 'scan', 'score', 'examine', 'is', 'defective', 'see'];

function result(action, reason = null) {
	if (!action) return {action: null, moves: false, reason, plan: [], task: null};
	const task = action === 'SORT_GREEN' ? TASKS.green : action === 'SORT_PINK' ? TASKS.pink : null;
	return {action, moves: ACTIONS[action].moves, reason, task, title: ACTIONS[action].title,
		plan: PLANS[action].map(([key, text]) => ({key, text}))};
}

export function parseCommand(input) {
	const text = String(input ?? '').toLowerCase().replace(/[^a-z' ]+/g, ' ').replace(/\s+/g, ' ').trim();
	if (!text) return result(null, 'Type what Armigo should do, for example “sort this brick”.');
	if (has(text, ['stop', 'halt', 'freeze', 'abort', 'emergency', 'pause'])) return result('STOP');
	if (/\b(don't|dont|do not|never|without moving)\b/.test(text)) {
		return result(null, 'That sounds like a “don’t”. Say what Armigo should do, or say “stop”.');
	}
	const green = has(text, GREEN), pink = has(text, PINK) && !/\bis (it|this|the)\b.*\bdefective\b/.test(text);
	const asksQuestion = /^(is|does|are|what|how)\b/.test(text) || /\?/.test(String(input));
	if (green && pink) return result(null, 'Both bowls were mentioned. Name one bowl, or say “sort it” to let inspection decide.');
	if ((green || pink) && has(text, PLACE) && !asksQuestion) return result(green ? 'SORT_GREEN' : 'SORT_PINK');
	if (has(text, SORT) || /\bwhere it belongs\b/.test(text)) return result('INSPECT_AND_SORT');
	if (has(text, INSPECT) || asksQuestion) return result('INSPECT');
	return result(null, 'Armigo only sorts bricks. Try “sort this brick”, “inspect it”, “put it in the green bowl” or “stop”.');
}
