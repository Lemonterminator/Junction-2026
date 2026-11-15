/** Rebuild the fixed English narration on macOS using the story as its transcript. */
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { STORY } from '../frontend/intro.mjs';

if (process.platform !== 'darwin') throw new Error('Rebuilding narration requires macOS; playback works on every supported platform.');
const frontend = fileURLToPath(new URL('../frontend/', import.meta.url));
const temporary = mkdtempSync(join(tmpdir(), 'physicai-narration-'));
try {
	for (const chapter of STORY) {
		const intermediate = join(temporary, chapter.key + '.aiff');
		const output = join(frontend, chapter.audio);
		mkdirSync(dirname(output), {recursive:true});
		execFileSync('/usr/bin/say', ['-v','Samantha','-r','168','-o',intermediate,chapter.narration]);
		execFileSync('/usr/bin/afconvert', ['-f','WAVE','-d','LEI16',intermediate,output]);
	}
} finally { rmSync(temporary, {recursive:true, force:true}); }
