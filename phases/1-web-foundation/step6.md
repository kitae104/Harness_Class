# Step 6: offline-build

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 7절 빌드 두 가지와 오프라인 제약
- `/docs/ADR.md` — ADR-008(오프라인·인라인 스크립트), ADR-012(Playwright, verify와 분리), CD-05
- `/docs/DEPLOYMENT.md` — 2절 명령, 10절 오프라인 배포
- `/docs/QUALITY_CHECKLIST.md` — V-WEB-002, V-WEB-003, 5절 배포 관문
- `/docs/UI_GUIDE.md` — 레이아웃(375px), 접근성
- step 0 산출물: `/package.json`, `/astro.config.mjs`, `/scripts/verify.mjs`
- step 2·3 산출물: `/src/layouts/*`, `/src/components/CopyButton.astro`, `/src/components/Checklist.astro`, `/src/components/LessonNav.astro`
- step 5 산출물: `/content/day1/01.mdx`(복사 버튼과 체크리스트가 있는 실제 교시)

## 작업 목적

교육망에서 Vercel이 막혀도 수업할 수 있도록 **오프라인 번들**을 만든다(CD-05). 그리고 브라우저 테스트로 핵심 기능이 인터넷 없이 동작하는지 검증한다: 복사, 이전/다음, 휴대폰 폭 화면, file:// 열기.

## 수정/생성 대상

- 생성: `scripts/build_offline.mjs`, `tests/unit/build-offline.test.ts`, `playwright.config.ts`, `tests/e2e/offline.spec.ts`, `tests/e2e/site.spec.ts`
- 수정: `package.json`(scripts·devDependencies), `package-lock.json`, `.gitignore`(`test-results/`, `playwright-report/`), `docs/QUALITY_CHECKLIST.md`(V-WEB-003 행 처리, 아래 5번)

## 작업 범위

1. **`scripts/build_offline.mjs`**
   - `dist/`를 `dist-offline/`로 복사하고 HTML 안의 사이트 루트 기준 링크(`href="/..."`, `src="/..."`)를 **각 파일 위치 기준 상대경로**로 바꾼다.
   - 디렉터리 링크(`/course/day1/01/`)는 `.../index.html`로 끝나게 바꾼다. file://에서는 디렉터리 인덱스가 자동으로 열리지 않기 때문이다.
   - 외부 URL(`http://`, `https://`)을 불러오는 `<script src>`, `<link rel="stylesheet">`, `<img src>`가 하나라도 있으면 실패로 끝낸다.
   - `dist-offline.zip`을 만든다. zip 생성은 Node만으로 하거나 크로스플랫폼 npm 패키지를 쓴다. OS의 `zip` 명령에 의존하지 않는다.
   - 경로 변환 함수(`toRelative(fromFile, rootPath)` 등)는 export하고 `tests/unit/build-offline.test.ts`로 먼저 테스트한다(TDD). Windows 경로 구분자(`\`)가 결과 URL에 섞이지 않게 한다.
2. **package.json scripts**
   - `build:offline` → `npm run build && node scripts/build_offline.mjs`
   - `test:e2e` → `playwright test`
   - `@playwright/test`를 devDependency로 추가하고, `npx playwright install chromium`으로 **Chromium만** 설치한다.
3. **`playwright.config.ts`**: Chromium 프로젝트 하나. `webServer`로 `npm run preview`를 띄워 `site.spec.ts`를 실행한다. `offline.spec.ts`는 `dist-offline/`의 파일을 `file://` URL로 직접 연다.
4. **테스트** — 두 파일 모두에서 **외부 네트워크 요청을 전부 막는다**(`page.route`로 localhost·file 외 요청은 abort). 막힌 요청이 발생하면 테스트 실패로 처리한다.
   - `site.spec.ts`(preview 서버):
     - 홈 → 전체 과정 → D1-01로 이동
     - D1-01의 "다음"을 누르면 D1-02(준비 중)로 이동
     - D1-01의 복사 버튼을 누르면 "복사됨"이 표시되고 클립보드 내용이 일치(클립보드 권한 부여)
     - 375px 폭에서 가로 스크롤이 없음(`scrollWidth <= clientWidth`)
     - 체크리스트 체크 후 새로고침해도 유지, "진행 초기화"로 해제
   - `offline.spec.ts`(file://):
     - `dist-offline/index.html` 열기 → 교시 링크 이동
     - D1-01 복사 버튼(대체 경로 포함) 동작
     - 이전/다음 동작
     - 콘솔 오류 없음
5. **QUALITY_CHECKLIST**: V-WEB-003은 Python validator가 아니라 Playwright가 검사한다. 1절 표에서 V-WEB-003 행을 지우고, 5절 배포 관문의 "오프라인·UI 변경" 행에 "(V-WEB-003 내용: 복사·이전/다음·375px·file://·외부 요청 차단)"을 덧붙인다. 다른 행은 바꾸지 않는다.

## 수정 허용 경로

`scripts/build_offline.mjs`, `playwright.config.ts`, `tests/e2e/*`, `tests/unit/*`, `package.json`, `package-lock.json`, `.gitignore`, `docs/QUALITY_CHECKLIST.md`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
npm run build:offline
npm run test:e2e
```

## 검증 절차

1. `npx playwright install chromium`을 먼저 실행한 뒤 위 AC 커맨드를 순서대로 실행한다.
2. `dist-offline/index.html`을 탐색기에서 더블클릭해 열리는지 확인한다(가능한 환경이라면).
3. `python scripts/validate_course.py`가 여전히 오류 0인지 확인한다(QUALITY_CHECKLIST 수정 후 V-QUA-001).
4. 아키텍처 체크리스트:
   - 링크 변환에 Windows 경로 구분자가 섞이지 않는가(테스트 존재)?
   - 외부 요청을 막은 상태에서 테스트가 통과하는가?
   - `test:e2e`를 `verify`에 넣지 않았는가?(ADR-012)
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 6을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "오프라인 번들 방식과 e2e 테스트 범위를 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - Chromium 다운로드가 네트워크 문제로 불가 → `"status": "blocked"`, `"blocked_reason": "playwright install chromium 실패: 원인"` 후 즉시 중단

## 금지사항

- 오프라인 문제를 컴포넌트 수정으로 해결하지 마라(`src/*`는 허용 경로가 아니다). 컴포넌트가 file://에서 동작하지 않으면 error_message에 원인과 파일을 적어 보고한다. 이유: 이 step은 검증을 담당하며, 원인 수정은 별도 step으로 한다.
- `test:e2e`를 `npm run verify`에 넣지 마라. 이유: 느린 테스트를 매 step AC에 넣지 않는다(ADR-012).
- Chromium 외 브라우저를 설치하지 마라. 이유: 설치 용량과 시간(ADR-012).
- OS 전용 명령(`zip`, `cp -r`, `rm -rf`)에 의존하지 마라. 이유: Windows에서 동작하지 않고 `rm -rf`는 훅이 차단한다.
- 기존 테스트를 깨뜨리지 마라.
