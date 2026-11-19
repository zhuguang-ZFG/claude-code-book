// Exercise the pinned source's layer merge; path discovery and parsing are fixture adapters.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp, readFile, rm, writeFile} from 'node:fs/promises';
import {stripTypeScriptTypes} from 'node:module';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {runInNewContext} from 'node:vm';

if (!process.argv[2]) throw Error('Pass the Kimi 2.5.2 source checkout');
const path = join(process.argv[2], 'packages/agent-core-v2/src/app/mcpConfig/configLoader.ts');
const source = (await readFile(path, 'utf8')).replaceAll('\r\n', '\n');
const blob = createHash('sha1').update('blob ' + Buffer.byteLength(source) + '\0').update(source).digest('hex');
assert.equal(blob, '93879a95c8e0b83cb6153981cad969f321b6205b');
const js = stripTypeScriptTypes(source);
const start = js.indexOf('export async function loadMcpServersDetailed(');
const end = js.indexOf('\n}', start);
assert.ok(start >= 0 && end > start);
const body = js.slice(start + 'export '.length, end + 2);
const root = await mkdtemp(join(tmpdir(), 'kimi-book-mcp-'));
try {
    const paths = {user:join(root, 'user.json'), projectRoot:join(root, 'root.json'), project:join(root, 'project.json')};
    const merge = runInNewContext('(' + body + ')', {
        resolveMcpJsonPaths: async () => paths,
        dirname: () => root,
        readMcpJson: async (_fs, file) => JSON.parse(await readFile(file, 'utf8')).mcpServers,
    });
    const save = (file, servers) => writeFile(file, JSON.stringify({mcpServers:servers}));
    const user = {command:'python', args:['user.py']};
    const project = {command:'node', args:['project.mjs']};
    await save(paths.user, {rules:user});
    await save(paths.projectRoot, {});
    await save(paths.project, {});
    assert.equal((await merge({})).origins.rules, paths.user);
    await save(paths.project, {rules:project});
    const conflict = await merge({});
    assert.equal(conflict.origins.rules, paths.project);
    assert.deepEqual(conflict.servers.rules, project);
    await save(paths.project, {'project-rules':project});
    const fixed = await merge({});
    assert.deepEqual(fixed.servers.rules, user);
    assert.deepEqual(fixed.servers['project-rules'], project);
    assert.equal(fixed.origins.rules, paths.user);
    assert.equal(fixed.origins['project-rules'], paths.project);
    console.log('Kimi MCP: project shadowed rules; renaming kept both commands and their origins');
} finally {
    await rm(root, {recursive:true, force:true});
}
