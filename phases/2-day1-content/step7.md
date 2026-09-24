# Step 7: d1-05-evalset

## 읽어야 할 파일

- `/CLAUDE.md` — CRITICAL 규칙, course.yaml 수정 예외 범위
- `/docs/ADR.md` — CD-06(문항당 1점), CD-16(제공 20 + 직접 3), **CD-17**, CD-21
- `/docs/PRACTICE_DESIGN.md` — **3절(평가 절차의 단일 원천)**, 4·5절(평가 문항 1회차 = 바꿔 쓰기), 7절, 9절
- `/docs/PRACTICE_CASES.md` — 2절 평가세트 구성
- `/docs/PROMPT_GUIDE.md` — 4·5절(나쁜 카드: "평가 질문 10개 만들어 줘", 답변 단계에 기대 답변)
- `/docs/CONTENT_GUIDE.md`, `/docs/LEARNING_OBJECTIVES.md`, `/docs/HARNESS_ELEMENTS.md`, `/docs/UI_GUIDE.md`
- `/content/course.yaml` — `d1-evalset` 항목, `card-eval-question-critique`
- **실습형 기준 예시(reviewed)**: `/content/day1/04.mdx`, `/content/instructor/day1/04.md`
- 앞 교시: `/content/day1/02.mdx`, `/content/day1/03.mdx`, `/content/day1/04.mdx`
- `/content/kits/day1-civil/` — 질문 파일, 기대 답변 파일, 채점표 CSV
- `/content/sources.yaml` — `fictional-day1-move-in-rule`
- `/content/external-links.yaml`

## 작업 목적

D1-05 `d1-evalset`(평가세트 설계)를 만든다. 지침과 근거를 갖춘 비서를 "좋아졌다"고 말하려면 무엇을 맞혀야 하는지 먼저 정해야 한다(**평가세트 먼저**). **검증(Evals)**이 처음 들어오는 교시다.

## 작업

1. `content/day1/05.mdx`(`lesson_id: d1-evalset`) — 기준 예시 구조를 따른다.
   - 설명: 평가세트 먼저, 평가 문항·기대 답변·채점 기준의 역할.
   - 강사 시연: 채점 기준(CD-06: 정확과 출처를 모두 충족해야 1점, 금지 위반 0점, "자료에 없음"은 "확인 필요"면 1점). 수치는 본문에 새로 정의하지 않고 PRACTICE_DESIGN 3절 기준을 따른다.
   - 함께 따라하기: 키트 기대 답변으로 가상 답변 2개 손채점.
   - 실습: 내 평가 문항 3개와 기대 답변(핵심 포인트 2개 + 근거 조문 — 가상 규정 조문) 작성. 하네스 대장 "평가" 탭에 기록.
   - AI 도움받기: `<PromptCard id="card-eval-question-critique" />` — 내가 쓴 문항을 비판받기(문항을 대신 만들어 달라는 카드가 아니다).
   - 제공 20문항은 `<KitDownload id="day1-civil" />`로 안내하고, **질문 파일과 기대 답변 파일의 용도 차이**(답변 단계에는 질문만, 기대 답변은 채점 단계에서만 — CD-17)를 이 교시에서 미리 알린다.
   - 예상 결과 / 잘못된 결과 예시(정답이 없는 문항, 근거 조문이 없는 기대 답변)와 어디가 왜 틀렸는지.
   - "Harness에서 무엇을 바꿨는가": 검증(Evals) 기준이 생겼다. "다음 교시 연결": D1-06에서 23문항을 실행해 점수를 얻는다.
2. `content/prompts/card-eval-question-critique.md` — `where: new-chat`, 기본 단계 2(바꿔 쓰기). "확인 필요"·개인정보 안내, `check`, `do_not_trust`, `next`. `tested_at`/`tested_by` 비움.
3. `content/instructor/day1/05.md` — 공개 가능한 진행 안내만. 의도된 결함과 연결된 문항 번호는 쓰지 않는다(키트의 강사용 설명 파일이 원천).
4. `content/course.yaml` — **`d1-evalset`·`card-eval-question-critique` 항목 안에서만** 예외 범위로 고친다.
5. `content/external-links.yaml` — "평가" 탭을 **추가만**. 열은 PRACTICE_DESIGN 3절 8열(번호 / 질문 / 답변 요약 / 정확 / 출처 / 금지 / 점수 / 틀린 이유). D1-06·07이 같은 탭을 쓴다.

## 수정 허용 경로

`content/day1/05.mdx`, `content/instructor/day1/05.md`, `content/prompts/card-eval-question-critique.md`, `content/course.yaml`(예외 범위), `content/external-links.yaml`(탭 추가만), `public/images/d1-evalset/*`.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-evalset
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`에 `d1-evalset`·`card-eval-question-critique` 항목 밖의 변경이 없는지 확인한다.
3. 체크리스트: 채점 기준이 CD-06과 같은가 / 답변 단계에 기대 답변을 넣으라는 안내가 없는가(CD-17) / 카드가 문항을 대신 만들지 않는가 / 예상 결과·잘못된 결과 예시 / status draft까지.
4. 결과에 따라 `phases/2-day1-content/index.json`의 step 7을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일, 평가 탭 ID와 열, 넘기는 산출물(평가세트 23문항)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/kits/`와 reviewed 교시·카드 파일을 수정하지 마라. 이유: reviewed 해시가 깨진다. 키트 문항에 문제가 있으면 error로 보고한다.
- 평가 실행 절차(답변 받기·채점)를 이 교시에서 자세히 쓰지 마라. 이유: 실행은 D1-06, 절차의 단일 원천은 PRACTICE_DESIGN 3절이다.
- "평가 질문 N개 만들어 줘" 형태의 카드를 만들지 마라. 이유: PROMPT_GUIDE 5절.
- status를 reviewed로 올리거나 `npm run review:approve`를 실행하지 마라. Codex를 등장시키지 마라.
- 기존 테스트를 깨뜨리지 마라.
