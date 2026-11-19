// Use the installed package directory, never the user's session directory.
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, readFile, copyFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

if (!process.argv[2]) throw Error('Pass the pi-coding-agent 1.5.0 package directory');
const pkg = resolve(process.argv[2]);
assert.equal(JSON.parse(await readFile(join(pkg, 'package.json'), 'utf8')).version, '1.5.0');
const root = await mkdtemp(join(tmpdir(), 'pi-book-resume-'));
try {
    process.env.PI_CODING_AGENT_DIR = join(root, 'agent');
    const {SessionManager} = await import(pathToFileURL(join(pkg, 'dist/core/session-manager.js')));
    const sessions = join(root, 'sessions');
    await mkdir(sessions);
    const file = join(sessions, 'review.jsonl');
    const backup = join(root, 'before.jsonl');
    const header = {type:'session', version:3, id:'book-review', cwd:root, timestamp:new Date().toISOString()};
    await writeFile(file, JSON.stringify(header) + '\n');
    const first = SessionManager.open(file, sessions);
    const question = first.appendMessage({role:'user', content:'Check inventory', timestamp:1});
    await copyFile(file, backup);
    const recent = SessionManager.continueRecent(root, sessions);
    assert.equal(recent.getSessionId(), header.id);
    assert.equal(recent.getLeafId(), question);
    await writeFile(file, 'invalid session header\n');
    assert.throws(() => SessionManager.open(file, sessions), /not a valid/);
    assert.equal(await readFile(file, 'utf8'), 'invalid session header\n');
    await copyFile(backup, file);
    const recovered = SessionManager.open(file, sessions);
    const mark = recovered.appendCustomEntry('book:checkpoint', {step:'resumed'});
    const reloaded = SessionManager.open(file, sessions);
    assert.equal(reloaded.getSessionId(), header.id);
    assert.deepEqual(reloaded.getEntries().map(e => [e.id, e.parentId]), [[question, null], [mark, question]]);
    console.log('Pi 1.5.0: continued same session; invalid header rejected; restored 2 linked entries');

    const {loadExtensions} = await import(pathToFileURL(join(pkg, 'dist/core/extensions/loader.js')));
    const filePath = join(root, 'git-status.ts');
    await writeFile(filePath, 'export default {};\n');
    const failed = await loadExtensions([filePath], root);
    assert.equal(failed.extensions.length, 0);
    assert.match(failed.errors[0].error, /factory function/);
    await copyFile(new URL('./git-status.ts', import.meta.url), filePath);
    const loaded = await loadExtensions([filePath], root);
    assert.deepEqual(loaded.errors, []);
    assert.deepEqual([...loaded.extensions[0].tools.keys()], ['book_git_status']);
    console.log('Pi loader: rejected invalid factory; restored extension registered book_git_status');
} finally {
    await rm(root, {recursive:true, force:true});
}
