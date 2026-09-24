# Step 1: content-schema

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 2절 데이터 흐름, 3절 스키마 담당, 4절 course.yaml 스키마, 5절 URL 규칙, 10절 검토 상태
- `/docs/ADR.md` — ADR-003(단일 원천), ADR-004(검사 담당), ADR-011(상태는 course.yaml에만)
- `/docs/PROMPT_GUIDE.md` — 2절 카드 파일 스키마
- `/content/course.yaml`, `/content/product-features.yaml`, `/content/sources.yaml`, `/content/external-links.yaml`, `/content/glossary.yaml`
- step 0 산출물: `/package.json`, `/astro.config.mjs`, `/tsconfig.json`, `/scripts/verify.mjs`, `/src/pages/index.astro`

## 작업 목적

사이트가 콘텐츠와 등록부를 읽는 **데이터 계층**을 만든다. 교시 MDX·카드 파일의 frontmatter 스키마(zod)와, course.yaml·등록부를 타입이 있는 객체로 제공하는 조회 함수를 만든다. 이후 레이아웃·컴포넌트는 이 계층만 사용한다.

## 수정/생성 대상

- 생성: `src/content.config.ts`, `src/lib/course.ts`, `src/lib/registries.ts`, `src/lib/types.ts`, `tests/unit/course.test.ts`, `tests/unit/registries.test.ts`, `tests/fixtures/*`(테스트용 가짜 yaml)

## 작업 범위

1. **`src/content.config.ts`** — Astro content layer(`glob` 로더)로 컬렉션 3개:
   - `lessons`: `./content` 아래 `day1/*.mdx`, `day2/*.mdx`. frontmatter는 `lesson_id`(문자열, 필수)만 요구한다. 제목·목표·상태는 course.yaml에서 가져오므로 frontmatter에 두지 않는다.
   - `prompts`: `./content/prompts/*.md`. frontmatter는 PROMPT_GUIDE 2절의 필드(`id`, `stuck_point`, `where`, `when`, `input`, `l3_structure`, `l2_template`, `l1_full`, `default_level`, `line_notes`, `replace`, `check`, `do_not_trust`, `next`, `tested_at`, `tested_by`). `where`는 `instructions | project-chat | new-chat | temporary-chat`, `default_level`은 1~3. **`status`·`reviewed_hash` 필드는 두지 않는다**(ADR-011).
   - `modules`: `./content/modules/*.mdx`. frontmatter는 `module_id`.
   - 폴더가 비어 있어도 빌드가 실패하지 않아야 한다(지금은 콘텐츠 파일이 없다).
2. **`src/lib/types.ts`** — course.yaml과 등록부의 TypeScript 타입(Lesson, Card, StuckPoint, Feature, Source, ExternalLink, Term). 값 검증은 하지 않는다.
3. **`src/lib/course.ts`** — course.yaml을 `yaml` 패키지로 읽는 조회 함수:
   ```ts
   loadCourse(path?: string): Course
   lessonsInOrder(course): Lesson[]            // day, number 순
   lessonById(course, id): Lesson | undefined
   lessonByPosition(course, day, number): Lesson | undefined
   neighbors(course, id): { prev?: Lesson; next?: Lesson }   // Day 1 7교시 다음은 Day 2 1교시
   lessonUrl(lesson): string                   // /course/day{d}/{nn}, nn은 두 자리
   cardsForLesson(course, id): Card[]
   commonCards(course): Card[]
   ```
   - 경로 기본값은 저장소 루트의 `content/course.yaml`. 테스트는 `tests/fixtures`의 가짜 yaml로 한다.
4. **`src/lib/registries.ts`** — `loadFeatures()`, `featureById(id)`, `loadSources()`, `sourceById(id)`, `loadExternalLinks()`, `linkById(id)`, `loadGlossary()`, `termLabel(id)`(수강생 표기 `student_label` 우선). 없는 ID면 `undefined`를 반환하고, 빌드 단계에서 쓰는 쪽이 오류를 낸다.
5. **테스트(TDD)** — 테스트를 먼저 쓰고 구현한다.
   - 교시 순서
   - 이전/다음(첫 교시는 prev 없음, 마지막 교시는 next 없음, Day 경계를 넘는 경우)
   - URL 두 자리 번호
   - 카드 조회
   - 기능 조회와 학생 표기
   - 실제 `content/course.yaml`을 읽어 14교시가 나오는지 한 번 확인

## 수정 허용 경로

`src/content.config.ts`, `src/lib/*`, `tests/unit/*`, `tests/fixtures/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `npx vitest run tests/unit/course.test.ts tests/unit/registries.test.ts`가 통과하는지 따로 확인한다.
3. 아키텍처 체크리스트:
   - 등록부 yaml 검증을 zod로 중복 구현하지 않았는가?(ADR-004)
   - frontmatter에 status·reviewed_hash·제목·목표 같은 course.yaml 정보를 두지 않았는가?(ADR-003, ADR-011)
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
4. 결과에 따라 `phases/1-web-foundation/index.json`의 step 1을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "컬렉션 3개와 조회 함수 목록(파일 경로 포함)을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/*.yaml`을 수정하지 마라. 이유: 이 step은 읽기만 한다. 등록부 변경은 소유 step만 한다.
- 등록부 yaml의 필드 검증을 zod나 TypeScript 런타임 검사로 다시 만들지 마라. 이유: Python 검증기와 규칙이 이중화된다(ADR-004).
- 콘텐츠 파일(`content/day1/*.mdx` 등)을 만들지 마라. 이유: 교시 콘텐츠는 step 5와 이후 콘텐츠 phase의 범위다.
- 페이지·레이아웃·컴포넌트를 만들지 마라. 이유: step 2~3의 범위다.
- 기존 테스트를 깨뜨리지 마라.
