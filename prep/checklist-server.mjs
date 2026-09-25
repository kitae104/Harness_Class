#!/usr/bin/env node
// 강의 준비표 로컬 서버(개설 전 삭제, CD-25).
//   npm run prep:checklist   → http://127.0.0.1:4380 에서 prep/checklist.html을 연다.
// 체크 상태와 메모는 prep/checklist-progress.json에 저장한다(.gitignore 대상, 강사 개인 기록).
// 이 컴퓨터(127.0.0.1)에서만 접속된다. 준비표 페이지와 진행 파일 외에는 아무것도 내보내지 않는다.
import { createServer } from 'node:http';
import { existsSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const MAX_BODY = 1024 * 1024; // 1MB — 메모가 길어도 충분하다

function send(res, status, type, body) {
  res.writeHead(status, { 'content-type': type, 'cache-control': 'no-store' });
  res.end(body);
}

/**
 * @param {{ dir?: string }} [options] 준비표 HTML과 진행 파일이 있는 폴더(기본: prep/)
 */
export function createChecklistServer({ dir = HERE } = {}) {
  const page = join(dir, 'checklist.html');
  const progress = join(dir, 'checklist-progress.json');
  return createServer((req, res) => {
    const url = new URL(req.url ?? '/', 'http://localhost');
    if (req.method === 'GET' && (url.pathname === '/' || url.pathname === '/checklist.html')) {
      return send(res, 200, 'text/html; charset=utf-8', readFileSync(page));
    }
    if (url.pathname === '/api/progress' && req.method === 'GET') {
      const text = existsSync(progress) ? readFileSync(progress, 'utf8') : '{}';
      return send(res, 200, 'application/json; charset=utf-8', text);
    }
    if (url.pathname === '/api/progress' && req.method === 'POST') {
      let size = 0;
      const chunks = [];
      req.on('data', (c) => {
        size += c.length;
        if (size > MAX_BODY) req.destroy();
        else chunks.push(c);
      });
      req.on('end', () => {
        let data;
        try {
          data = JSON.parse(Buffer.concat(chunks).toString('utf8'));
          if (typeof data !== 'object' || data === null || Array.isArray(data)) throw new Error('객체가 아닙니다');
        } catch {
          return send(res, 400, 'application/json; charset=utf-8', '{"error":"JSON 객체가 아닙니다"}');
        }
        data.savedAt = new Date().toISOString();
        const tmp = `${progress}.tmp`;
        writeFileSync(tmp, JSON.stringify(data, null, 2) + '\n', 'utf8');
        renameSync(tmp, progress); // 쓰다 멈춰도 기존 파일이 깨지지 않게
        return send(res, 200, 'application/json; charset=utf-8', JSON.stringify({ savedAt: data.savedAt }));
      });
      return undefined;
    }
    return send(res, 404, 'text/plain; charset=utf-8', 'not found');
  });
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  const port = Number(process.env.PREP_CHECKLIST_PORT || 4380);
  createChecklistServer().listen(port, '127.0.0.1', () => {
    console.log(`강의 준비표: http://127.0.0.1:${port}  (진행 기록: prep/checklist-progress.json, 끝내려면 Ctrl+C)`);
  });
}
