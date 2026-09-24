#!/usr/bin/env node
// npm run build:offline — dist/를 file://에서 열 수 있는 dist-offline/과 dist-offline.zip으로 만든다(CD-05).
// 사이트 루트 기준 링크(href="/...", src="/...")를 각 HTML 파일 위치 기준 상대경로로 바꾸고,
// 디렉터리 링크는 index.html로 끝나게 한다(file://은 디렉터리 인덱스를 열지 않는다).
// 외부 URL을 불러오는 script·stylesheet·img가 있으면 실패한다(ADR-008). OS 명령에 의존하지 않는다.
import { cpSync, existsSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { join, posix, relative } from 'node:path';
import { pathToFileURL } from 'node:url';
import { zipSync } from 'fflate';

/**
 * 사이트 루트 기준 경로를 fromFile(출력 폴더 기준 상대 파일 경로) 위치에서 본 상대경로로 바꾼다.
 * @param {string} fromFile 예: 'course/day1/01/index.html' (Windows 구분자도 허용)
 * @param {string} rootPath 예: '/course/day1/02/', '/_astro/a.css#x'
 */
export function toRelative(fromFile, rootPath) {
  const cut = rootPath.search(/[?#]/);
  let target = cut === -1 ? rootPath : rootPath.slice(0, cut);
  const suffix = cut === -1 ? '' : rootPath.slice(cut);
  if (target.endsWith('/')) {
    target += 'index.html';
  } else if (!posix.basename(target).includes('.')) {
    target += '/index.html';
  }
  const fromDir = posix.dirname(fromFile.replace(/\\/g, '/'));
  const rel = posix.relative(posix.join('/', fromDir), posix.join('/', target));
  return rel + suffix;
}

const ROOT_LINK = /(\s(?:href|src)=)(["'])(\/(?!\/)[^"']*)\2/g;

/** HTML 안의 사이트 루트 기준 href·src를 파일 위치 기준 상대경로로 바꾼다. */
export function rewriteHtml(html, fromFile) {
  return html.replace(
    ROOT_LINK,
    (_match, attr, quote, path) => `${attr}${quote}${toRelative(fromFile, path)}${quote}`,
  );
}

const TAG = /<(script|link|img)\b[^>]*>/gi;
const EXTERNAL = /^(?:https?:)?\/\//i;

function attribute(tag, name) {
  const match = tag.match(new RegExp(`\\s${name}=(["'])([^"']*)\\1`, 'i'));
  return match ? match[2] : null;
}

/** 외부 URL을 불러오는 <script src>, <link rel="stylesheet">, <img src>의 URL 목록. */
export function findExternalAssets(html) {
  const found = [];
  for (const [tag, name] of html.matchAll(TAG)) {
    const kind = name.toLowerCase();
    let url = null;
    if (kind === 'link') {
      const rel = (attribute(tag, 'rel') || '').toLowerCase().split(/\s+/);
      if (rel.includes('stylesheet')) url = attribute(tag, 'href');
    } else {
      url = attribute(tag, 'src');
    }
    if (url && EXTERNAL.test(url)) found.push(url);
  }
  return found;
}

function listFiles(dir) {
  return readdirSync(dir, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => relative(dir, join(entry.parentPath, entry.name)).replace(/\\/g, '/'));
}

/**
 * distDir를 outDir로 복사해 HTML 링크를 바꾸고 zipPath에 압축한다.
 * @returns {{ pages: number, files: number, errors: string[] }}
 */
export function buildOffline({ distDir, outDir, zipPath }) {
  if (!existsSync(join(distDir, 'index.html'))) {
    return { pages: 0, files: 0, errors: [`${distDir}/index.html이 없습니다. 먼저 npm run build를 실행하세요.`] };
  }
  rmSync(outDir, { recursive: true, force: true });
  rmSync(zipPath, { force: true });
  cpSync(distDir, outDir, { recursive: true });

  const errors = [];
  const entries = {};
  let pages = 0;
  const files = listFiles(outDir);
  for (const file of files) {
    const full = join(outDir, file);
    if (file.endsWith('.html')) {
      const html = readFileSync(full, 'utf8');
      for (const url of findExternalAssets(html)) errors.push(`${file}: 외부 자원 ${url}`);
      const rewritten = rewriteHtml(html, file);
      writeFileSync(full, rewritten, 'utf8');
      pages += 1;
    }
    entries[file] = new Uint8Array(readFileSync(full));
  }
  if (errors.length === 0) writeFileSync(zipPath, zipSync(entries, { level: 9 }));
  return { pages, files: files.length, errors };
}

function main() {
  const result = buildOffline({ distDir: 'dist', outDir: 'dist-offline', zipPath: 'dist-offline.zip' });
  if (result.errors.length > 0) {
    for (const error of result.errors) console.error(`[build:offline] ${error}`);
    console.error('[build:offline] 실패: 오프라인 번들은 외부 CDN·웹폰트·외부 이미지를 쓸 수 없습니다(ADR-008).');
    process.exit(1);
  }
  console.log(
    `[build:offline] dist-offline/ (HTML ${result.pages}개, 파일 ${result.files}개) + dist-offline.zip`,
  );
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
