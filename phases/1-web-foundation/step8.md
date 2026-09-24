# Step 8: human-review

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 역할을 파악하라:

- `/CLAUDE.md` — reviewed는 사람만 올린다
- `/docs/ADR.md` — ADR-005(사람 검토 관문), ADR-011(상태는 course.yaml에만)
- `/docs/QUALITY_CHECKLIST.md` — 2절 사람 검토 항목(H-02, H-03, H-06, H-07), 3절 루브릭
- `/.claude/commands/harness.md` — human-review step 규칙
- `/phases/1-web-foundation/index.json` — `review_targets`
- `/content/course.yaml` — `d1-harness-intro`의 status와 reviewed_hash

## 작업 목적

개념형 기준 예시 D1-01(`d1-harness-intro`)이 **사람의 승인을 받았는지 확인하는 관문**이다. 이 step은 아무것도 만들거나 고치지 않는다. 승인되지 않았으면 사람에게 무엇을 해야 하는지 알려 주고 멈춘다.

## 수정/생성 대상

없음. `phases/1-web-foundation/index.json`의 이 step 상태만 갱신한다.

## 작업 범위

1. 아래 AC를 실행한다.
2. **통과하면**(review_targets가 모두 reviewed이고 해시가 일치) step을 completed로 기록한다.
3. **실패하면** 아무 파일도 고치지 말고 step을 blocked로 기록한다. `blocked_reason`에 사람이 할 일을 적는다:
   - 로컬에서 확인: `npm run build && npm run preview` → `/course/day1/01/`
   - 오프라인 확인(선택): `npm run build:offline` → `dist-offline/index.html`
   - QUALITY_CHECKLIST 3절 루브릭으로 검토. 4개 항목이 모두 2점이어야 승인한다.
   - 수정이 필요하면 `content/day1/01.mdx`를 고친 뒤 다시 검토한다.
   - 승인: `npm run review:approve d1-harness-intro`
   - 이 step의 status를 `pending`으로 되돌리고 `blocked_reason`을 지운 뒤 `python scripts/execute.py 1-web-foundation`을 다시 실행한다.

## 수정 허용 경로

없음(빈 목록). 자기 phase 디렉터리의 index.json만 갱신한다.

## Acceptance Criteria

```bash
python scripts/validate_course.py --scope phase:1-web-foundation --require-reviewed
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 결과에 따라 `phases/1-web-foundation/index.json`의 step 8을 업데이트한다:
   - 오류 0 → `"status": "completed"`, `"summary": "D1-01 기준 예시 사람 승인 확인(reviewed_hash 일치)"`
   - V-REV-001 또는 V-REV-002 오류 → `"status": "blocked"`, `"blocked_reason": "D1-01 사람 검토 필요: <위 작업 범위 3의 절차를 요약>"` 후 즉시 중단
   - 그 밖의 오류(예: 스크립트 실행 실패) → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `npm run review:approve`나 `scripts/review_approve.py`를 실행하지 마라. 이유: 승인은 사람만 한다(CLAUDE.md CRITICAL, ADR-005).
- course.yaml의 status나 reviewed_hash를 직접 고치지 마라. 이유: 같은 이유.
- 콘텐츠를 고쳐서 통과시키려 하지 마라. 이유: 이 step의 허용 경로는 비어 있다.
- 3회 재시도 동안 같은 판정이 나오면 추가 시도 없이 blocked로 기록하라. 이유: 사람 개입 없이는 결과가 바뀌지 않는다.
