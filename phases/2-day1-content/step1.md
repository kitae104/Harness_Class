# Step 1: kit-civil-context

## 읽어야 할 파일

먼저 아래 파일들을 읽고 설계 의도를 파악하라:

- `/CLAUDE.md` — CRITICAL 규칙(등록부 추가만, status는 draft까지, 가상 자료 표기)
- `/docs/ADR.md` — CD-04, **CD-21(교육용 가상 규정)**, CD-18(의도된 결함), CD-17
- `/docs/PRACTICE_CASES.md` — **1절 kit.yaml 스키마, 2절 day1-civil 전체**(근거, 교육용 가상 규정 작성 규칙, 지침서 5항목 예, v0 지침, 의도된 결함, 과태료 금액), 5절 공통 금지
- `/docs/SOURCE_REGISTER.md` — 1절 `fictional` 유형
- `/docs/HARNESS_ELEMENTS.md`
- `/content/sources.yaml` — 기존 항목 형식(`fictional-civil-cases` 참고)
- `/content/course.yaml` — `kits: []` 위치와 주석
- `/content/day1/01.mdx` — **체험 질문과 기준 질문 5개**(이 키트가 답할 수 있어야 한다)
- `/scripts/validate_course.py` — `check_kits`, `_check_kit_file`, `KIT_REQUIRED`, `KIT_ROLES`
- `/src/lib/kits.ts`, `/src/components/KitDownload.astro` — step 0에서 만든 다운로드 구조

## 작업 목적

Day 1 공통 키트 `day1-civil`(전입신고 민원 답변 비서)의 **근거 자료**를 만든다. 평가 문항은 step 2에서 만든다. 이 키트는 D1-02(v0 지침), D1-04(근거 연결), D1-05~07(평가·개선)에서 계속 쓰인다.

## 작업

1. `content/kits/day1-civil/`에 자료 파일을 만든다. 파일명은 수강생이 알아보기 쉬운 한국어 또는 영문 kebab-case로 한다. 최소 구성:
   - **교육용 가상 규정** 1개(role `context`, download true). PRACTICE_CASES 2절 "교육용 가상 규정 작성 규칙(CD-21)"을 모두 지킨다:
     - 제목과 파일 첫머리에 "교육용 가상 규정"임과, 실제 법령 원문이 아니며 법적 효력이 없는 실습용 합성 자료임을 적는다.
     - 가상 지자체명을 쓴다. 실제 법령명·법령 번호·시행일·실제 기관명을 붙이지 않는다. 실제 조문 문구를 복제하지 않는다.
     - 조문은 `제N조(제목)` 형식. 기한·절차·수치는 단순화한다.
     - **과태료 금액을 정하지 않는다**(PRACTICE_CASES 2절 과태료 항목).
   - **규정 기반 교육용 FAQ** 1개(role `context`, download true). 가상 규정과 일치하고, 각 항목에 근거 조문(`제N조`)을 적는다. **의도된 결함(CD-18)**: FAQ에서 항목 1개를 일부러 빠뜨린다. 빠뜨린 항목과 그 이유는 강사용 설명 파일(role `other`, download false)에 적는다.
   - **v0 지침**(role `guideline`, download true): 지침서 5항목 중 일부가 추상적이거나 비어 있는 초안. 파일 첫머리에 "일부러 단순하게 만든 초안"임을 밝힌다(CD-18).
   - 필요하면 README 성격의 안내 파일(role `other`).
2. **D1-01과의 일관성**(D1-01은 reviewed라 바꿀 수 없다):
   - 체험 질문("지난달에 이사했는데 전입신고를 아직 못 했어요…")과 기준 질문 1~4는 가상 규정·FAQ로 답할 수 있어야 한다.
   - 기준 질문 5(자동차 주소)는 **자료에 없음 → "확인 필요"** 사례로 남긴다. 규정·FAQ에 넣지 않는다.
3. `content/kits/day1-civil/kit.yaml` — PRACTICE_CASES 1절 스키마를 **직접** 따른다:
   - 필수: `id: day1-civil`, `title`, `track: core`, `sources`, `privacy_notes`, `fictional_label`, `files`
   - `files[]`는 폴더의 **모든** 자료 파일(kit.yaml 제외)을 `path`, `role`, `download`, `description`으로 적는다.
   - `sources`에는 아래 4에서 등록한 fictional ID만 넣는다. 실제 법령 ID(`law-*`)를 넣지 않는다(CD-21).
4. `content/sources.yaml`에 가상 규정을 **추가만** 한다:
   - `id: fictional-day1-move-in-rule`(형식 `fictional-<kit>-<주제>`), `type: fictional`
   - `title`에 "(교육용 가상)"을 넣는다(`<Source>`가 제목을 그대로 표시한다).
   - `articles`: 가상 규정의 조문 목록(`제N조(제목)`), `url: null`, `note`(가상 표기 방법), `accessed_at`(오늘 날짜), `license: 프로젝트 자체 제작(가상)`
5. `content/course.yaml`의 `kits`에 항목 1개를 추가한다: `{id: day1-civil, title: <kit.yaml title과 같게>, status: draft}`. **kits 항목 외에는 아무것도 바꾸지 않는다.**

## 수정 허용 경로

`content/kits/day1-civil/*`, `content/sources.yaml`(추가만), `content/course.yaml`(`kits` 항목만). 이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify -- --scope kit:day1-civil
```

## 검증 절차

1. 위 AC 커맨드를 실행한다. V-KIT-001·V-REG-002·V-PII-001 오류가 0이어야 한다.
2. `git diff content/course.yaml`에 `kits` 항목 추가 외의 변경이 없는지, `git diff content/sources.yaml`이 추가뿐인지 확인한다.
3. 체크리스트:
   - 모든 자료 파일 첫머리에 가상 자료 표기가 있는가? 이름은 명백한 가상 이름, 전화번호는 `010-0000-XXXX`만 쓰는가?
   - 가상 규정에 실제 법령명·법령 번호·과태료 금액이 없는가?
   - D1-01 기준 질문 1~4와 체험 질문에 답할 근거가 있고, 5는 없는가?
4. 결과에 따라 `phases/2-day1-content/index.json`의 step 1을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일 목록, fictional 출처 ID와 조문 수, 의도된 결함(빠뜨린 FAQ 항목)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `npm run new:kit`을 실행하지 마라. 이유: `scripts/scaffold/kit.yaml`이 옛 스키마(`context_files` 등)를 쓴 적이 있고, 옛 필드가 남아도 V-KIT-001이 잡지 못한다. PRACTICE_CASES 1절 스키마로 직접 작성한다.
- 실제 법령 원문을 옮기거나 실제 법령 ID를 키트 sources에 넣지 마라. 이유: CD-21.
- 평가 문항·기대 답변 파일을 만들지 마라. 이유: step 2의 일이다.
- course.yaml에서 교시·카드 항목이나 다른 값을 바꾸지 마라. 이유: 이 step의 course.yaml 권한은 kits 항목 추가뿐이다.
- 키트 status를 reviewed로 올리거나 reviewed_hash를 쓰지 마라. 이유: 승인은 사람만 한다(ADR-011).
- 실제 개인정보·실제 기관 문서를 쓰지 마라.
- 기존 테스트를 깨뜨리지 마라.
