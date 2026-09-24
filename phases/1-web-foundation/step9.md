# Step 9: objective-check-rules

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 배경을 파악하라:

- `/CLAUDE.md`
- `/docs/LEARNING_OBJECTIVES.md` — 3절(step 8에서 보완한 학습목표↔결과 확인 연결 규칙)
- `/docs/ARCHITECTURE.md` — 2절·4절·6절(step 8에서 보완한 checks 형식, external-links의 `fallback_kind`·`fallback_templates`)
- `/docs/QUALITY_CHECKLIST.md` — V-LSN-005, V-LNK-001(`예정(P1)`), 구현 열 규칙
- `/scripts/validate_course.py`, `/scripts/test_validate_course.py` — 기존 규칙, `check_course`, `check_registries`, `_resolve_scope`, `check_reviewed`, `--require-reviewed`
- `/src/lib/types.ts`, `/src/lib/course.ts`, `/src/layouts/LessonLayout.astro` — 결과 확인(`checks`)을 읽고 표시하는 곳
- `/content/course.yaml`, `/content/external-links.yaml`
- step 8 산출물: 위 docs와 등록부의 변경 내용(`git log -1 -p`로 확인)

## 작업 목적

step 8에서 정한 두 규칙을 검증기와 사이트에 구현한다.

- **V-LSN-005**: draft·reviewed 교시는 학습목표마다 결과 확인이 연결되어 있어야 한다.
- **V-LNK-001**: 교시가 준비 전 외부 링크를 쓸 때 바로 쓸 수 있는 대안이 있어야 한다.

## 수정/생성 대상

- 수정: `scripts/validate_course.py`, `scripts/test_validate_course.py`, `docs/QUALITY_CHECKLIST.md`(두 규칙의 구현 열을 `구현`으로)
- 수정: `src/lib/types.ts`, `src/lib/course.ts`(필요하면), `src/layouts/LessonLayout.astro`
- 테스트: `tests/unit/*`, `tests/fixtures/*`

## 작업 범위 (모두 TDD: 실패하는 테스트를 먼저 쓴다)

1. **checks 형식 (두 형식 허용)**
   - `lessons[].checks[]`는 문자열(과거 형식) 또는 `{id, text}`를 허용한다.
   - `objectives[].checks`는 같은 교시의 결과 확인 `id` 목록이다.
   - 결과 확인 `id`는 V-CRS-007(ID 중복 검사)에 포함한다.
   - V-CRS-001(스키마)은 두 형식을 모두 받아들인다. 기존 13개 planned 교시(문자열 형식)가 오류가 되면 안 된다.
2. **V-LSN-005**
   - status가 draft·reviewed인 교시는 다음을 모두 만족해야 한다. 어기면 **오류**.
     - 결과 확인이 모두 `{id, text}` 형식이다.
     - 학습목표마다 `checks`가 1개 이상 있다.
     - 모든 `checks`가 존재하는 결과 확인 id를 가리킨다.
   - planned 교시에서 위 조건을 어기면 **경고**.
   - `--scope`를 따른다.
3. **V-LNK-001**
   - 교시 MDX 본문에서 `<ExternalLink id="...">`를 찾는다.
   - 참조한 링크의 status가 `active`가 아니면 다음을 검사한다.
     - `fallback_kind`가 `template`이고 `fallback_templates`에 요청한 `tab`(속성이 있으면)이 있는지
     - 또는 `fallback_kind`가 `download`이고 그 파일이 실제로 있는지
   - 둘 다 아니면 기본은 **경고**, `--require-reviewed`·`--production`에서는 **오류**.
   - V-REG-004에 `fallback_kind` 허용값(`template` | `download` | `none`)과 `fallback_templates` 형식(탭 → 문자열 목록) 검사를 추가한다.
4. **사이트**
   - `types.ts`의 Lesson 타입에 새 checks 형식을 반영한다.
   - `LessonLayout.astro`는 두 형식 모두에서 결과 확인 문장을 표시한다.
5. **QUALITY_CHECKLIST**: V-LSN-005, V-LNK-001의 구현 열을 `구현`으로 바꾼다. RULES 등록부와 정확히 일치해야 한다(V-QUA-001).

## 수정 허용 경로

`scripts/validate_course.py`, `scripts/test_validate_course.py`, `docs/QUALITY_CHECKLIST.md`, `src/lib/*`, `src/layouts/LessonLayout.astro`, `tests/unit/*`, `tests/fixtures/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `python scripts/validate_course.py --scope lesson:d1-harness-intro`의 결과가 다음과 같은지 확인한다.
   - D1-01은 아직 문자열 checks이고 목표↔결과 확인 연결이 없으므로 **V-LSN-005 오류가 나와야 정상**이다. step 12가 고친다.
   - 이 오류 때문에 `npm run verify`(전체)가 실패하면, 이 step의 AC는 D1-01을 제외한 범위로 확인한다. 전체가 실패하는 그 상태는 step 12가 해소한다.
   - 이 판단은 summary에 명시한다.
3. 기존 테스트가 모두 통과하는지 확인한다.
4. 결과에 따라 `phases/1-web-foundation/index.json`의 step 9를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "V-LSN-005·V-LNK-001 구현, checks 두 형식 지원, D1-01이 V-LSN-005 오류 상태임(step 12에서 해소)을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/course.yaml`과 `content/day1/01.mdx`를 수정해 규칙을 통과시키지 마라. 이유: D1-01 수정은 step 12의 범위다.
- 기존 규칙의 ID·의미·수준을 바꾸지 마라. 이유: QUALITY_CHECKLIST와 테스트가 의존한다.
- planned 교시의 문자열 checks를 오류로 만들지 마라. 이유: 13개 교시는 각 교시를 작성하는 step에서 새 형식으로 바꾼다.
- 기존 테스트를 깨뜨리지 마라.

## 참고: AC 전체 실패 처리

D1-01의 V-LSN-005 오류가 `npm run verify` 전체를 실패시키는 것은 이 step의 의도된 결과다. 그래서 이 step의 성공 판정은 다음 세 가지로 한다.

- `npm run lint`, `npm run build`, `npm test`, `python -m pytest scripts -q`가 모두 통과한다.
- `python scripts/validate_course.py`의 오류가 **D1-01의 V-LSN-005뿐**이다.
- 그 사실을 summary에 적는다.

step 12가 끝나면 `npm run verify` 전체가 통과해야 한다.
