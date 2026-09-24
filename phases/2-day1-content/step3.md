# Step 3: d1-04-exemplar

## 읽어야 할 파일

먼저 아래 파일들을 읽고 설계 의도를 파악하라:

- `/CLAUDE.md` — CRITICAL 규칙, course.yaml 수정 예외 범위
- `/docs/CONTENT_GUIDE.md` — 1절(실습형 필수 섹션), 2절(**이 교시가 실습형 기준 예시**), 3~8절
- `/docs/ADR.md` — **CD-21**, CD-04, CD-17, CD-18
- `/docs/PRACTICE_CASES.md` — 2절 전체, 특히 **"수업 안내 규칙(D1-04 연결 문구, 필수)"**
- `/docs/PRACTICE_DESIGN.md` — 1절 3단 구조, 4절 지원 방식, 5절 단계 이동(근거 연결 1회차 = 바꿔 쓰기), 9절 시간 기준
- `/docs/PROMPT_GUIDE.md` — 카드 스키마·5칸 뼈대·작성 원칙·나쁜 카드
- `/docs/LEARNING_OBJECTIVES.md`, `/docs/HARNESS_ELEMENTS.md`, `/docs/TOOL_GUIDE.md`, `/docs/UI_GUIDE.md`
- `/content/course.yaml` — `d1-context` 교시 항목, `card-source-rule-snippet`
- `/content/day1/01.mdx`와 `/content/instructor/day1/01.md` — **개념형 기준 예시(reviewed)**. 문체·분량·컴포넌트 사용법을 맞추되 구조를 기계적으로 복제하지 않는다.
- `/content/kits/day1-civil/` 전체와 `kit.yaml` — step 1·2의 키트
- `/content/sources.yaml` — `fictional-day1-move-in-rule`, 실제 법령 `law-resident-registration`
- `/content/product-features.yaml` — `chatgpt-projects`, `chatgpt-file-uploads`, `chatgpt-project-file-limit`
- `/content/external-links.yaml` — `sheet-harness-ledger`의 `fallback_templates`
- `/src/components/` — `KitDownload`, `PromptCard`, `Source`, `Feature`, `ExternalLink`, `Callout`, `Checklist`, `CopyButton`
- `/scripts/scaffold/lesson-practice.mdx`

## 작업 목적

D1-04 `d1-context`(근거 자료 연결과 출처 답변)를 만든다. 이 교시는 **실습형 기준 예시**다. step 4에서 사람이 승인해야 D1-02·03·05·07을 만들 수 있다(CONTENT_GUIDE 2절). Day 1 흐름에서 이 교시는 지침(D1-02·03)에 **근거(Context)**를 더해, D1-01에서 기록한 "근거를 밝히지 않는 답"을 고치는 시간이다.

## 작업

1. `content/day1/04.mdx`(frontmatter `lesson_id: d1-context`)
   - CONTENT_GUIDE 1절의 공통 필수 섹션 + 실습형 섹션(강사 시연, 함께 따라하기, AI 도움받기, **예상 결과, 잘못된 결과 예시**, 잘 안 될 때)을 갖춘다. 개념 설명·잘 안 될 때·결과 예시는 접이식.
   - **교육용 가상 규정 안내(필수, PRACTICE_CASES 2절)**: 근거 자료를 처음 나눠 주는 지점에 다음 네 가지 뜻을 모두 담은 안내를 `Callout`으로 넣는다. 문구는 문맥에 맞게 다듬어도 된다.
     1. 이 실습의 규정은 실제 법령의 구조와 취지를 참고해 만든 **교육용 가상 규정**이다.
     2. **실제 법령 원문이 아니다.**
     3. **실습용으로 만든 자료**다.
     4. **실제 업무에서는 실제 법령을 확인한다**(D1-01에서 본 조문).
   - D1-01의 "기한과 늦었을 때의 처리가 맞는지는 D1-4에서 근거 자료로 확인합니다"와 자연스럽게 이어지게 한다(예: D1-01 체험 질문을 다시 꺼내 가상 규정으로 확인).
   - 키트 다운로드는 `<KitDownload id="day1-civil" />`.
   - 가상 규정 조문 인용은 `<Source id="fictional-day1-move-in-rule" article="제N조" />`. 실제 법령은 "실제 업무에서 확인할 법령"으로만 `<Source id="law-resident-registration" .../>` 인용할 수 있다. 가상 규정과 실제 법령을 한 문장에서 섞지 않는다.
   - 파일 업로드와 Project 관련 제품 정보는 `<Feature>`로만. 업로드가 막힐 때(sp-d1-04-c)는 본문 붙여넣기 대안을 `<Feature ... show="fallback"/>`로 안내한다.
   - 실습: 자료 안 질문 3개는 출처와 함께, 자료 밖 질문 2개는 "확인 필요"로 답하는지 테스트(course.yaml checks). 기준 질문 5(자동차 주소)를 자료 밖 질문 예로 쓸 수 있다.
   - 잘못된 결과 예시: **지어낸 조문**(가상 규정에 없는 조문 번호를 인용한 답)과 그것을 알아보는 방법(sp-d1-04-b). 어디가 왜 틀렸는지 바로 아래에 적는다.
   - 기록: 자료 목록과 기준일(하네스 대장 "자료 목록" 탭, 아래 5).
   - 섹션 "Harness에서 무엇을 바꿨는가": 근거(Context)와 안전장치(확인 필요 규칙)를 더했다는 것.
   - 섹션 "다음 교시 연결": D1-05 평가세트 설계.
   - 학습목표마다 수강생이 증거를 남기는 활동(말하기·쓰기·체크·기록)을 본문에 둔다.
2. `content/prompts/card-source-rule-snippet.md` — PROMPT_GUIDE 2절 스키마. `where: instructions`(지침란에 넣는 "지침 조각"), 기본 단계 2(바꿔 쓰기). 대괄호와 `replace` 1:1. "확인 필요" 문장과 "실제 개인정보를 넣지 마세요" 안내 포함. `tested_at`/`tested_by`는 비워 둔다(사람이 실제 테스트 후 채운다).
3. `content/instructor/day1/04.md` — 공개 가능한 진행 안내만(소요시간, 시연 순서, 흔한 오류, 생략 항목). 의도된 결함의 정답이나 운영 내부 메모는 쓰지 않는다(CD-02).
4. `content/course.yaml` — **`d1-context` 항목과 `card-source-rule-snippet` 항목 안에서만**, CLAUDE.md 예외 범위로 고친다: `status: draft`, `checks`를 `{id, text}` 형식으로 전환하고 `objectives[].checks` 연결, 필요 시 `stuck_points` 추가, `activities` 분 조정. 학습목표·산출물의 뜻과 ID는 바꾸지 않는다.
5. `content/external-links.yaml` — `sheet-harness-ledger.fallback_templates`에 이 교시가 쓰는 탭(예: `sources` "자료 목록": 자료명 / 기준일 / 올린 곳 / 메모)을 **추가만** 한다. 기존 탭은 바꾸지 않는다.
6. 과정 고유 용어(예: 교육용 가상 규정)를 새로 쓰면 `content/glossary.yaml`에 **추가만** 할 수 있다.

## 수정 허용 경로

`content/day1/04.mdx`, `content/instructor/day1/04.md`, `content/prompts/card-source-rule-snippet.md`, `content/course.yaml`(예외 범위), `content/external-links.yaml`(탭 추가만), `content/glossary.yaml`(추가만), `public/images/d1-context/*`. 이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-context
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`에 `d1-context`·`card-source-rule-snippet` 항목 밖의 변경이 없는지 확인한다.
3. 체크리스트:
   - 교육용 가상 규정 안내의 네 가지 뜻이 모두 있는가? D1-01과 이어지는가?
   - 수치·제품 정보·출처를 본문에 직접 쓰지 않고 등록부 ID로 참조했는가?
   - 실습형 필수 섹션(예상 결과·잘못된 결과 예시)이 있는가?
   - "긴 프롬프트 = 하네스"로 읽힐 문장이 없는가?
   - 콘텐츠 status를 draft까지만 올렸는가?
4. 결과에 따라 `phases/2-day1-content/index.json`의 step 3을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일, 섹션 구성, 추가한 대장 탭 ID, 가상 규정 안내 위치"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 등록부에 없는 제품 기능이 꼭 필요함 등 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/kits/`를 수정하지 마라. 이유: 키트는 step 1·2의 산출물이고 step 4에서 함께 검토한다. 문제가 있으면 error로 보고한다.
- `content/day1/01.mdx`를 수정하지 마라. 이유: reviewed 기준 예시라 해시가 깨진다.
- 가상 규정을 실제 법령처럼 표현하거나 실제 법령 원문을 옮기지 마라. 이유: CD-21.
- 등록부에 없는 제품 기능·메뉴 위치·한도를 본문에 쓰지 마라. 필요하면 blocked로 멈춰라. 이유: CLAUDE.md CRITICAL.
- status를 reviewed로 올리거나 `npm run review:approve`를 실행하지 마라. 이유: 승인은 사람만 한다.
- D1-02·03·05·06·07 파일을 만들지 마라. 이유: 기준 예시 승인 전에는 같은 유형 교시를 만들지 않는다.
- Codex를 등장시키지 마라. 이유: V-CRS-009.
- 기존 테스트를 깨뜨리지 마라.
