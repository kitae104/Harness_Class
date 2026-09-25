import { mkdtempSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { createChecklistServer } from '../../prep/checklist-server.mjs';

const servers: { close: () => void }[] = [];
afterEach(() => {
  while (servers.length) servers.pop()?.close();
});

async function start() {
  const dir = mkdtempSync(join(tmpdir(), 'checklist-'));
  writeFileSync(join(dir, 'checklist.html'), '<title>준비표</title>', 'utf8');
  const server = createChecklistServer({ dir });
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  servers.push(server);
  const { port } = server.address() as { port: number };
  return { dir, base: `http://127.0.0.1:${port}` };
}

describe('checklist server', () => {
  it('serves the checklist page at /', async () => {
    const { base } = await start();
    const res = await fetch(`${base}/`);
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toContain('text/html');
    expect(await res.text()).toContain('준비표');
  });

  it('returns an empty progress object before anything is saved', async () => {
    const { base } = await start();
    const res = await fetch(`${base}/api/progress`);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({});
  });

  it('saves progress to checklist-progress.json and reads it back', async () => {
    const { base, dir } = await start();
    const body = { checked: { 's0-1': true }, notes: { s0: '메모' } };
    const put = await fetch(`${base}/api/progress`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
    expect(put.status).toBe(200);
    const saved = JSON.parse(readFileSync(join(dir, 'checklist-progress.json'), 'utf8'));
    expect(saved.checked).toEqual({ 's0-1': true });
    expect(saved.savedAt).toBeTypeOf('string');
    const res = await fetch(`${base}/api/progress`);
    expect((await res.json()).notes).toEqual({ s0: '메모' });
  });

  it('rejects invalid JSON without touching the file', async () => {
    const { base, dir } = await start();
    const res = await fetch(`${base}/api/progress`, { method: 'POST', body: '{broken' });
    expect(res.status).toBe(400);
    expect(existsSync(join(dir, 'checklist-progress.json'))).toBe(false);
  });

  it('does not serve other files', async () => {
    const { base } = await start();
    expect((await fetch(`${base}/../package.json`)).status).toBe(404);
    expect((await fetch(`${base}/checklist-server.mjs`)).status).toBe(404);
  });
});
