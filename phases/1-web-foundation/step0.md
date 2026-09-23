# Step 0: astro-setup

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md` — CRITICAL 규칙과 명령어
- `/docs/ARCHITECTURE.md` — 1절 디렉터리, 3절 스키마 담당, 7절 빌드와 오프라인 제약
- `/docs/ADR.md` — ADR-001(Astro), ADR-002(서버·분석 도구 없음), ADR-004(검사 담당), ADR-007(CI), ADR-008(오프라인·인라인 스크립트), ADR-012(Playwright 분리)
- `/docs/UI_GUIDE.md` — 원칙 4(오프라인), 타이포그래피(시스템 글꼴만)
- `/docs/DEPLOYMENT.md` — 2절 로컬 명령, 4절 CI
- `/scripts/validate_course.py` — 이미 있는 Python 검증기(CLI 옵션 `--scope`, `--docs-only`)
- `/requirements-dev.txt`, `/.gitignore`, `/.gitattributes`

이 저장소에는 아직 Node 프로젝트가 없다. Phase 0에서 만든 docs·`content/*.yaml`·Python 검증기가 있다.

## 작업 목적

웹 강의 사이트의 빌드·검증 도구를 설치하고, 이후 모든 step의 AC가 되는 `npm run verify` 명령을 만든다. 이 step에서는 사이트 기능을 만들지 않는다.

## 수정/생성 대상

- 생성: `package.json`, `package-lock.json`, `astro.config.mjs`, `tsconfig.json`, `.nvmrc`, `eslint.config.js`, `vitest.config.ts`, `scripts/verify.mjs`, `tests/unit/verify.test.ts`, `.github/workflows/verify.yml`, `src/env.d.ts`, `src/pages/index.astro`, `public/favicon.svg`
- 수정: `.gitignore`(필요한 항목만 추가)

## 작업 범위

1. **버전 확인**: `npm view astro version`, `npm view @astrojs/mdx version`으로 현재 버전을 확인하고 그 메이저 버전을 쓴다. Astro가 요구하는 Node 버전(`npm view astro engines.node`)을 `.nvmrc`와 `package.json` `engines.node`에 적는다(이 PC는 Node 22.x).
2. **의존성**: astro, @astrojs/mdx, @astrojs/check, typescript, yaml(등록부 yaml 읽기), vitest, eslint, eslint-plugin-astro, typescript-eslint. Playwright는 이 step에서 설치하지 않는다(step 6).
3. **`astro.config.mjs`**: `output: 'static'`, MDX 통합. 외부 CDN·웹폰트·분석 통합을 넣지 않는다. `build.format`은 `directory` 기본값을 유지한다(오프라인 변환은 step 6).
4. **`tsconfig.json`**: Astro strict 프리셋.
5. **`package.json` scripts** (모두 Node 스크립트 또는 도구 명령으로 작성해 Windows·Linux에서 같게 동작해야 한다):
   - `dev`, `build`, `preview`: astro 명령
   - `lint`: `eslint .` 와 `astro check`
   - `test`: `vitest run`
   - `verify`: `node scripts/verify.mjs`
6. **`scripts/verify.mjs`**: 아래 순서로 실행하고, 하나라도 실패하면 즉시 non-zero로 끝낸다.
   1. `npm run lint`
   2. `npm run build`
   3. `npm run test`
   4. `<python> -m pytest scripts -q`
   5. `<python> scripts/validate_course.py [--scope <값>]`
   - `<python>`은 `python3` → `python` 순으로 `--version`이 성공하는 것을 고른다. Windows의 WindowsApps 가짜 python(스토어 안내만 띄우는 것)은 버전 확인이 실패하므로 건너뛰게 된다.
   - 명령행 인자 중 `--scope <값>`(또는 `--scope=<값>`)만 validator로 넘긴다. 다른 인자는 무시하고 경고를 출력한다.
   - 자식 프로세스의 출력은 그대로 보여 주고, 마지막에 어느 단계에서 실패했는지 한 줄로 요약한다.
   - 순수 함수(`pickPython`, `parseScope`)는 export해 테스트할 수 있게 한다.
7. **`tests/unit/verify.test.ts`**: `parseScope`(`--scope lesson:x`, `--scope=lesson:x`, 인자 없음, 알 수 없는 인자)와 `pickPython`(명령 실행 함수를 주입해 python3 실패·python 성공 등)을 테스트한다. 테스트를 먼저 쓰고 구현한다(TDD).
8. **`src/pages/index.astro`**: "공무원을 위한 하네스 엔지니어링 — 준비 중" 정도의 최소 페이지. 과정명은 `content/course.yaml`의 `course.title`을 읽어 표시한다(`yaml` 패키지 사용). 스타일은 최소, 외부 리소스 없음.
9. **`.github/workflows/verify.yml`**: push(main)·pull_request에서 실행. actions/setup-node(`.nvmrc`), actions/setup-python(3.11 이상), `pip install -r requirements-dev.txt`, `npm ci`, `npm run verify`. 저장소 연결 전이라 실제로 돌지 않는다. YAML 문법만 맞으면 된다.
10. **`.gitignore`**: `dist/`, `dist-offline/`, `.astro/`, `node_modules/`는 이미 있다. 필요하면 `coverage/`만 추가한다. `references/` 줄은 절대 지우지 않는다.

## 수정 허용 경로

`package.json`, `package-lock.json`, `astro.config.mjs`, `tsconfig.json`, `.nvmrc`, `eslint.config.js`, `vitest.config.ts`, `.gitignore`, `scripts/verify.mjs`, `tests/unit/*`, `.github/*`, `src/env.d.ts`, `src/pages/index.astro`, `public/favicon.svg`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm install
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다. `npm run verify`의 다섯 단계가 모두 통과해야 한다.
2. `npm run verify -- --scope lesson:d1-harness-intro`도 실행해 scope가 validator로 전달되는지 확인한다.
3. `dist/`에 외부 URL(`http://`, `https://`)을 불러오는 `<script src>`·`<link href>`가 없는지 확인한다.
4. 아키텍처 체크리스트:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 스택을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 0을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "생성한 설정 파일, verify 단계 구성, 확정한 astro·Node 버전을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요(npm 레지스트리 접속 불가 등) → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 외부 CDN, 웹폰트(Google Fonts 등), 분석 도구를 추가하지 마라. 이유: 교육망에서 차단되고 오프라인 번들이 깨진다(ADR-002, ADR-008).
- npm 스크립트에 `rm`, `cp`, `VAR=값 명령` 같은 셸 전용 문법을 쓰지 마라. 이유: Windows의 npm은 cmd로 실행되어 동작하지 않는다.
- `content/*.yaml`을 zod로 다시 검증하지 마라. 이유: 등록부 검사는 Python 검증기만 담당한다(ADR-004).
- 교시 페이지, 레이아웃, 컴포넌트를 만들지 마라. 이유: step 1~3의 범위다.
- `scripts/validate_course.py`와 Python 테스트를 수정하지 마라. 이유: 이 step의 허용 경로가 아니다.
- git push를 하지 마라. 이유: 원작자 허락 전(CD-15).
- 기존 테스트를 깨뜨리지 마라.
