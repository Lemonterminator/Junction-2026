// Public source snapshots. Run intentionally with Node 22+; never stores tokens.
import { mkdir, writeFile } from 'node:fs/promises';
import { execFile, execFileSync } from 'node:child_process';
import { promisify } from 'node:util';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const destination = path.join(root, 'docs/2026/bronze/intel_open_edge_platform');
const now = new Date().toISOString();
const pendingWrites = [];
const hash = data => createHash('sha256').update(data).digest('hex');
const run = promisify(execFile);
async function get(url, json = false) {
  const response = await fetch(url, { headers: { 'User-Agent': 'Junction-2026-source-archive', Accept: 'application/vnd.github+json' } });
  if (!response.ok) throw new Error(`${response.status}: ${url}`);
  return json ? response.json() : response.text();
}
await mkdir(destination, { recursive: true });
const repositories = [];
const pages = [];
for (let page = 1; ; page++) {
  const url = `https://api.github.com/search/repositories?q=org%3Aopen-edge-platform&sort=stars&order=desc&per_page=100&page=${page}`;
  const result = await get(url, true);
  if (result.incomplete_results) throw new Error('GitHub returned incomplete results; retry before archiving.');
  pages.push({ url, total_count: result.total_count, count: result.items.length });
  repositories.push(...result.items.map(r => ({ name: r.name, full_name: r.full_name, url: r.html_url, description: r.description, stars: r.stargazers_count, forks: r.forks_count, default_branch: r.default_branch, archived: r.archived, pushed_at: r.pushed_at, license: r.license?.spdx_id ?? null })));
  if (repositories.length >= result.total_count) break;
  if (page >= 10 || !result.items.length) throw new Error('Search coverage limit reached.');
}
pendingWrites.push(['repositories.json', JSON.stringify({ retrieved_at: now, source_url: 'https://github.com/orgs/open-edge-platform/repositories?q=sort%3Astars', coverage: 'All public repositories returned by GitHub Search at retrieval time; no private repositories.', pages, repositories }, null, 2) + '\n']);
const selected = ['geti-instant-learn', 'manufacturing-ai-suite', 'edge-ai-sizing-tool', 'dlstreamer', 'scenescape', 'robotics-ai-suite'];
const sources = [];
for (const name of selected) {
  const repo = repositories.find(r => r.name === name);
  if (!repo) throw new Error(`Selected repository missing (possibly renamed): ${name}`);
  const remote = await run('git', ['ls-remote', `https://github.com/${repo.full_name}.git`, `refs/heads/${repo.default_branch}`]);
  const commit = remote.stdout.trim().split(/\s+/)[0];
  if (!/^[0-9a-f]{40}$/.test(commit)) throw new Error(`Cannot resolve ${repo.full_name}`);
  const url = `https://raw.githubusercontent.com/${repo.full_name}/${commit}/README.md`;
  const content = await get(url);
  const file = `repositories/${name}/README.md`;
  pendingWrites.push([file, content]);
  sources.push({ repository: repo.full_name, branch: repo.default_branch, commit, file, source_url: url, retrieved_at: now, sha256: hash(content) });
}
const upstreamDir = path.join(root, 'external/physical-ai-studio');
const commit = execFileSync('git', ['-C', upstreamDir, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
const content = execFileSync('git', ['-C', upstreamDir, 'show', 'HEAD:JUNCTION2026.md']);
pendingWrites.push(['JUNCTION2026.md', content]);
sources.unshift({ repository: 'open-edge-platform/physical-ai-studio', branch: 'junction2026', commit, file: 'JUNCTION2026.md', source_url: `https://github.com/open-edge-platform/physical-ai-studio/blob/${commit}/JUNCTION2026.md`, retrieved_at: now, sha256: hash(content) });
pendingWrites.push(['manifest.json', JSON.stringify({ retrieved_at: now, sources, organizer_message: { text: 'Check out the interesting repos here; Feel free to use any of them for an extra bit of creativity', attribution: 'Organizer message supplied by the user in this chat; independently unverified.', supplied_date: '2026-11-13' } }, null, 2) + '\n']);
// Do not overwrite a valid archive when any upstream retrieval fails.
for (const [file, data] of pendingWrites) {
  await mkdir(path.dirname(path.join(destination, file)), { recursive: true });
  await writeFile(path.join(destination, file), data);
}
console.log(`Archived ${repositories.length} public repositories and ${sources.length} pinned source documents.`);
