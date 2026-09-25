#!/usr/bin/env node
// 강의 준비 표시(CD-25) 모으기·지우기.
//   npm run prep:list            남은 표시를 파일:줄로 보여 준다(--check: 하나라도 있으면 exit 1, 개설 전 관문)
//   npm run prep:strip           표시를 모두 지운다(prep/ 폴더와 PrepNote 컴포넌트는 안내에 따라 따로 지운다)
// 표시 두 가지:
//   - MDX·Astro: <PrepNote ...>...</PrepNote> 블록(중첩 없음). 마지막 블록을 지우면 import 줄도 지운다.
//   - 강사 안내 .md: "## 강의 준비" 절(다음 "## " 제목 전까지).
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const DEFAULT_ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SCAN_DIRS = ['content', 'src/pages'];
const EXTENSIONS = ['.mdx', '.md', '.astro'];
const BLOCK_RE = /<PrepNote\b([^>]*)>[\s\S]*?<\/PrepNote>/g;
const IMPORT_RE = /^import PrepNote from [^\n]*\n/m;
const SECTION_HEADING = '## 강의 준비';

function attr(attrs, name) {
  const m = new RegExp(`${name}="([^"]*)"`).exec(attrs);
  return m ? m[1] : undefined;
}

function lineOf(text, index) {
  return text.slice(0, index).split('\n').length;
}

/** 강사 안내의 "## 강의 준비" 절 범위들 [start, end). */
function sectionRanges(text) {
  const ranges = [];
  const re = new RegExp(`^${SECTION_HEADING}[^\\n]*\\n?`, 'gm');
  let m;
  while ((m = re.exec(text)) !== null) {
    const bodyStart = m.index + m[0].length;
    const next = text.slice(bodyStart).search(/^## /m);
    ranges.push([m.index, next === -1 ? text.length : bodyStart + next]);
  }
  return ranges;
}

/** 파일 텍스트에서 표시를 찾는다. @returns {{file, line, title, guide?}[]} */
export function findPrepNotes(text, file) {
  const found = [];
  for (const m of text.matchAll(BLOCK_RE)) {
    found.push({ file, line: lineOf(text, m.index), title: attr(m[1], 'title') ?? '강의 준비', guide: attr(m[1], 'guide') });
  }
  if (file.endsWith('.md')) {
    for (const [start] of sectionRanges(text)) {
      found.push({ file, line: lineOf(text, start), title: '강의 준비' });
    }
  }
  return found;
}

/** 표시를 지운 텍스트. 줄바꿈 형식(LF/CRLF)은 그대로 둔다. */
export function stripPrepNotes(text, file) {
  const crlf = text.includes('\r\n');
  let out = crlf ? text.replace(/\r\n/g, '\n') : text;
  const before = out;
  out = out.replace(BLOCK_RE, '');
  if (file.endsWith('.md')) {
    for (const [start, end] of sectionRanges(out).reverse()) {
      out = out.slice(0, start) + out.slice(end);
    }
  }
  if (out !== before) {
    if (!out.includes('<PrepNote')) out = out.replace(IMPORT_RE, '');
    out = out.replace(/\n{3,}/g, '\n\n');
  }
  return crlf ? out.replace(/\n/g, '\r\n') : out;
}

function* walk(dir) {
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const name of entries) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) yield* walk(full);
    else if (EXTENSIONS.some((ext) => name.endsWith(ext))) yield full;
  }
}

function scan(root) {
  const files = [];
  for (const dir of SCAN_DIRS) for (const full of walk(join(root, dir))) files.push(full);
  return files;
}

/**
 * @param {string[]} argv
 * @param {{ root?: string, io?: { log: (s: string) => void, error: (s: string) => void } }} [options]
 * @returns {number} exit code
 */
export function run(argv, { root = DEFAULT_ROOT, io = console } = {}) {
  const [cmd, ...rest] = argv;
  const rel = (full) => relative(root, full).split('\\').join('/');
  if (cmd === 'list') {
    const all = scan(root).flatMap((full) => findPrepNotes(readFileSync(full, 'utf8'), rel(full)));
    for (const n of all) io.log(`${n.file}:${n.line}  ${n.title}${n.guide ? `  → ${n.guide}` : ''}`);
    io.log(`강의 준비 표시 ${all.length}건`);
    return rest.includes('--check') && all.length > 0 ? 1 : 0;
  }
  if (cmd === 'strip') {
    let changed = 0;
    for (const full of scan(root)) {
      const text = readFileSync(full, 'utf8');
      const out = stripPrepNotes(text, rel(full));
      if (out !== text) {
        writeFileSync(full, out, 'utf8');
        changed += 1;
        io.log(`지움: ${rel(full)}`);
      }
    }
    io.log(`${changed}개 파일에서 강의 준비 표시를 지웠습니다. prep/ 폴더와 src/components/PrepNote.astro는 prep/README.md의 안내대로 지우세요.`);
    return 0;
  }
  io.error('사용법: node scripts/prep_notes.mjs <list [--check] | strip>');
  return 2;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  process.exit(run(process.argv.slice(2)));
}
