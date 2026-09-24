# Step 4: human-review-exemplar

## 읽어야 할 파일

- `/CLAUDE.md` — reviewed는 사람만 올린다
- `/docs/ADR.md` — ADR-005(사람 검토 관문), ADR-011(상태는 course.yaml에만), CD-21
- `/docs/QUALITY_CHECKLIST.md` — 사람 검토 항목(H-01 등), 루브릭
- `/.claude/commands/harness.md` — human-review step 규칙(step 단위 review_targets)
- `/phases/2-day1-content/index.json` — 이 step의 `review_targets`
- `/content/course.yaml` — 대상 항목의 status와 reviewed_hash

## 작업 목적

**실습형 기준 예시와 Day 1 키트가 사람의 승인을 받았는지 확인하는 관문**이다. 대상:
- `kit:day1-civil` — 가상 규정·FAQ·v0 지침·평가세트
- `lesson:d1-context` — D1-04 실습형 기준 예시
- `card:card-source-rule-snippet`

검토자는 **강사 본인**이다(H-01, OQ-12). 이 step은 아무것도 만들거나 고치지 않는다.

## 작업 범위

1. 아래 AC를 실행한다.
2. **통과하면** step을 completed로 기록한다.
3. **실패하면** 아무 파일도 고치지 말고 step을 blocked로 기록한다. `blocked_reason`에 사람이 할 일을 적는다:
   - 확인: `npm run build && npm run preview` → `/course/day1/04/`, 키트 zip 내려받아 열어 보기
   - 검토 초점: H-01(가상 규정·FAQ·기대 답변이 서로 맞고, 가상 규정이 실제 법령 원문으로 오해되지 않게 표기됨), D1-04의 가상 규정 안내 네 가지 뜻, 실습형 기준 예시로서 구조·분량·어조, 카드를 교육용 Plus 계정에서 실제 테스트(PROMPT_GUIDE 6절, `tested_at`·`tested_by` 기록), QUALITY_CHECKLIST 루브릭
   - 수정이 필요하면 해당 파일을 고친 뒤 다시 검토한다
   - 승인: `npm run review:approve day1-civil`, `npm run review:approve d1-context`, `npm run review:approve card-source-rule-snippet`
   - 이 step의 status를 `pending`으로 되돌리고 `blocked_reason`을 지운 뒤 `python scripts/execute.py 2-day1-content`를 다시 실행한다

## 수정 허용 경로

없음(빈 목록). 자기 phase 디렉터리의 index.json만 갱신한다.

## Acceptance Criteria

```bash
python scripts/validate_course.py --scope phase:2-day1-content:step4 --require-reviewed
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 결과에 따라 `phases/2-day1-content/index.json`의 step 4를 업데이트한다:
   - 오류 0 → `"status": "completed"`, `"summary": "D1-04 기준 예시·day1-civil 키트·card-source-rule-snippet 사람 승인 확인(reviewed_hash 일치)"`
   - V-REV-001 또는 V-REV-002 오류 → `"status": "blocked"`, `"blocked_reason": "사람 검토 필요: <위 작업 범위 3의 절차 요약과 미승인 항목>"` 후 즉시 중단
   - 그 밖의 오류 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `npm run review:approve`나 `scripts/review_approve.py`를 실행하지 마라. 이유: 승인은 사람만 한다(CLAUDE.md CRITICAL, ADR-005).
- course.yaml의 status나 reviewed_hash를 직접 고치지 마라. 이유: 같은 이유.
- 콘텐츠·키트를 고쳐서 통과시키려 하지 마라. 이유: 이 step의 허용 경로는 비어 있다.
- 3회 재시도 동안 같은 판정이 나오면 추가 시도 없이 blocked로 기록하라. 이유: 사람 개입 없이는 결과가 바뀌지 않는다.
