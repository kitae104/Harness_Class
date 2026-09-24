# Step 10: human-review-lessons

## 읽어야 할 파일

- `/CLAUDE.md` — reviewed는 사람만 올린다
- `/docs/ADR.md` — ADR-005, ADR-011
- `/docs/QUALITY_CHECKLIST.md` — 사람 검토 항목, 루브릭
- `/.claude/commands/harness.md` — human-review step 규칙
- `/phases/2-day1-content/index.json` — 이 step의 `review_targets`, step 9의 summary(reviewed 쪽 어긋남 보고)
- `/content/course.yaml` — 대상 항목의 status와 reviewed_hash

## 작업 목적

D1-02·03·05·07과 그 카드가 **사람의 승인을 받았는지 확인하는 관문**이다. D1-06(OQ-03 대기)과 분리해 먼저 검토한다. 검토자는 **강사 본인**이다(H-01). 이 step은 아무것도 만들거나 고치지 않는다.

대상: `lesson:d1-guideline`, `lesson:d1-project`, `lesson:d1-evalset`, `lesson:d1-improve`, `card:card-guideline-critique`, `card:card-eval-question-critique`, `card:card-failure-cause`

## 작업 범위

1. 아래 AC를 실행한다.
2. **통과하면** step을 completed로 기록한다.
3. **실패하면** 아무 파일도 고치지 말고 step을 blocked로 기록한다. `blocked_reason`에 사람이 할 일을 적는다:
   - 확인: `npm run build && npm run preview` → `/course/day1/02/`, `03/`, `05/`, `07/`
   - 검토 초점: Day 1 누적 흐름(step 9 summary 포함), 초보자 기준, 실습형 필수 섹션, CD-17(D1-05의 질문·기대 답변 용도 구분), D1-07이 평가 절차를 다시 쓰지 않는지, 카드를 교육용 Plus 계정에서 실제 테스트(`tested_at`·`tested_by`), QUALITY_CHECKLIST 루브릭
   - 수정이 필요하면 해당 파일을 고친 뒤 다시 검토한다
   - 승인: `npm run review:approve <id>`를 대상마다 실행(d1-guideline, d1-project, d1-evalset, d1-improve, card-guideline-critique, card-eval-question-critique, card-failure-cause)
   - 이 step의 status를 `pending`으로 되돌리고 `blocked_reason`을 지운 뒤 `python scripts/execute.py 2-day1-content`를 다시 실행한다

## 수정 허용 경로

없음(빈 목록). 자기 phase 디렉터리의 index.json만 갱신한다.

## Acceptance Criteria

```bash
python scripts/validate_course.py --scope phase:2-day1-content:step10 --require-reviewed
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 결과에 따라 `phases/2-day1-content/index.json`의 step 10을 업데이트한다:
   - 오류 0 → `"status": "completed"`, `"summary": "D1-02·03·05·07과 카드 3장 사람 승인 확인(reviewed_hash 일치)"`
   - V-REV-001 또는 V-REV-002 오류 → `"status": "blocked"`, `"blocked_reason": "사람 검토 필요: <위 절차 요약과 미승인 항목>"` 후 즉시 중단
   - 그 밖의 오류 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `npm run review:approve`나 `scripts/review_approve.py`를 실행하지 마라. 이유: 승인은 사람만 한다(CLAUDE.md CRITICAL, ADR-005).
- course.yaml의 status나 reviewed_hash를 직접 고치지 마라.
- 콘텐츠를 고쳐서 통과시키려 하지 마라. 이유: 이 step의 허용 경로는 비어 있다.
- 3회 재시도 동안 같은 판정이 나오면 추가 시도 없이 blocked로 기록하라.
