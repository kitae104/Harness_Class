# Step 5: d1-01-exemplar

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md` — CRITICAL 규칙, 정보 상태 태그
- `/docs/CONTENT_GUIDE.md` — 전체. 특히 1절 개념형 템플릿, 2절 기준 예시, 3절 문체, 4절 용어, 5절 수치·제품·출처 표기, 7절 핵심 메시지
- `/docs/HARNESS_ELEMENTS.md` — 1절 Prompt→Context→Harness 비교표(한계 열), 2절 6요소, 5절 행정 관행 비유
- `/docs/COURSE_MAP.md` — Day 1의 역할, 교시 간 산출물 연결
- `/docs/LEARNING_OBJECTIVES.md` — 목표·결과 확인 작성 규칙
- `/docs/PRACTICE_DESIGN.md` — 1절 실습 3단(STEP A/B/C), 2절 전/후 비교(D1-1 기준 답변은 비개인화 임시 채팅)
- `/docs/TOOL_GUIDE.md` — 2절 붙여넣을 곳, 5절 알려진 실패
- `/docs/UI_GUIDE.md` — 도식과 캡처(SVG 규칙, 대체 텍스트)
- `/content/course.yaml` — 교시 `d1-harness-intro`(활동·목표·산출물·막힘 지점·생략 항목)
- `/content/product-features.yaml` — `chatgpt-temporary-chat`, `chatgpt-projects`
- `/content/glossary.yaml`, `/content/banned-terms.yaml`
- step 2~4 산출물: `/src/layouts/LessonLayout.astro`, `/src/components/*`(CopyButton, Feature, Callout, Checklist, TrackBadge), `/scripts/scaffold/lesson-concept.mdx`, `/scripts/new_content.mjs`

## 작업 목적

Day 1 1교시 "하네스 엔지니어링 이해"를 **개념형 교시의 기준 예시**로 작성한다. 이후 모든 개념형 교시가 이 교시의 구조·분량·어조를 따른다. 사람이 승인하기 전까지 status는 draft다.

## 수정/생성 대상

- 생성: `content/day1/01.mdx`(`npm run new:lesson d1-harness-intro`로 뼈대를 만든 뒤 작성)
- 생성: `content/instructor/day1/01.md`(공개 가능한 강사 안내)
- 생성: `public/images/d1-harness-intro/harness-six-elements.svg`(그림 A: 6요소 개념도)
- 수정: `content/course.yaml` — **`d1-harness-intro`의 `status`만** `planned` → `draft`

## 작업 범위

1. **구조**: CONTENT_GUIDE 1절의 공통 필수 섹션 + 개념형 추가 섹션(왜 필요한가, 핵심 개념, 체험). 맨 위에 "필수 경로" 3~5단계를 둔다. 개념 설명은 접이식을 활용한다.
2. **흐름**: course.yaml `activities` 순서를 따른다: 입과 안내 → 같은 질문 2회 체험 → Prompt·Context·Harness와 6요소 지도 → 기준 질문 5개 기록. **분·시간 수치를 본문에 쓰지 않는다**(LessonLayout·course.yaml이 표시).
3. **체험(같은 질문, 다른 답)**:
   - 전입신고 관련 민원 질문 1개를 예시 입력으로 준다. 수강생이 두 번 묻고 짝과 비교한다.
   - 비교 관점 체크리스트 3개(내용·형식·근거)를 Checklist 컴포넌트로 둔다.
   - 질문 문장만 제공하고, **정답 내용(기한·과태료 등)을 본문에 단정하지 않는다.** 법령 내용이 필요하면 `<Source id="law-resident-registration" article="..."/>`로만 가리킨다.
4. **개념**:
   - HARNESS_ELEMENTS 1절의 비교표를 쓴다(한계 열 포함).
   - "긴 프롬프트 = 하네스가 아니다"를 명확히 쓴다.
   - 6요소를 한 줄씩 소개하고, 그림 A를 대체 텍스트와 함께 넣는다.
   - 행정 관행 비유 표를 1개 이상 쓴다.
5. **기준 질문 5개**:
   - Day 1 민원 답변 비서에서 쓸 질문 5개를 예시 입력으로 제공하고, CopyButton으로 복사할 수 있게 한다.
   - 수강생은 **비개인화 임시 채팅**에서 묻고 답을 하네스 대장에 기록한다. 임시 채팅은 `<Feature id="chatgpt-temporary-chat"/>`로 가리키고, 메뉴 위치를 본문에 직접 쓰지 않는다.
   - 하네스 대장 링크는 `<ExternalLink id="sheet-harness-ledger"/>`로 둔다(아직 planned이므로 fallback이 표시됨).
6. **막힘 지점**: course.yaml `stuck_points`(sp-d1-01-a, sp-d1-01-b)의 지원 방식(강사 시연·체크리스트·예시 입력)을 본문에 배치한다. 이 교시에는 카드가 없다(`cards: []`). 카드를 만들지 않는다.
7. **Harness에서 무엇을 바꿨는가 / 다음 교시 연결**: 기준 답변이 D1-3에서 "적용 전" 답으로 쓰인다는 것을 쓴다.
8. **그림 A (SVG)**:
   - 6요소 개념도. 텍스트는 SVG 안의 실제 `<text>`로 쓴다.
   - `<title>`과 `<desc>`를 넣는다. 외부 폰트·이미지를 참조하지 않는다.
   - 색은 UI_GUIDE 팔레트만 쓴다(보라·그라데이션 금지).
   - 같은 내용을 본문 목록으로도 제공한다.
9. **강사 안내** (`content/instructor/day1/01.md`): 시연 순서, 흔한 오류(로그인 실패, 임시 채팅 위치), 시간 부족 시 생략 항목(course.yaml `skip_if_short`와 일치). 예상 질문의 답이나 기관 내부 정보는 쓰지 않는다(CD-02).
10. **어조**: "~합니다" 강의체. 한 문장 60자 안팎, 한 문단 3문장 이내. 수강생 화면 용어만 쓴다.
11. **course.yaml 수정**: `d1-harness-intro` 항목의 `status: planned`를 `status: draft`로만 바꾼다.

## 수정 허용 경로

`content/day1/01.mdx`, `content/instructor/day1/01.md`, `public/images/d1-harness-intro/*`, `content/course.yaml`(`d1-harness-intro`의 status 한 줄만)

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-harness-intro
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`이 `d1-harness-intro`의 status 한 줄만 바꿨는지 확인한다.
3. `dist/course/day1/01/index.html`을 열어 확인한다: 필수 경로가 맨 위에 있는가, 복사 버튼이 있는가, 그림 A에 대체 텍스트가 있는가, 학습목표·결과 확인이 course.yaml에서 표시되는가.
4. 아키텍처 체크리스트:
   - 수치·제품 정보·법령 내용을 본문에 직접 쓰지 않고 `<Feature>`·`<Source>`·course.yaml로 표시했는가?
   - banned-terms(무료 계정, 모델명, 개발 용어)가 없는가?
   - "긴 프롬프트 = 하네스"로 읽힐 문장이 없는가?
   - status를 draft까지만 올렸는가?
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 5를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "D1-01 기준 예시의 섹션 구성·사용 컴포넌트·그림 경로를 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- status를 `reviewed`로 올리거나 `reviewed_hash`를 쓰지 마라. 이유: 사람만 승인한다(ADR-005, ADR-011).
- course.yaml에서 `d1-harness-intro`의 status 외에 다른 줄을 바꾸지 마라. 이유: course.yaml은 공유 등록부다. 목표·활동을 바꿀 필요가 있으면 error_message로 보고한다.
- 전입신고 기한, 과태료 금액 등 법령 내용을 본문에 단정하지 마라. 이유: 법령은 sources.yaml로만 인용하고, 과태료 금액은 원문 확인 전이다(OQ-07).
- 메뉴 위치, 모델명, 요금제 한도를 본문에 쓰지 마라. 이유: 제품 정보는 product-features.yaml에만 둔다.
- 실제 이름, 실제 전화번호, 실제 기관 자료를 쓰지 마라. 예시는 가상 자료로 표기한다. 이유: CLAUDE.md CRITICAL.
- 카드(`content/prompts/*`)를 만들지 마라. 이유: 이 교시에는 막힘 지점 근거가 있는 카드가 없다.
- Codex를 언급하지 마라. 이유: core 교시는 Codex에 의존하지 않는다(V-CRS-009).
- 기존 테스트를 깨뜨리지 마라.
