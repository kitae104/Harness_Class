# Step 11: d1-06-eval-run

## 0. OQ-03은 CD-22 보수 절차로 진행한다 (다른 작업보다 먼저 읽는다)

`/docs/ADR.md`의 **CD-22**와 `/docs/PRACTICE_DESIGN.md` 3절의 OQ-03 문장을 읽는다.

- OQ-03(같은 Project의 다른 대화가 평가에 주는 영향)은 **open이어도 이 step을 진행한다.** 확인 전이므로 **영향이 있다고 가정**한다(CD-22 ②).
- D1-06 절차에 등록부 대안을 반영한다: ① 평가(답변 단계) 전에 같은 Project의 연습 대화를 정리한다 `<Feature id="chatgpt-project-memory" />` ② 기대 답변·채점 결과(틀린 이유 포함)를 Project에 넣지 않는다.
- OQ-03 관련 문장에는 `[TBD: OQ-03]`를 남긴다. 확인된 사실처럼 쓰지 않는다(예: "정리하면 영향이 없다" 금지).
- OQ-03을 닫거나 docs를 고치지 않는다. 실사용 결과가 나오면 사람이 D1-06을 다시 검토한다(OQ-03 "필요 시점: 개설 전(D1-06 재검토)", OQ-23).
- 카드 `tested_at`·`tested_by`는 비워 둔다(CD-22 ①).

## 읽어야 할 파일

- `/CLAUDE.md` — CRITICAL 규칙, course.yaml 수정 예외 범위
- `/docs/OPEN_QUESTIONS.md` — OQ-03(open, CD-22 가정), OQ-23
- `/docs/ADR.md` — CD-06, **CD-17**, CD-21, **CD-22**
- `/docs/PRACTICE_DESIGN.md` — **3절(평가 절차의 단일 원천)**, 4·5절(채점 실행 1회차 = 따라 쓰기), 9절
- `/docs/PROMPT_GUIDE.md` — 5절(나쁜 카드: 답변 단계 기대 답변, Project 안 채점), 8절 ③ 이관
- `/docs/TOOL_GUIDE.md`, `/docs/CONTENT_GUIDE.md`, `/docs/LEARNING_OBJECTIVES.md`, `/docs/HARNESS_ELEMENTS.md`, `/docs/UI_GUIDE.md`
- `/content/course.yaml` — `d1-eval-run` 항목, `card-batch-grading`, `card-help-long-output`(lesson: common — 막힘 지점 `sp-d1-06-a`의 카드)
- `/content/product-features.yaml` — `chatgpt-temporary-chat`, `chatgpt-temporary-chat-in-project`, `chatgpt-project-memory`, `chatgpt-project-memory-eval-impact`
- **실습형 기준 예시(reviewed)**: `/content/day1/04.mdx`, `/content/instructor/day1/04.md`
- 앞뒤 교시: `/content/day1/05.mdx`, `/content/day1/07.mdx`(07은 "D1-06과 같은 방법으로" 재평가한다고 가리킨다)
- `/content/kits/day1-civil/` — 질문 파일(1~10, 11~20), 기대 답변 파일, 채점표 CSV
- `/content/external-links.yaml` — "평가" 탭

## 작업 목적

D1-06 `d1-eval-run`(일괄 평가 실행)을 만든다. 평가세트 23문항으로 비서의 점수를 얻는다. 핵심은 **답변과 채점을 분리**하는 것이다(CD-17). 그래야 같은 Project의 대화나 기대 답변이 점수를 부풀리지 않는다.

## 작업

1. `content/day1/06.mdx`(`lesson_id: d1-eval-run`) — 기준 예시 구조를 따른다. 평가 절차는 PRACTICE_DESIGN 3절 "실행(CD-17)"을 **그대로** 따른다:
   1. **답변**: Project의 새 대화에 **질문만** 붙여 넣는다. 두 번에 나눠 실행(1~10, 11~20 + 직접 쓴 3문항). 기대 답변은 넣지 않는다.
   2. **채점**: **Project 밖** 비개인화 임시 채팅에서 질문·기대 답변·받은 답을 넣고 `<PromptCard id="card-batch-grading" />`을 쓴다.
   3. **표본 확인**: 사람이 3문항을 직접 채점해 AI 채점과 비교한다.
   - OQ-03 보수 절차(CD-22: 평가 전 연습 대화 정리, 기대 답변·채점 결과를 Project에 넣지 않기)를 절차에 반영하고 `[TBD: OQ-03]`를 남긴다.
   - 답변을 받기 **전** 체크: Project 파일 목록에 규정·FAQ 두 파일만 있고 평가 질문·기대 답변 파일이 없는지 확인한다(TOOL_GUIDE 3절, CD-17).
   - 채점 카드는 기대 답변의 "참고(감점 사유 아님)" 항목으로 감점하지 않게 한다(CD-06: 자료에 없음 문항은 "확인 필요"면 1점).
   - 채점 결과("틀린 이유" 포함)는 하네스 대장 평가 탭에만 적고 **Project 대화에 붙이지 않게** 한다. 정답 내용이 Project에 남으면 D1-07 재평가가 오염된다(D1-07 카드도 질문·받은 답만 받는다).
   - 제품 정보(임시 채팅, 프로젝트 메모리)는 `<Feature>`로만.
   - 출력이 끊길 때(sp-d1-06-a): `<PromptCard id="card-help-long-output" />`.
   - 예상 결과 / 잘못된 결과 예시: **관대한 자기채점**(PRACTICE_DESIGN 3절)과 어디가 왜 틀렸는지.
   - 기록: 23문항 점수와 틀린 이유를 하네스 대장 "평가" 탭에(course.yaml checks).
   - "Harness에서 무엇을 바꿨는가": 검증(Evals)이 점수로, 기록(Observability)이 평가 탭으로 남았다. "다음 교시 연결": D1-07에서 틀린 문항의 원인을 찾아 고치고 같은 방법으로 다시 잰다.
2. `content/prompts/card-batch-grading.md` — **채점 전용**, `where: temporary-chat`, 기본 단계 1. CD-06 채점 규칙, 8열 출력. 답변을 생성하게 하지 않는다. `do_not_trust`에 관대한 채점. `tested_at`/`tested_by` 비움.
3. `content/prompts/card-help-long-output.md` — 공통 문제 해결 카드(분류 A, `where: project-chat`, 기본 단계 1). 이 step이 담당한다.
4. `content/instructor/day1/06.md` — 공개 가능한 진행 안내만.
5. `content/course.yaml` — **`d1-eval-run`·`card-batch-grading`·`card-help-long-output` 항목 안에서만** 예외 범위로 고친다.
6. "평가" 탭은 step 7에서 만들었다. 이 교시에 다른 탭이 꼭 필요할 때만 `content/external-links.yaml`에 **추가만** 한다.

## 수정 허용 경로

`content/day1/06.mdx`, `content/instructor/day1/06.md`, `content/prompts/card-batch-grading.md`, `content/prompts/card-help-long-output.md`, `content/course.yaml`(예외 범위), `content/external-links.yaml`(탭 추가만), `public/images/d1-eval-run/*`.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-eval-run
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`에 세 항목 밖의 변경이 없는지 확인한다.
3. 체크리스트: 답변 단계에 기대 답변이 없는가 / 채점이 Project 밖 임시 채팅인가 / 사람 표본 3문항이 있는가 / OQ-03 보수 절차(CD-22)가 반영되고 [TBD: OQ-03]가 남았는가 / 예상 결과·잘못된 결과 예시 / status draft까지.
4. D1-07(`content/day1/07.mdx`)이 이 교시의 확정 절차와 어긋나면 **07을 고치지 말고** error로 보고한다(07은 step 10에서 reviewed — 고치면 해시가 깨지고 전체 verify·CI가 실패한다. 사람이 07 수정과 재승인을 판단한다).
5. 결과에 따라 `phases/2-day1-content/index.json`의 step 11을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일, 반영한 OQ-03 보수 절차(CD-22), 카드 2장"`
   - 수정 3회 시도 후에도 실패, 또는 D1-07과 어긋남 → `"status": "error"`, `"error_message": "구체적 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- OQ-03이 해결된 것처럼 쓰지 마라. 이유: CD-22는 영향이 있다고 가정한 보수 절차다.
- OQ-03을 직접 닫거나 docs를 고치지 마라. 이유: 실사용 테스트는 사람이 한다. docs는 이 step의 허용 경로 밖이다.
- `content/day1/07.mdx`, `content/kits/`, 다른 reviewed 교시·카드를 수정하지 마라. 이유: reviewed 해시가 깨진다.
- 채점 카드에 답변 생성이나 Project 안 채점을 넣지 마라. 이유: CD-17, PROMPT_GUIDE 5절.
- status를 reviewed로 올리거나 `npm run review:approve`를 실행하지 마라. Codex를 등장시키지 마라.
- 기존 테스트를 깨뜨리지 마라.
