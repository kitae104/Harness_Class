# Step 12: human-review-final

## 읽어야 할 파일

- `/CLAUDE.md` — reviewed는 사람만 올린다
- `/docs/ADR.md` — ADR-005, ADR-011, CD-17, CD-21
- `/docs/QUALITY_CHECKLIST.md` — 사람 검토 항목, 루브릭, 관문
- `/.claude/commands/harness.md` — human-review step 규칙
- `/phases/2-day1-content/index.json` — 이 step의 `review_targets`, 앞 step summary
- `/content/course.yaml` — 대상 항목의 status와 reviewed_hash

## 작업 목적

**Day 1 전체의 최종 관문**이다. D1-06과 그 카드를 승인받고, 이미 승인된 항목이 승인 뒤에 바뀌지 않았는지(해시 일치) 함께 확인한다. 검토자는 **강사 본인**이다(H-01). 이 step은 아무것도 만들거나 고치지 않는다.

대상(14개):
- 교시 7개: `d1-harness-intro`, `d1-guideline`, `d1-project`, `d1-context`, `d1-evalset`, `d1-eval-run`, `d1-improve`
- 카드 6장: `card-guideline-critique`, `card-source-rule-snippet`, `card-eval-question-critique`, `card-batch-grading`, `card-failure-cause`, `card-help-long-output`
- 키트: `day1-civil`

## 작업 범위

1. 아래 AC를 실행한다.
2. **통과하면** step을 completed로 기록한다.
3. **실패하면** 아무 파일도 고치지 말고 step을 blocked로 기록한다. `blocked_reason`에 사람이 할 일을 적는다:
   - 확인: `npm run build && npm run preview` → Day 1 일곱 교시를 순서대로, `npm run build:offline`에서 키트 zip이 열리는지, (선택) `npm run test:e2e`
   - 검토 초점: D1-06이 CD-17(답변은 Project 안 질문만, 채점은 Project 밖 임시 채팅, 사람 표본 3문항)과 OQ-03 해결 내용을 따르는지, D1-07과 이어지는지, Day 1 전체 누적 흐름, 카드 실제 테스트(`tested_at`·`tested_by`), QUALITY_CHECKLIST 루브릭
   - 수정이 필요하면 해당 파일을 고친 뒤 다시 검토한다(이미 승인된 항목을 고쳤다면 그 항목도 다시 승인한다)
   - 승인: 미승인 항목마다 `npm run review:approve <id>`
   - 이 step의 status를 `pending`으로 되돌리고 `blocked_reason`을 지운 뒤 `python scripts/execute.py 2-day1-content`를 다시 실행한다

## 수정 허용 경로

없음(빈 목록). 자기 phase 디렉터리의 index.json만 갱신한다.

## Acceptance Criteria

```bash
python scripts/validate_course.py --scope phase:2-day1-content:step12 --require-reviewed
npm run verify
```

## 검증 절차

1. 위 AC 커맨드 두 개를 실행한다.
2. 결과에 따라 `phases/2-day1-content/index.json`의 step 12를 업데이트한다:
   - 둘 다 오류 0 → `"status": "completed"`, `"summary": "Day 1 교시 7·카드 6·키트 1 모두 reviewed, 해시 일치, verify 통과"`
   - V-REV-001 또는 V-REV-002 오류 → `"status": "blocked"`, `"blocked_reason": "사람 검토 필요: <위 절차 요약과 미승인·해시 불일치 항목>"` 후 즉시 중단
   - 그 밖의 오류(verify 실패 등) → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `npm run review:approve`나 `scripts/review_approve.py`를 실행하지 마라. 이유: 승인은 사람만 한다(CLAUDE.md CRITICAL, ADR-005).
- course.yaml의 status나 reviewed_hash를 직접 고치지 마라.
- 콘텐츠를 고쳐서 통과시키려 하지 마라. 이유: 이 step의 허용 경로는 비어 있다.
- 3회 재시도 동안 같은 판정이 나오면 추가 시도 없이 blocked로 기록하라.
