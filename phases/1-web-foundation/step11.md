# Step 11: instructor-notes

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 배경을 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 8절 강사 안내 렌더링, 7절 오프라인 제약
- `/docs/CONTENT_GUIDE.md` — 1절(강사 안내는 페이지 하단 접이식, 민감 메모 금지)
- `/docs/ADR.md` — CD-02(Public 저장소, 공개 가능한 진행 안내만)
- `/docs/UI_GUIDE.md` — 접이식, 인쇄, 발표 모드
- `/src/content.config.ts`, `/src/layouts/LessonLayout.astro`, `/src/pages/course/[day]/[num].astro`
- `/content/instructor/day1/01.md` — 이미 있는 강사 안내(렌더링되지 않고 있음)
- `/tests/e2e/site.spec.ts`, `/tests/e2e/offline.spec.ts`

## 작업 목적

ARCHITECTURE 8절에 정해 두었지만 구현되지 않은 **강사 안내 렌더링**을 만든다. 교시 페이지 하단에 `content/instructor/day{d}/{nn}.md`를 접이식 "강사 안내"로 표시한다.

## 수정/생성 대상

- 수정: `src/content.config.ts`(강사 안내 컬렉션 추가), `src/layouts/LessonLayout.astro`, `src/pages/course/[day]/[num].astro`
- 생성: `src/components/InstructorNotes.astro`
- 필요하면 수정: `src/styles/*`
- 테스트: `tests/unit/*`, `tests/e2e/*`

## 작업 범위

1. **컬렉션**: `instructor` 컬렉션을 `glob`(base `./content/instructor`, pattern `day*/*.md`)으로 추가한다. 강사 안내 파일에는 frontmatter가 없으므로 스키마는 빈 객체를 허용한다. ID로 day와 번호를 찾을 수 있어야 한다.
2. **표시**
   - 교시 페이지에서 같은 위치(day, number)의 강사 안내가 있으면 LessonNav 바로 앞에 `<details><summary>강사 안내</summary>…</details>`로 렌더링한다. 기본은 접힌 상태.
   - 파일이 없으면 아무것도 표시하지 않는다.
   - "준비 중" 교시에는 표시하지 않는다.
3. **인쇄·발표 모드**
   - 인쇄 CSS는 이미 모든 `<details>`를 펼친다. 강사 안내는 인쇄에서 **제외**한다(수강생 인쇄물에 들어가지 않게).
   - 발표 모드에서도 접힌 상태를 유지한다.
4. **테스트**
   - 단위 테스트: 교시 위치 → 강사 안내 ID 매핑 함수가 있으면 테스트한다.
   - e2e(`site.spec.ts`): D1-01 페이지에 "강사 안내" summary가 있고 기본으로 접혀 있는지 검사한다. D1-02(준비 중)에는 없는지도 검사한다.

## 수정 허용 경로

`src/content.config.ts`, `src/layouts/LessonLayout.astro`, `src/pages/course/*`, `src/components/InstructorNotes.astro`, `src/styles/*`, `tests/unit/*`, `tests/e2e/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run lint
npm run build
npm test
python -m pytest scripts -q
npm run build:offline
npm run test:e2e
```

(`npm run verify` 전체는 step 12 전까지 D1-01의 V-LSN-005 오류로 실패할 수 있다. 그래서 validator를 뺀 단계를 AC로 쓴다. `python scripts/validate_course.py`의 오류가 D1-01의 V-LSN-005뿐인지도 확인한다.)

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `dist/course/day1/01/index.html`에 강사 안내가 `<details>` 안에 있는지 확인한다.
3. 아키텍처 체크리스트:
   - 강사 안내에 민감 정보가 없는 기존 파일만 표시하는가(내용은 이 step에서 바꾸지 않음)?
   - 인쇄 CSS에서 강사 안내가 빠지는가?
   - 모듈 스크립트나 외부 리소스를 추가하지 않았는가?
4. 결과에 따라 `phases/1-web-foundation/index.json`의 step 11을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "instructor 컬렉션과 교시 하단 접이식 강사 안내(인쇄 제외), e2e 추가를 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/instructor/*`의 내용을 수정하지 마라. 이유: 강사 안내 내용은 step 12의 범위다.
- 강사 안내를 기본으로 펼쳐 두지 마라. 이유: 수강생이 보는 화면이다. 강사용 정보는 필요할 때만 연다.
- 모듈 스크립트를 쓰지 마라. 이유: file://에서 차단된다(ADR-008).
- 기존 테스트를 깨뜨리지 마라.
