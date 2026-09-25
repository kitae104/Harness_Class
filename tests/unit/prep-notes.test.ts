import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { findPrepNotes, run, stripPrepNotes } from '../../scripts/prep_notes.mjs';

const MDX = [
  '---',
  'lesson_id: d2-forms',
  '---',
  "import Callout from '../../src/components/Callout.astro';",
  "import PrepNote from '../../src/components/PrepNote.astro';",
  '',
  '## 강사 시연',
  '',
  '<PrepNote title="공용 폼 만들기" guide="prep/google-forms.md">',
  '',
  '강사 공용 폼을 만들고 링크를 등록합니다.',
  '',
  '</PrepNote>',
  '',
  '본문은 그대로 남습니다.',
  '',
  '<PrepNote title="캡처">메뉴 캡처를 넣습니다.</PrepNote>',
  '',
  '끝.',
  '',
].join('\n');

const MD = [
  '# 강사 안내 — Day 2 · 1교시',
  '',
  '## 준비',
  '- 폼을 미리 연다.',
  '',
  '## 강의 준비',
  '- 공용 폼을 만든다(prep/google-forms.md).',
  '- 링크를 등록한다.',
  '',
  '## 시연 순서',
  '1. 시작한다.',
  '',
].join('\n');

describe('findPrepNotes', () => {
  it('finds PrepNote blocks in MDX with line and title', () => {
    const found = findPrepNotes(MDX, 'content/day2/01.mdx');
    expect(found).toHaveLength(2);
    expect(found[0]).toMatchObject({ file: 'content/day2/01.mdx', line: 9, title: '공용 폼 만들기', guide: 'prep/google-forms.md' });
    expect(found[1]).toMatchObject({ line: 17, title: '캡처' });
  });

  it('finds the 강의 준비 section in instructor notes', () => {
    const found = findPrepNotes(MD, 'content/instructor/day2/01.md');
    expect(found).toHaveLength(1);
    expect(found[0]).toMatchObject({ line: 6, title: '강의 준비' });
  });

  it('returns nothing for text without markers', () => {
    expect(findPrepNotes('# 제목\n본문\n', 'a.md')).toEqual([]);
  });
});

describe('stripPrepNotes', () => {
  it('removes PrepNote blocks and the now-unused import from MDX', () => {
    const out = stripPrepNotes(MDX, 'content/day2/01.mdx');
    expect(out).not.toContain('PrepNote');
    expect(out).toContain("import Callout from '../../src/components/Callout.astro';");
    expect(out).toContain('본문은 그대로 남습니다.');
    expect(out).toContain('끝.');
    expect(out).not.toMatch(/\n{3,}/);
  });

  it('removes only the 강의 준비 section from instructor notes', () => {
    const out = stripPrepNotes(MD, 'content/instructor/day2/01.md');
    expect(out).not.toContain('강의 준비');
    expect(out).toContain('## 준비');
    expect(out).toContain('## 시연 순서');
  });

  it('keeps CRLF line endings', () => {
    const out = stripPrepNotes(MD.replace(/\n/g, '\r\n'), 'x.md');
    expect(out).toContain('\r\n');
    expect(out).not.toMatch(/[^\r]\n/);
  });

  it('is a no-op without markers', () => {
    expect(stripPrepNotes('본문\n', 'a.mdx')).toBe('본문\n');
  });
});

describe('run (CLI)', () => {
  const quiet = { log: () => {}, error: () => {} };

  function makeRoot() {
    const root = mkdtempSync(join(tmpdir(), 'prep-'));
    mkdirSync(join(root, 'content', 'day2'), { recursive: true });
    mkdirSync(join(root, 'content', 'instructor', 'day2'), { recursive: true });
    mkdirSync(join(root, 'src', 'pages'), { recursive: true });
    writeFileSync(join(root, 'content', 'day2', '01.mdx'), MDX, 'utf8');
    writeFileSync(join(root, 'content', 'instructor', 'day2', '01.md'), MD, 'utf8');
    writeFileSync(join(root, 'content', 'day2', '02.mdx'), '본문만\n', 'utf8');
    return root;
  }

  it('list prints markers and --check fails while any remain', () => {
    const root = makeRoot();
    const lines: string[] = [];
    expect(run(['list'], { root, io: { log: (s: string) => lines.push(s), error: () => {} } })).toBe(0);
    expect(lines.join('\n')).toContain('content/day2/01.mdx:9');
    expect(run(['list', '--check'], { root, io: quiet })).toBe(1);
  });

  it('strip removes every marker, then --check passes', () => {
    const root = makeRoot();
    expect(run(['strip'], { root, io: quiet })).toBe(0);
    expect(readFileSync(join(root, 'content', 'day2', '01.mdx'), 'utf8')).not.toContain('PrepNote');
    expect(readFileSync(join(root, 'content', 'day2', '02.mdx'), 'utf8')).toBe('본문만\n');
    expect(run(['list', '--check'], { root, io: quiet })).toBe(0);
  });

  it('unknown command exits non-zero', () => {
    expect(run(['nope'], { root: makeRoot(), io: quiet })).not.toBe(0);
  });
});
