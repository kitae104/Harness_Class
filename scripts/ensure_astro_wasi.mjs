#!/usr/bin/env node
// postinstall: Windows(Smart App Control이 서명 없는 .node를 막을 수 있음)와 네이티브가 실패하는 환경에서
// 같은 버전의 WebAssembly(WASI) 대체 패키지를 node_modules에 넣는다.
// - Linux·macOS에서 네이티브가 불러와지면(CI, Vercel) 아무것도 하지 않는다.
// - @astrojs/compiler-binding은 네이티브가 실패하면 @astrojs/compiler-binding-wasm32-wasi를 스스로 찾아 쓴다.
// - 그 패키지는 cpu: wasm32로 표시되어 npm이 자동 설치하지 않으므로, npm pack + tar로 풀어 넣는다.
// - 설치를 실패시키지 않는다. 문제가 있으면 안내만 출력하고 0으로 끝낸다.
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const BINDING = '@astrojs/compiler-binding';
const WASI = '@astrojs/compiler-binding-wasm32-wasi';

/** 설치할 WASI 패키지 지정자. 네이티브 바인딩과 같은 버전이어야 한다. */
export function wasiPackageSpec(version) {
  if (typeof version !== 'string' || version === '') throw new Error(`${BINDING} 버전을 알 수 없습니다`);
  return `${WASI}@${version}`;
}

/**
 * Windows에서는 항상 대체 패키지를 둔다. Smart App Control은 같은 파일을 어떤 때는 막고 어떤 때는
 * 허용해서(2026-09-25 관찰), 설치 시점 검사만으로는 믿을 수 없다. 대체 패키지는 네이티브가 실패할 때만 쓰인다.
 * @returns {'native' | 'wasi-present' | 'install'}
 */
export function planWasi({ platform, nativeLoads, wasiInstalled }) {
  if (wasiInstalled) return 'wasi-present';
  if (platform === 'win32' || !nativeLoads) return 'install';
  return 'native';
}

function nativeLoads(req) {
  const env = process.env.NAPI_RS_FORCE_WASI;
  delete process.env.NAPI_RS_FORCE_WASI;
  try {
    // 플랫폼별 네이티브 패키지만 직접 불러 본다(WASI 대체로 성공한 것을 네이티브로 오인하지 않게).
    const arch = process.arch;
    const suffix = { win32: `win32-${arch}-msvc`, linux: `linux-${arch}-gnu`, darwin: `darwin-${arch}` }[process.platform];
    if (!suffix) return true; // 모르는 플랫폼은 건드리지 않는다
    req(`${BINDING}-${suffix}`);
    return true;
  } catch {
    return false;
  } finally {
    if (env !== undefined) process.env.NAPI_RS_FORCE_WASI = env;
  }
}

function install(version) {
  const spec = wasiPackageSpec(version);
  const work = mkdtempSync(join(tmpdir(), 'astro-wasi-'));
  try {
    const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    const tgz = execFileSync(npm, ['pack', spec, '--silent'], { cwd: work, encoding: 'utf8', shell: process.platform === 'win32' })
      .trim().split(/\r?\n/).pop();
    const dest = join(ROOT, 'node_modules', ...WASI.split('/'));
    mkdirSync(dest, { recursive: true });
    execFileSync('tar', ['-xzf', join(work, tgz), '-C', dest, '--strip-components=1']);
    return dest;
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}

export function main() {
  const req = createRequire(join(ROOT, 'package.json'));
  let version;
  try {
    version = JSON.parse(readFileSync(req.resolve(`${BINDING}/package.json`), 'utf8')).version;
  } catch {
    return 0; // Astro가 아직 없으면(부분 설치) 할 일이 없다
  }
  const plan = planWasi({
    platform: process.platform,
    nativeLoads: nativeLoads(req),
    wasiInstalled: existsSync(join(ROOT, 'node_modules', ...WASI.split('/'), 'package.json')),
  });
  if (plan !== 'install') return 0;
  try {
    const dest = install(version);
    console.log(`[ensure-astro-wasi] Astro 컴파일러 WASI 대체 패키지를 넣었습니다(네이티브가 막힐 때만 쓰임): ${dest}`);
  } catch (e) {
    console.warn(`[ensure-astro-wasi] WASI 대체 패키지 설치 실패: ${e.message}`);
    console.warn(`  수동 설치: npm pack ${wasiPackageSpec(version)} 후 node_modules/${WASI}에 풉니다(docs/DEPLOYMENT.md 참고).`);
  }
  return 0;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  process.exit(main());
}
