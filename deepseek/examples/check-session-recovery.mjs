// Load the real JSONL backend from an isolated npm installation.
import assert from 'node:assert/strict';
import {appendFile, mkdtemp, readFile, readdir, rm} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

if (!process.argv[2]) throw Error('Pass the npm installation prefix');
const loader = createRequire(join(resolve(process.argv[2]), 'package.json'));
const pkg = '@deepseek-ai/dsh-session-persistence-jsonl';
assert.equal(loader(pkg + '/package.json').version, '0.2.2-rc.1');
const load = name => import(pathToFileURL(loader.resolve(name)));
const {Context} = await load('@deepseek-ai/cordis');
const {SESSION_FORMAT_VERSION} = await load('@deepseek-ai/dsh-session');
const backend = await load(pkg);
const root = await mkdtemp(join(tmpdir(), 'book-dsh-session-'));
const id = 'book-review';
async function mount() {
    const ctx = new Context();
    await ctx.plugin(backend, {root, compression:'none'});
    return ctx;
}
async function readEvents(store) {
    const reader = await store.open(id, 'read');
    try {
        assert.equal(reader.header.id, id);
        return (await reader.read()).events;
    } finally {
        await reader.close();
    }
}
let ctx;
try {
    ctx = await mount();
    const writer = await ctx.sessionPersistence.create({version:SESSION_FORMAT_VERSION, id, createdAt:1000, isSeeded:false});
    const start = {type:'turn/start', seq:0, time:1, data:{turn:1}};
    await writer.append([start]);
    await writer.flush();
    await writer.close();
    await ctx.fiber.dispose();
    ctx = undefined;
    const files = (await readdir(root, {recursive:true})).filter(name => name.endsWith('.jsonl'));
    assert.equal(files.length, 1);
    const path = join(root, files[0]);
    const committed = await readFile(path);
    const tail = '{"type":"turn/end","seq":';
    await appendFile(path, tail);
    ctx = await mount();
    assert.deepEqual(await readEvents(ctx.sessionPersistence), [start]);
    assert.deepEqual(await readFile(path), Buffer.concat([committed, Buffer.from(tail)]));
    const resumed = await ctx.sessionPersistence.open(id, 'write');
    const end = {type:'turn/end', seq:1, time:2, data:{turn:1, reason:{kind:'interrupted'}}};
    await resumed.append([end]);
    await resumed.flush();
    await resumed.close();
    await ctx.fiber.dispose();
    ctx = await mount();
    assert.deepEqual(await readEvents(ctx.sessionPersistence), [start, end]);
    const repaired = await readFile(path);
    assert.deepEqual(repaired.subarray(0, committed.length), committed);
    assert.deepEqual(JSON.parse(repaired.subarray(committed.length).toString().trim()), end);
    console.log('JSONL: read preserved the torn tail; write repaired it; remount returned seq 0,1');
} finally {
    try { await ctx?.fiber.dispose(); }
    finally { await rm(root, {recursive:true, force:true}); }
}
