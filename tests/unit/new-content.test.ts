import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { parse as parseYaml } from 'yaml';
import {
  checkName,
  fillTemplate,
  lessonTarget,
  planNew,
  registrationHint,
  run,
} from '../../scripts/new_content.mjs';

const course = {
  cards: [
    { id: 'card-a', lesson: 'l1', title: '카드', category: 'C', level: 2, where: 'new-chat', track: 'core', status: 'planned' },
  ],
  lessons: [
    {
      id: 'l1', day: 1, number: 3, type: 'practice', status: 'planned',
      stuck_points: [{ id: 'sp-l1', text: '막힘', supports: [2], card: 'card-a' }],
    },
    { id: 'l2', day: 2, number: 12, type: 'concept', status: 'planned', stuck_points: [] },
    { id: 'l3', day: 2, number: 5, type: 'project', status: 'planned' },
  ],
};

describe('checkName', () => {
  it('accepts kebab-case ids', () => {
    expect(checkName('d1-harness-intro')).toBeNull();
    expect(checkName('card-a')).toBeNull();
  });

  it('rejects empty, uppercase, spaces, and path characters', () => {
    for (const bad of ['', 'Card-A', 'card a', '../x', 'a/b', 'a\\b', '-a', 'a-', 'a--b']) {
      expect(checkName(bad)).not.toBeNull();
    }
  });
});

describe('lessonTarget', () => {
  it('uses day folder and two-digit number', () => {
    expect(lessonTarget({ day: 1, number: 3 })).toBe('content/day1/03.mdx');
    expect(lessonTarget({ day: 2, number: 12 })).toBe('content/day2/12.mdx');
  });
});

describe('fillTemplate', () => {
  it('replaces every {{key}} occurrence', () => {
    expect(fillTemplate('a {{x}} b {{x}} {{y}}', { x: '1', y: '2' })).toBe('a 1 b 1 2');
  });

  it('fails on unknown keys so scaffolds never keep raw placeholders', () => {
    expect(() => fillTemplate('{{missing}}', {})).toThrow(/missing/);
  });
});

describe('planNew', () => {
  it('lesson: picks scaffold by lesson type', () => {
    expect(planNew('lesson', 'l1', course)).toMatchObject({
      target: 'content/day1/03.mdx',
      scaffold: 'lesson-practice.mdx',
      vars: { lesson_id: 'l1' },
    });
    expect(planNew('lesson', 'l2', course).scaffold).toBe('lesson-concept.mdx');
    expect(planNew('lesson', 'l3', course).scaffold).toBe('lesson-project.mdx');
  });

  it('lesson: unknown id is an error', () => {
    expect(() => planNew('lesson', 'ghost', course)).toThrow(/course\.yaml/);
  });

  it('prompt: fills card metadata from course.yaml', () => {
    expect(planNew('prompt', 'card-a', course)).toMatchObject({
      target: 'content/prompts/card-a.md',
      scaffold: 'prompt.md',
      vars: { id: 'card-a', stuck_point: 'sp-l1', where: 'new-chat', default_level: '2' },
    });
  });

  it('prompt: unregistered card tells the author to register it first', () => {
    expect(() => planNew('prompt', 'card-new', course)).toThrow(/먼저 막힘 지점과 카드를 course\.yaml에 등록하라/);
  });

  it('module and kit: target folders and a registration hint', () => {
    expect(planNew('module', 'my-practice', course)).toMatchObject({
      target: 'content/modules/my-practice.mdx',
      scaffold: 'module.mdx',
    });
    expect(planNew('kit', 'day1-civil', course)).toMatchObject({
      target: 'content/kits/day1-civil/kit.yaml',
      scaffold: 'kit.yaml',
    });
  });

  it('kit hint asks to register the kit in course.yaml kits', () => {
    const { hint } = planNew('kit', 'day1-civil', course);
    expect(hint).toContain('course.yaml kits');
    expect(hint).toContain('id: day1-civil');
  });

  it('rejects bad names and unknown kinds', () => {
    expect(() => planNew('module', '../escape', course)).toThrow();
    expect(() => planNew('page', 'x', course)).toThrow(/lesson \| module \| prompt \| kit/);
  });
});

describe('registrationHint', () => {
  it('module hint is a course.yaml modules line', () => {
    expect(registrationHint('module', 'my-practice')).toContain('- {id: my-practice,');
  });
});

describe('run (temporary folder)', () => {
  function makeRoot() {
    const root = mkdtempSync(join(tmpdir(), 'new-content-'));
    mkdirSync(join(root, 'content'), { recursive: true });
    const yamlText = [
      'cards:',
      '  - {id: card-a, lesson: l1, title: 카드, category: C, level: 2, where: new-chat, track: core, status: planned}',
      'lessons:',
      '  - id: l1',
      '    day: 1',
      '    number: 3',
      '    type: practice',
      '    status: planned',
      '    stuck_points:',
      '      - {id: sp-l1, text: 막힘, supports: [2], card: card-a}',
      '',
    ].join('\n');
    writeFileSync(join(root, 'content', 'course.yaml'), yamlText, 'utf8');
    return root; // 뼈대 파일은 저장소의 scripts/scaffold/에서 읽는다
  }

  const quiet = { log: () => {}, error: () => {} };

  it('creates a lesson file with lesson_id and does not touch course.yaml', () => {
    const root = makeRoot();
    const before = readFileSync(join(root, 'content', 'course.yaml'), 'utf8');
    expect(run(['lesson', 'l1'], { root, io: quiet })).toBe(0);
    const text = readFileSync(join(root, 'content', 'day1', '03.mdx'), 'utf8');
    expect(text).toMatch(/^---\nlesson_id: l1\n---/);
    expect(text).not.toContain('{{');
    expect(readFileSync(join(root, 'content', 'course.yaml'), 'utf8')).toBe(before);
  });

  it('unknown lesson id exits non-zero and creates nothing', () => {
    const root = makeRoot();
    expect(run(['lesson', 'ghost'], { root, io: quiet })).not.toBe(0);
    expect(existsSync(join(root, 'content', 'day1'))).toBe(false);
  });

  it('never overwrites an existing file', () => {
    const root = makeRoot();
    mkdirSync(join(root, 'content', 'day1'), { recursive: true });
    writeFileSync(join(root, 'content', 'day1', '03.mdx'), '기존 내용', 'utf8');
    expect(run(['lesson', 'l1'], { root, io: quiet })).not.toBe(0);
    expect(readFileSync(join(root, 'content', 'day1', '03.mdx'), 'utf8')).toBe('기존 내용');
  });

  it('creates prompt, module, and kit scaffolds', () => {
    const root = makeRoot();
    expect(run(['prompt', 'card-a'], { root, io: quiet })).toBe(0);
    expect(run(['module', 'my-practice'], { root, io: quiet })).toBe(0);
    expect(run(['kit', 'day1-civil'], { root, io: quiet })).toBe(0);
    const card = readFileSync(join(root, 'content', 'prompts', 'card-a.md'), 'utf8');
    expect(card).toContain('id: card-a');
    expect(card).toContain('stuck_point: sp-l1');
    expect(card).toContain('default_level: 2');
    expect(card).not.toContain('{{');
    expect(readFileSync(join(root, 'content', 'modules', 'my-practice.mdx'), 'utf8')).toContain('module_id: my-practice');
    expect(readFileSync(join(root, 'content', 'kits', 'day1-civil', 'kit.yaml'), 'utf8')).toContain('id: day1-civil');
  });

  it('kit scaffold follows the PRACTICE_CASES 1 schema (files[], no legacy fields)', () => {
    const root = makeRoot();
    expect(run(['kit', 'day1-civil'], { root, io: quiet })).toBe(0);
    const kit = parseYaml(readFileSync(join(root, 'content', 'kits', 'day1-civil', 'kit.yaml'), 'utf8'));
    for (const key of ['id', 'title', 'track', 'sources', 'privacy_notes', 'fictional_label', 'files']) {
      expect(kit).toHaveProperty(key);
    }
    expect(Array.isArray(kit.files)).toBe(true);
    for (const legacy of ['guideline_frame', 'context_files', 'input_data', 'eval_candidates', 'form_template']) {
      expect(kit).not.toHaveProperty(legacy);
    }
  });

  it('missing arguments exit non-zero', () => {
    const root = makeRoot();
    expect(run([], { root, io: quiet })).not.toBe(0);
    expect(run(['lesson'], { root, io: quiet })).not.toBe(0);
  });
});
