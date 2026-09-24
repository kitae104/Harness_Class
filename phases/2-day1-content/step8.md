# Step 8: d1-07-improve

## 읽어야 할 파일

- `/CLAUDE.md` — CRITICAL 규칙, course.yaml 수정 예외 범위
- `/docs/PRACTICE_DESIGN.md` — **3절(실패 원인 3분류, 재평가, 평가 절차의 단일 원천)**, 5절(실패 분석 1회차 = 바꿔 쓰기), 6절(빼보기 실험 선택), 9절
- `/docs/ADR.md` — CD-06, CD-17, CD-18, CD-21
- `/docs/PRACTICE_CASES.md` — 2절 의도된 결함
- `/docs/CONTENT_GUIDE.md`, `/docs/PROMPT_GUIDE.md`, `/docs/LEARNING_OBJECTIVES.md`, `/docs/HARNESS_ELEMENTS.md`, `/docs/COURSE_MAP.md`, `/docs/UI_GUIDE.md`
- `/content/course.yaml` — `d1-improve` 항목, `card-failure-cause`, Day 2 교시의 `used_by` 연결(`d2-guardrails`, `d2-batch-classify`)
- **실습형 기준 예시(reviewed)**: `/content/day1/04.mdx`, `/content/instructor/day1/04.md`
- 앞 교시: `/content/day1/01.mdx`~`/content/day1/05.mdx`(D1-06은 아직 없다 — "준비 중" 페이지)
- `/content/kits/day1-civil/` — 기대 답변, 가상 규정, FAQ
- `/content/external-links.yaml` — "지침 버전", "평가" 탭

## 작업 목적

D1-07 `d1-improve`(실패 분석과 재평가)를 만든다. D1-06 점수표의 틀린 문항을 원인별로 나눠 지침 또는 근거를 고치고, 다시 재서 점수 변화를 기록한다. **지침·근거·검증·기록이 한 바퀴 도는 것 = 하네스**라는 Day 1의 결론을 만드는 시간이다.

D1-06은 이 step 뒤(step 11)에 만든다. D1-06은 OQ-03 확인 결과에 따라 절차가 보완될 수 있다. 그래서 이 교시는 **평가 실행 절차를 다시 쓰지 않는다.** 재평가는 "D1-06과 같은 방법으로"라고만 쓰고, D1-06 페이지(`/course/day1/06/`)와 PRACTICE_DESIGN 3절의 원칙을 가리킨다.

## 작업

1. `content/day1/07.mdx`(`lesson_id: d1-improve`) — 기준 예시 구조를 따른다.
   - 강사 시연: 실패 원인 3분류(근거 / 지침 / 금지 위반) 판별 질문(PRACTICE_DESIGN 3절).
   - 실습: 내 실패 문항 원인 분류 → 지침 또는 근거 수정(수정 전 지침을 "지침 버전" 탭에 복사) → 실패 문항 + 무작위 5문항 재평가(**D1-06과 같은 방법으로**, 절차 반복 서술 금지) → 점수 전·후와 개정 이유 기록.
   - 의도된 결함(CD-18): 교육용 FAQ에서 빠진 항목은 **근거 보강**으로, 범위 애매 문항은 **지침 범위 문장 수정**으로 맞게 된다. 수강생에게 결함 위치를 미리 알려 주지 않되, "일부러 단순하게 만든 초안"임은 이미 공개되어 있다.
   - 근거 보강은 수강생이 **자기 Project의 자료**에 보충 설명을 더하는 것이다. 키트 원본 파일을 고치는 것이 아니다.
   - 보강할 FAQ 항목(11번, 대리 신고 준비물)은 `content/kits/day1-civil/instructor-notes.md` 3절의 문구를 **글자 그대로** 본문에 제공한다(복사 버튼). 새로 쓰거나 바꾸지 않는다 — 기대 답변 12번과 어긋난다.
   - 평가 12번에 "확인 필요"로 답했다면 그것은 **지침대로 한 올바른 행동**이었고, 점수가 0인 이유는 근거 자료에 답이 없었기 때문(근거 문제)이라고 분명히 설명한다. "짐작해야 점수를 받는다"로 읽히지 않게 한다.
   - AI 도움받기: `<PromptCard id="card-failure-cause" />` — 오답 원인 분석(바꿔 쓰기).
   - 예상 결과 / 잘못된 결과 예시(원인을 지침으로 잘못 짚어 지침만 길어진 경우 — "긴 프롬프트 ≠ 하네스")와 어디가 왜 틀렸는지.
   - "Harness에서 무엇을 바꿨는가": Day 1 전체 정리 — 지침 → 근거 → 평가 → 개선, 6요소 중 무엇이 생겼고(지침·근거·검증·안전장치·기록), 무엇이 Day 2로 남았는지(**도구(Tools)**, 안전장치·기록의 운영 규칙).
   - "다음 교시 연결": Day 2 D2-01(폼으로 입력 구조화), Project v3가 Day 2에서 이어진다.
2. `content/prompts/card-failure-cause.md` — `where: project-chat`, 기본 단계 2. "확인 필요"·개인정보 안내, `check`, `do_not_trust`, `next`. `tested_at`/`tested_by` 비움.
3. `content/instructor/day1/07.md` — 공개 가능한 진행 안내만.
4. `content/course.yaml` — **`d1-improve`·`card-failure-cause` 항목 안에서만** 예외 범위로 고친다.
5. `content/external-links.yaml` — "개정 기록" 탭을 **추가만**(예: 날짜 / 바꾼 곳(지침·근거) / 바꾼 내용 / 이유 / 점수 전 / 점수 후).

## 수정 허용 경로

`content/day1/07.mdx`, `content/instructor/day1/07.md`, `content/prompts/card-failure-cause.md`, `content/course.yaml`(예외 범위), `content/external-links.yaml`(탭 추가만), `public/images/d1-improve/*`.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-improve
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`에 `d1-improve`·`card-failure-cause` 항목 밖의 변경이 없는지 확인한다.
3. 체크리스트: 평가 실행 절차를 반복 서술하지 않았는가 / 6요소 누적과 Day 2로 남은 요소가 보이는가 / 키트 원본 수정을 요구하지 않는가 / 예상 결과·잘못된 결과 예시 / status draft까지.
4. 결과에 따라 `phases/2-day1-content/index.json`의 step 8을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일, 추가한 탭 ID, D1-06 참조 방식, Day 2로 넘긴 요소"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- D1-06 파일(`content/day1/06.mdx`)을 만들지 마라. 이유: OQ-03 확인 뒤 step 11에서 만든다.
- 답변 받기·채점 절차를 이 교시에 다시 쓰지 마라. 이유: D1-06이 확정되면 어긋난다. 이 파일은 step 10에서 승인된 뒤 다시 고칠 수 없다.
- `content/kits/`와 reviewed 교시·카드 파일을 수정하지 마라.
- status를 reviewed로 올리거나 `npm run review:approve`를 실행하지 마라. Codex를 등장시키지 마라.
- 기존 테스트를 깨뜨리지 마라.
