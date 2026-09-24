# Step 2: layout-nav

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 5절 사이트 구조와 URL 규칙(planned 교시는 "준비 중"), 6절 컴포넌트 규약(`LessonNav`), 7절 오프라인 제약
- `/docs/UI_GUIDE.md` — 디자인 원칙, 안티패턴, 색상, 타이포그래피, 레이아웃(본문 폭, 사이드바, 375px), 애니메이션
- `/docs/CONTENT_GUIDE.md` — 1절 교시 유형과 공통 필수 섹션
- `/docs/COURSE_MAP.md` — Day 1·Day 2의 역할
- step 1 산출물: `/src/content.config.ts`, `/src/lib/course.ts`, `/src/lib/registries.ts`, `/src/lib/types.ts`, `/tests/unit/*`
- step 0 산출물: `/src/pages/index.astro`, `/astro.config.mjs`

## 작업 목적

수강생과 강사가 교시 사이를 쉽게 이동하는 **사이트 골격**을 만든다. 공통 레이아웃, 사이드바, 현재 위치 표시, 이전/다음 이동, 시간표를 만든다. 교시 페이지는 교시 MDX가 있으면 본문을, 없으면 "준비 중"을 보여 준다. 나머지 메뉴 페이지는 빈 틀로 둔다.

## 수정/생성 대상

- 생성: `src/layouts/BaseLayout.astro`, `src/layouts/LessonLayout.astro`, `src/components/Sidebar.astro`, `src/components/LessonNav.astro`, `src/components/LocationBar.astro`, `src/styles/global.css`
- 생성: `src/pages/course/index.astro`, `src/pages/course/[day]/[num].astro`, `src/pages/before.astro`, `src/pages/practice/index.astro`, `src/pages/prompts/index.astro`, `src/pages/templates.astro`, `src/pages/project.astro`, `src/pages/resources.astro`, `src/pages/optional/codex.astro`
- 수정: `src/pages/index.astro`
- 테스트: `tests/unit/*`(순수 함수가 생기면)

## 작업 범위

1. **BaseLayout**
   - 시스템 한글 글꼴 스택만 사용한다(UI_GUIDE 타이포그래피).
   - 사이드바에 Day별 교시 목록(course.yaml `lessonsInOrder`)을 표시한다. 현재 교시를 강조하고, 좁은 폭에서는 `<details>`로 접는다.
   - 머리글에 과정명과 메뉴(홈, 사전 준비, 전체 과정, 실습, 프롬프트, 템플릿, 프로젝트, 자료)를 둔다.
   - `lang="ko"`. 본문 최대 폭 약 46rem, 좌측 정렬.
2. **LessonLayout**
   - 상단 LocationBar: "Day {d} · {n}교시 — {title}"와 필수/선택 배지(텍스트).
   - 본문 앞에 course.yaml의 학습목표를 자동 표시한다.
   - 본문 뒤에 결과 확인(`checks`)과 산출물(`outputs`)을 자동 표시한다.
   - 하단에 LessonNav를 둔다.
3. **LessonNav**: `neighbors()`로 이전/다음 교시 링크를 만든다. 링크 텍스트에 "Day·교시·제목"을 넣는다. 첫·마지막 교시는 한쪽만 표시한다.
4. **`/course`**: 전체 시간표. Day별로 교시 번호, 제목, 유형, 6요소를 표시한다. 6요소는 course.yaml `elements` 사전의 한국어 이름으로 보여 준다. **분·시간 수치는 course.yaml에서 계산해 표시하고 하드코딩하지 않는다.**
5. **`/course/[day]/[num]`**: `getStaticPaths`로 course.yaml의 core 교시 14개 경로를 모두 만든다. `lessons` 컬렉션에서 `lesson_id`가 일치하는 MDX가 있으면 렌더링한다. 없으면 "이 교시는 준비 중입니다"와 학습목표·산출물만 보여 준다. 교시 status가 `planned`이면 준비 중으로 표시한다.
6. **나머지 페이지**(`/before`, `/practice`, `/prompts`, `/templates`, `/project`, `/resources`, `/optional/codex`)는 제목과 "준비 중" 한 줄만 둔다. `/optional/codex` 첫 줄은 "몰라도 수료에 지장 없습니다."
7. **`global.css`**: UI_GUIDE의 색상과 타이포그래피를 CSS 변수로 정의한다. 다크 모드는 `prefers-color-scheme`를 따른다. 375px에서 가로 스크롤이 없어야 한다. 애니메이션은 넣지 않는다.
8. 모든 내부 링크는 사이트 루트 기준 절대경로(`/course/day1/01/`)로 만든다. 오프라인 상대경로 변환은 step 6이 담당한다.

## 수정 허용 경로

`src/layouts/*`, `src/pages/*`, `src/components/*`, `src/styles/*`, `tests/unit/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `dist/course/day1/01/index.html`부터 `dist/course/day2/07/index.html`까지 14개 파일이 생성되었는지 확인한다.
3. 각 교시 페이지에 이전/다음 링크가 올바르게 있는지(첫 교시는 이전 없음, 마지막 교시는 다음 없음) 빌드 결과를 열어 확인한다.
4. 아키텍처 체크리스트:
   - 교시 수·시간·목표를 하드코딩하지 않고 course.yaml에서 읽었는가?
   - 외부 CDN·웹폰트·모듈 스크립트를 쓰지 않았는가?
   - UI_GUIDE의 안티패턴(blur, gradient-text, 글로우, 보라색 등)을 쓰지 않았는가?
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 2를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 레이아웃·페이지·경로 구조를 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 교시 수, 시간, 학습목표, 산출물을 페이지에 직접 쓰지 마라. 이유: course.yaml이 단일 원천이다(CLAUDE.md CRITICAL).
- 모듈 스크립트(`<script>`를 Astro 기본 방식으로 번들)를 쓰지 마라. 인터랙션이 필요하면 `<details>`나 `is:inline` 스크립트만 쓴다. 이유: file://에서 모듈 스크립트가 차단된다(ADR-008).
- 교시 본문 MDX를 만들지 마라. 이유: 콘텐츠는 step 5와 콘텐츠 phase의 범위다.
- 카드·복사 버튼 등 UI 컴포넌트를 만들지 마라. 이유: step 3의 범위다.
- `content/*`, `src/lib/*`, `src/content.config.ts`를 수정하지 마라. 이유: 허용 경로가 아니다. 조회 함수가 부족하면 이 step 안에서 페이지 쪽에 작은 도우미를 만든다.
- 기존 테스트를 깨뜨리지 마라.
