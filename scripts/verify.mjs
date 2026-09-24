#!/usr/bin/env node
// npm run verify -- [--scope <대상>]
// lint → build → vitest → pytest → validate_course.py 순서로 실행하고, 하나라도 실패하면 즉시 멈춘다.
// --scope 인자만 validator로 넘긴다(ARCHITECTURE 7절). Windows·Linux에서 같게 동작해야 한다.
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const IS_WINDOWS = process.platform === 'win32';
// 출력이 파이프로 캡처될 때도 Python이 UTF-8로 쓰게 한다(Windows 기본 cp949 대비).
const CHILD_ENV = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };

/** 명령행 인자에서 --scope 값만 골라낸다. 나머지는 ignored로 돌려준다. */
export function parseScope(argv) {
  let scope = null;
  const ignored = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg.startsWith('--scope=')) {
      scope = arg.slice('--scope='.length) || null;
      if (scope === null) ignored.push(arg);
    } else if (arg === '--scope') {
      const next = argv[i + 1];
      if (next !== undefined && !next.startsWith('--')) {
        scope = next;
        i += 1;
      } else {
        ignored.push(arg);
      }
    } else {
      ignored.push(arg);
    }
  }
  return { scope, ignored };
}

/**
 * python3 → python 순으로 `--version`이 성공하는 실행 파일을 고른다.
 * Windows의 WindowsApps 가짜 python은 버전 확인이 실패하므로 건너뛴다.
 * @param {(cmd: string, args: string[]) => boolean} run 명령이 성공하면 true
 */
export function pickPython(run) {
  for (const candidate of ['python3', 'python']) {
    if (run(candidate, ['--version'])) return candidate;
  }
  return null;
}

function probe(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: 'ignore' });
  return result.error === undefined && result.status === 0;
}

function runStep(name, cmd, args) {
  console.log(`\n[verify] ${name}: ${cmd} ${args.join(' ')}`);
  // npm은 Windows에서 npm.cmd라 셸을 거쳐야 실행된다.
  const result = spawnSync(cmd, args, {
    stdio: 'inherit',
    env: CHILD_ENV,
    shell: IS_WINDOWS && cmd === 'npm',
  });
  if (result.error) console.error(`[verify] ${name} 실행 오류: ${result.error.message}`);
  return result.error === undefined && result.status === 0;
}

function main(argv) {
  const { scope, ignored } = parseScope(argv);
  if (ignored.length > 0) {
    console.warn(`[verify] 경고: --scope 외의 인자는 무시합니다: ${ignored.join(' ')}`);
  }

  const python = pickPython(probe);
  const validateArgs = ['scripts/validate_course.py', ...(scope ? ['--scope', scope] : [])];
  const steps = [
    ['lint', 'npm', ['run', 'lint']],
    ['build', 'npm', ['run', 'build']],
    ['test', 'npm', ['run', 'test']],
    ['pytest', python, ['-m', 'pytest', 'scripts', '-q']],
    ['validate', python, validateArgs],
  ];

  for (const [name, cmd, args] of steps) {
    if (cmd === null) {
      console.error(`\n[verify] 실패: ${name} 단계 — python3·python 중 실행 가능한 것이 없습니다.`);
      return 1;
    }
    if (!runStep(name, cmd, args)) {
      console.error(`\n[verify] 실패: ${name} 단계에서 멈췄습니다.`);
      return 1;
    }
  }
  console.log(`\n[verify] 통과: lint, build, test, pytest, validate${scope ? ` (scope ${scope})` : ''}`);
  return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exit(main(process.argv.slice(2)));
}
