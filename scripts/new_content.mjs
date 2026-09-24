#!/usr/bin/env node
// 콘텐츠 뼈대 생성 명령과 사람 승인 명령 래퍼 (ARCHITECTURE 10·11절).
//   npm run new:lesson -- <lesson-id>   course.yaml 교시 유형에 맞는 뼈대 → content/day{d}/{nn}.mdx
//   npm run new:module -- <slug>        → content/modules/<slug>.mdx
//   npm run new:prompt -- <card-id>     course.yaml cards에 등록된 카드만 → content/prompts/<id>.md
//   npm run new:kit -- <kit-id>         → content/kits/<kit-id>/kit.yaml
//   npm run review:approve -- <id>      python scripts/review_approve.py <id> (사람이 실행)
// course.yaml과 다른 등록부는 수정하지 않는다. 등록이 필요하면 안내 메시지만 출력한다.
// 이미 있는 파일은 덮어쓰지 않는다.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parse } from 'yaml';
import { pickPython } from './verify.mjs';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const DEFAULT_ROOT = dirname(SCRIPT_DIR);
const DEFAULT_SCAFFOLD_DIR = join(SCRIPT_DIR, 'scaffold');
const KINDS = ['lesson', 'module', 'prompt', 'kit'];
const LESSON_TYPES = ['concept', 'practice', 'project'];
const NAME_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

/** ID·slug 검사: 소문자·숫자·하이픈(kebab-case)만. 문제가 없으면 null, 있으면 오류 문장. */
export function checkName(name) {
  if (typeof name !== 'string' || name === '') return 'ID가 비어 있습니다';
  if (!NAME_RE.test(name)) return `ID '${name}'는 소문자·숫자·하이픈(kebab-case)만 쓸 수 있습니다`;
  return null;
}

/** 교시 파일 경로(저장소 루트 기준): content/day{day}/{number 두 자리}.mdx */
export function lessonTarget(lesson) {
  return `content/day${Number(lesson.day)}/${String(Number(lesson.number)).padStart(2, '0')}.mdx`;
}

/** 뼈대의 {{key}}를 채운다. 모르는 key가 있으면 오류(채워지지 않은 자리가 남지 않게). */
export function fillTemplate(text, vars) {
  return text.replace(/\{\{(\w+)\}\}/g, (_, key) => {
    if (!(key in vars)) throw new Error(`뼈대의 {{${key}}}를 채울 값이 없습니다`);
    return String(vars[key]);
  });
}

/** 파일을 만든 뒤 사람이 할 일을 한 줄로 안내한다. 등록부는 명령이 고치지 않는다. */
export function registrationHint(kind, name) {
  switch (kind) {
    case 'module':
      return `course.yaml modules에 다음 한 줄을 직접 추가하세요:\n  - {id: ${name}, title: 작성 예정, track: optional, status: planned, path: /practice/${name}}`;
    case 'kit':
      return `등록부 변경은 없습니다. kit.yaml의 sources에는 content/sources.yaml에 등록된 ID만 적으세요.`;
    case 'lesson':
      return `작성 후 course.yaml에서 교시 ${name}의 status만 draft로 바꾸고 npm run verify -- --scope lesson:${name}로 검사하세요.`;
    case 'prompt':
      return `작성 후 course.yaml에서 카드 ${name}의 status만 draft로 바꾸고 npm run verify로 검사하세요.`;
    default:
      return '';
  }
}

/**
 * 만들 파일을 계산한다(파일 시스템을 건드리지 않는 순수 함수).
 * @returns {{ target: string, scaffold: string, vars: Record<string, string>, hint: string }}
 */
export function planNew(kind, name, course) {
  if (!KINDS.includes(kind)) throw new Error(`알 수 없는 종류 '${kind}' (lesson | module | prompt | kit)`);
  const nameError = checkName(name);
  if (nameError) throw new Error(nameError);
  const hint = registrationHint(kind, name);

  if (kind === 'lesson') {
    const lesson = (course?.lessons ?? []).find((l) => l.id === name);
    if (!lesson) throw new Error(`course.yaml lessons에 없는 교시 ID: ${name} (교시는 course.yaml에 먼저 설계되어 있어야 합니다)`);
    if (!LESSON_TYPES.includes(lesson.type)) throw new Error(`교시 ${name}의 type '${lesson.type}'은 ${LESSON_TYPES.join(' | ')}이 아닙니다`);
    return { target: lessonTarget(lesson), scaffold: `lesson-${lesson.type}.mdx`, vars: { lesson_id: name }, hint };
  }

  if (kind === 'prompt') {
    const card = (course?.cards ?? []).find((c) => c.id === name);
    if (!card) throw new Error(`course.yaml cards에 없는 카드 ID: ${name} — 먼저 막힘 지점과 카드를 course.yaml에 등록하라`);
    const stuck = (course?.lessons ?? [])
      .flatMap((l) => l.stuck_points ?? [])
      .find((sp) => sp.card === name);
    if (!stuck) throw new Error(`카드 ${name}를 근거로 삼는 막힘 지점이 course.yaml에 없습니다 — 먼저 막힘 지점과 카드를 course.yaml에 등록하라`);
    return {
      target: `content/prompts/${name}.md`,
      scaffold: 'prompt.md',
      vars: { id: name, stuck_point: stuck.id, where: card.where, default_level: String(card.level) },
      hint,
    };
  }

  if (kind === 'module') {
    return { target: `content/modules/${name}.mdx`, scaffold: 'module.mdx', vars: { module_id: name }, hint };
  }

  return { target: `content/kits/${name}/kit.yaml`, scaffold: 'kit.yaml', vars: { kit_id: name }, hint };
}

/**
 * 뼈대 생성 명령 본체. 성공 0, 실패 1.
 * @param {string[]} argv [kind, name]
 * @param {{ root?: string, scaffoldDir?: string, io?: { log: (m: string) => void, error: (m: string) => void } }} [options]
 */
export function run(argv, { root = DEFAULT_ROOT, scaffoldDir = DEFAULT_SCAFFOLD_DIR, io = console } = {}) {
  const [kind, name] = argv;
  if (!kind || !name) {
    io.error('사용법: node scripts/new_content.mjs <lesson|module|prompt|kit> <id>');
    return 1;
  }
  try {
    const courseText = readFileSync(join(root, 'content', 'course.yaml'), 'utf8');
    const plan = planNew(kind, name, parse(courseText));
    const target = join(root, plan.target);
    if (existsSync(target)) throw new Error(`이미 있는 파일은 덮어쓰지 않습니다: ${plan.target}`);
    // 작업 폴더가 CRLF여도 만든 파일은 LF로 쓴다(git이 체크아웃 시 변환한다).
    const scaffold = readFileSync(join(scaffoldDir, plan.scaffold), 'utf8').replace(/\r\n?/g, '\n');
    const text = fillTemplate(scaffold, plan.vars);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, text, { encoding: 'utf8', flag: 'wx' });
    io.log(`만들었습니다: ${plan.target}`);
    io.log(plan.hint);
    return 0;
  } catch (e) {
    io.error(`[new:${kind}] 오류: ${e instanceof Error ? e.message : String(e)}`);
    return 1;
  }
}

function probe(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: 'ignore' });
  return result.error === undefined && result.status === 0;
}

/** npm run review:approve -- <id>: python을 골라 review_approve.py를 실행한다(사람이 실행하는 명령). */
function approve(args) {
  const python = pickPython(probe);
  if (python === null) {
    console.error('[review:approve] python3·python 중 실행 가능한 것이 없습니다.');
    return 1;
  }
  const result = spawnSync(python, [join(SCRIPT_DIR, 'review_approve.py'), ...args], {
    stdio: 'inherit',
    env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
  });
  if (result.error) console.error(`[review:approve] 실행 오류: ${result.error.message}`);
  return result.status ?? 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const argv = process.argv.slice(2);
  process.exit(argv[0] === 'approve' ? approve(argv.slice(1)) : run(argv));
}
