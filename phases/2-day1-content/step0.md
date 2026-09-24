# Step 0: kit-download

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 2절 데이터 흐름(`content/kits/` → 빌드 시 다운로드 생성, public/downloads 직접 커밋 금지), 6절 컴포넌트 규약, 7절 오프라인 제약
- `/docs/PRACTICE_CASES.md` — 1절 kit.yaml 스키마(`files[]`: path, role, download, description)
- `/docs/UI_GUIDE.md`
- `/scripts/validate_course.py` — `check_kits`, `_check_kit_file`(V-KIT-001), `KIT_ROLES`
- `/scripts/build_offline.mjs` — fflate로 zip을 만드는 기존 방식, 링크 상대경로 변환
- `/src/lib/course.ts`, `/src/lib/registries.ts`, `/src/lib/yaml.ts`, `/src/lib/types.ts` — 등록부 읽기 방식
- `/src/components/Source.astro`, `/src/components/ExternalLink.astro` — 컴포넌트가 등록부 ID를 받아 표시하는 방식(없는 ID는 빌드 오류)
- `/src/pages/course/[day]/[num].astro` — 정적 경로 생성 방식
- `/tests/unit/registries.test.ts`, `/tests/unit/build-offline.test.ts` — 테스트 스타일

## 작업 목적

Day 1 실습 키트(`day1-civil`, step 1·2에서 생성)를 수강생이 교시 페이지에서 내려받을 수 있게 한다. 이 step은 **코드만** 만든다. 키트 자료는 만들지 않는다. 현재 course.yaml `kits: []`이므로 키트가 0개일 때도 빌드가 통과해야 한다.

## 작업

TDD로 진행한다: 테스트를 먼저 쓰고 구현한다.

1. `src/lib/kits.ts`
   ```ts
   export interface KitFile { path: string; role: string; download?: boolean; description?: string }
   export interface Kit { id: string; title: string; track: string; fictional_label: string; privacy_notes: string; files: KitFile[] }
   export function loadKit(id: string, root?: string): Kit           // content/kits/<id>/kit.yaml
   export function listKits(root?: string): Kit[]                    // course.yaml kits 순서
   export function downloadFiles(kit: Kit): KitFile[]                // download: true인 파일만
   export function buildKitZip(kit: Kit, root?: string): Uint8Array  // fflate zipSync
   export function kitDownloadHref(id: string): string               // 예: /downloads/<id>.zip
   ```
   - zip에는 `download: true` 파일만 넣는다. 맨 앞에 `README.txt`(키트 제목, `fictional_label`, `privacy_notes`, 파일 목록과 description)를 넣는다.
   - 파일은 UTF-8 그대로 넣는다. zip 안 경로는 kit.yaml `path` 그대로(폴더 구조 유지).
   - kit.yaml에 적힌 파일이 없거나 경로가 키트 폴더 밖이면 예외를 던진다(빌드 실패). validator V-KIT-001과 같은 규칙이지만 여기서는 **빌드 안전장치**로만 두고, 규칙 판정은 validator가 한다.
2. `src/pages/downloads/[kit].zip.ts` — 정적 엔드포인트. `getStaticPaths`는 `listKits()`에서 다운로드 파일이 1개 이상인 키트만 반환한다. 응답은 `application/zip`.
3. `src/components/KitDownload.astro` — 입력 `id`.
   - 없는 키트 ID면 빌드 오류(`Source`와 같은 방식).
   - 표시: 키트 제목, "교육용 가상 자료" 표시(`fictional_label`), 다운로드 링크(zip), 파일 목록(파일명·description).
   - 다운로드 파일이 없으면 링크 대신 "내려받을 파일이 없습니다" 문구.
   - 스크립트 없이 동작한다(오프라인 번들, ARCHITECTURE 7절).
4. `src/lib/types.ts`에 타입이 필요하면 추가한다.
5. 오프라인 번들: `npm run build:offline` 결과에서 zip 링크가 상대경로로 동작하는지 확인한다. 필요할 때만 `scripts/build_offline.mjs`와 그 테스트를 고친다.
6. fflate는 현재 devDependencies다. 빌드 시점에만 쓰므로 그대로 둔다. 빌드가 실패할 때만 dependencies로 옮긴다(package.json, package-lock.json).
7. `docs/ARCHITECTURE.md`는 두 곳만 고친다: 2절의 "[생성과 <KitDownload>는 2-day1-content 첫 step에서 구현]" 표기를 구현 완료 표기로, 6절 컴포넌트 표에 `KitDownload` 한 행 추가.

테스트(`tests/unit/kits.test.ts`, 픽스처 `tests/fixtures/kits/`):
- download 필터, README 내용(가상 표기 포함), zip 안 파일 목록, 없는 파일·폴더 밖 경로 예외, 키트 0개일 때 경로 0개.

## 수정 허용 경로

`src/lib/kits.ts`, `src/lib/types.ts`, `src/pages/downloads/*`, `src/components/KitDownload.astro`, `tests/unit/kits*.test.ts`, `tests/fixtures/kits/*`, `scripts/build_offline.mjs`, `tests/unit/build-offline.test.ts`, `package.json`, `package-lock.json`, `docs/ARCHITECTURE.md`. 이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가? `public/downloads`에 파일을 커밋하지 않았는가?
   - ADR 기술 스택(Astro 정적, 외부 CDN 없음)을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
3. 결과에 따라 `phases/2-day1-content/index.json`의 step 0을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약(만든 파일, 다운로드 URL 형식, KitDownload 사용법)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/kits/`에 키트를 만들지 마라. 이유: 키트는 step 1·2의 일이다. 테스트는 `tests/fixtures/kits/`만 쓴다.
- `public/downloads/`에 zip을 만들거나 커밋하지 마라. 이유: 다운로드는 빌드 산출물이다(ARCHITECTURE 2절).
- validator(`scripts/validate_course.py`)에 규칙을 추가하지 마라. 이유: 키트 구조 판정은 V-KIT-001이 이미 한다.
- 외부 CDN·모듈 스크립트에 의존하는 다운로드 UI를 만들지 마라. 이유: 오프라인 번들(file://)에서 동작해야 한다.
- 기존 테스트를 깨뜨리지 마라.
