# Step 5: d1-02-guideline

## 읽어야 할 파일

- `/CLAUDE.md` — CRITICAL 규칙, course.yaml 수정 예외 범위
- `/docs/CONTENT_GUIDE.md` — 전체(실습형 섹션, 문체, 작성 순서)
- `/docs/PRACTICE_CASES.md` — 2절 지침서 5항목 작성 예, v0 지침, 의도된 결함(CD-18 공개 원칙)
- `/docs/PRACTICE_DESIGN.md` — 1절, 2절(지침 버전 탭에 복사 후 수정, [TBD: OQ-02]), 4절, 5절(지침 쓰기 1회차 = 따라 쓰기 + 비판 카드), 6·7절, 9절
- `/docs/PROMPT_GUIDE.md`, `/docs/LEARNING_OBJECTIVES.md`, `/docs/HARNESS_ELEMENTS.md`, `/docs/UI_GUIDE.md`
- `/content/course.yaml` — `d1-guideline` 항목, `card-guideline-critique`
- **실습형 기준 예시(reviewed)**: `/content/day1/04.mdx`, `/content/instructor/day1/04.md`, `/content/prompts/card-source-rule-snippet.md` — 구조·분량·어조를 맞춘다
- `/content/day1/01.mdx` — 앞 교시(기준 질문 기록, 다음 교시 연결 문장)
- `/content/kits/day1-civil/` — v0 지침 파일
- `/content/external-links.yaml`, `/content/product-features.yaml`

## 작업 목적

D1-02 `d1-guideline`(업무 지침서 작성)을 만든다. Day 1 흐름에서 D1-01의 "질문만 한 AI"에 처음으로 **지침(Instructions)**을 설계하는 시간이다. 키트의 v0 지침(일부러 단순하게 만든 초안)을 진단해 지침서 5항목으로 v1을 만든다.

## 작업

1. `content/day1/02.mdx`(`lesson_id: d1-guideline`) — 기준 예시 D1-04의 구조를 따르되 이 교시 내용에 맞춘다.
   - 강사 시연: 민원 업무 흐름과 AI·사람 역할 구분(업무 분석 1회차 = 강사 시연).
   - 함께 따라하기: v0 지침 함께 진단. v0이 "일부러 단순하게 만든 초안"임을 공개한다(CD-18).
   - 실습: 지침서 5항목(역할·범위·금지사항·출력 형식·모를 때 행동)으로 v1 작성. 범위는 "교육용 가상 규정과 교육용 FAQ 범위"(PRACTICE_CASES 2절). 수정 전 v0을 하네스 대장 "지침 버전" 탭에 복사한다.
   - AI 도움받기: `<PromptCard id="card-guideline-critique" />` — 먼저 스스로 쓰고, AI에게 애매한 곳을 비판받기.
   - 예상 결과 / 잘못된 결과 예시(추상적 표현 "친절하게"가 남은 지침 등)와 어디가 왜 틀렸는지.
   - "Harness에서 무엇을 바꿨는가": 지침이 생겼다(아직 AI에 넣지 않음). "다음 교시 연결": D1-03에서 이 지침을 Project에 넣고 D1-01 기준 답과 비교.
   - 키트 파일은 `<KitDownload id="day1-civil" />`로 안내한다.
2. `content/prompts/card-guideline-critique.md` — `where: new-chat`, 기본 단계 1(따라 쓰기). 5칸 뼈대, "확인 필요", 개인정보 안내, `check`, `do_not_trust`, `next`(반복 규칙은 지침으로 옮기기). `tested_at`/`tested_by`는 비워 둔다.
3. `content/instructor/day1/02.md` — 공개 가능한 진행 안내만.
4. `content/course.yaml` — **`d1-guideline`·`card-guideline-critique` 항목 안에서만** 예외 범위로: `status: draft`, `checks` `{id, text}` 전환과 `objectives[].checks` 연결, `stuck_points` 추가, `activities` 분 조정.
5. `content/external-links.yaml` — `sheet-harness-ledger.fallback_templates`에 "지침 버전" 탭을 **추가만**(예: 버전 / 날짜 / 지침 전문 / 바꾼 이유). 이미 있으면 그대로 쓴다. 탭 제목(`title`)은 **"지침 버전"** 으로 정확히 맞춘다 — 승인된 D1-04 본문이 이미 "하네스 대장 지침 버전 탭"이라고 부른다. 탭 ID는 `guideline-versions`를 권장한다.

## 수정 허용 경로

`content/day1/02.mdx`, `content/instructor/day1/02.md`, `content/prompts/card-guideline-critique.md`, `content/course.yaml`(예외 범위), `content/external-links.yaml`(탭 추가만), `public/images/d1-guideline/*`.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-guideline
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`에 `d1-guideline`·`card-guideline-critique` 항목 밖의 변경이 없는지 확인한다.
3. 체크리스트: 기준 예시와 구조·어조가 맞는가 / 수치·제품 정보를 등록부 ID로만 참조했는가 / 예상 결과·잘못된 결과 예시가 있는가 / "긴 프롬프트 = 하네스" 오해 문장이 없는가 / status는 draft까지인가.
4. 결과에 따라 `phases/2-day1-content/index.json`의 step 5를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일, 추가한 탭 ID, 다음 교시로 넘기는 산출물(지침서 v1)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/kits/`, `content/day1/01.mdx`, `content/day1/04.mdx`와 reviewed 카드 파일을 수정하지 마라. 이유: reviewed 해시가 깨진다. 문제가 있으면 error로 보고한다.
- 등록부에 없는 제품 기능을 쓰지 마라. 필요하면 blocked. 이유: CLAUDE.md CRITICAL.
- 지침 쓰기 1회차에 직접 쓰기(level 3)를 요구하지 마라. 이유: PRACTICE_DESIGN 5절.
- status를 reviewed로 올리거나 `npm run review:approve`를 실행하지 마라.
- 다른 교시 파일을 만들지 마라. Codex를 등장시키지 마라.
- 기존 테스트를 깨뜨리지 마라.
