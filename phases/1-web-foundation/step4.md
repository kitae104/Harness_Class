# Step 4: authoring-tools

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md` — status·reviewed_hash 규칙
- `/docs/ARCHITECTURE.md` — 10절 검토 상태와 승인(해시 규칙), 11절 확장 절차(생성 명령)
- `/docs/ADR.md` — ADR-005(사람 검토 관문, LF 정규화), ADR-011(상태는 course.yaml에만)
- `/docs/QUALITY_CHECKLIST.md` — V-REV-001, V-REV-002, 구현 열 규칙
- `/docs/CONTENT_GUIDE.md` — 1절 교시 유형별 섹션(뼈대 파일에 반영)
- `/docs/PROMPT_GUIDE.md` — 2절 카드 필드, 3절 5칸 뼈대
- `/scripts/validate_course.py`, `/scripts/test_validate_course.py` — 규칙 등록부 `RULES`, `check_reviewed`, `_resolve_scope`
- `/content/course.yaml`
- step 0~3 산출물: `/package.json`, `/src/content.config.ts`(교시 `lesson_id`, 카드 frontmatter)

## 작업 목적

콘텐츠 작성자가 쓰는 도구 두 가지를 만든다.
1. **뼈대 생성 명령**: 교시·모듈·카드·키트의 빈 파일을 규칙에 맞게 만든다.
2. **사람 승인 명령**: 사람이 검토를 마친 콘텐츠의 해시를 course.yaml에 기록하고, validator가 승인 이후의 수정을 잡아내게 한다.

## 수정/생성 대상

- 생성: `scripts/content_hash.py`, `scripts/test_content_hash.py`, `scripts/review_approve.py`, `scripts/test_review_approve.py`, `scripts/new_content.mjs`, `scripts/scaffold/lesson-concept.mdx`, `scripts/scaffold/lesson-practice.mdx`, `scripts/scaffold/lesson-project.mdx`, `scripts/scaffold/prompt.md`, `scripts/scaffold/module.mdx`, `scripts/scaffold/kit.yaml`, `tests/unit/new-content.test.ts`
- 수정: `scripts/validate_course.py`, `scripts/test_validate_course.py`, `docs/QUALITY_CHECKLIST.md`(V-REV-002 구현 열을 `구현`으로), `package.json`(scripts만)

## 작업 범위

1. **`scripts/content_hash.py`** (TDD)
   ```python
   def normalized_bytes(path: Path) -> bytes   # UTF-8로 읽고 CRLF·CR을 LF로 바꾼 바이트
   def content_hash(path: Path) -> str         # "sha256:<hex>"
   def target_file(root: Path, kind: str, item: dict) -> Path
       # kind="lesson" → content/day{day}/{number:02d}.mdx
       # kind="card"   → content/prompts/{id}.md
   ```
   - **핵심 규칙: 같은 내용이면 CRLF 파일과 LF 파일의 해시가 같아야 한다.** 테스트로 보장한다. 이유: Windows 작업 폴더는 CRLF, CI는 LF다.
2. **`scripts/review_approve.py`** (TDD)
   - 사용법: `python scripts/review_approve.py <id> [--root .]`. `<id>`는 교시 ID 또는 카드 ID.
   - 대상 콘텐츠 파일이 없으면 오류로 끝낸다(non-zero).
   - course.yaml 해당 항목의 `status`를 `reviewed`로 바꾸고 `reviewed_hash`를 기록한다.
   - **course.yaml을 쓸 때 다른 내용(주석, 키 순서, 인라인 `{...}` 형식)을 망가뜨리지 않는다.** yaml을 통째로 다시 dump하지 말고, 해당 항목의 줄만 텍스트로 수정하는 방식을 쓴다. 대상 줄을 못 찾으면 오류로 끝낸다.
   - 콘텐츠 파일은 수정하지 않는다.
   - 실행 전후를 한 줄로 출력한다: `d1-harness-intro: draft → reviewed (sha256:ab12…)`.
   - 이 명령은 사람이 실행한다. step 안에서 실제 콘텐츠에 대해 실행하지 마라(테스트는 임시 폴더에서).
3. **validator에 V-REV-002 추가** (TDD, `scripts/validate_course.py`)
   - status가 `reviewed`인 교시·카드에 대해 `content_hash(target_file)`와 `reviewed_hash`를 비교한다. 다르면 오류 "승인 후 수정됨 — 다시 검토 필요". 파일이 없거나 `reviewed_hash`가 없으면 오류.
   - `RULES`에 V-REV-002를 추가하고, `docs/QUALITY_CHECKLIST.md`의 V-REV-002 구현 열을 `구현`으로 바꾼다(V-QUA-001이 대조한다).
   - `--require-reviewed`(V-REV-001)의 기존 동작은 바꾸지 않는다.
4. **`scripts/new_content.mjs`** — 뼈대 생성 명령.
   - package.json scripts:
     - `new:lesson` → `node scripts/new_content.mjs lesson <lesson-id>`
     - `new:module` → `node scripts/new_content.mjs module <slug>`
     - `new:prompt` → `node scripts/new_content.mjs prompt <card-id>`
     - `new:kit` → `node scripts/new_content.mjs kit <kit-id>`
     - `review:approve` → Node 래퍼가 python을 골라(`scripts/verify.mjs`의 `pickPython`을 import해 재사용) `scripts/review_approve.py`를 실행
   - lesson: course.yaml에서 교시를 찾아 유형에 맞는 scaffold를 `content/day{d}/{nn}.mdx`로 복사하고 `lesson_id`를 채운다. 교시가 course.yaml에 없으면 오류. 파일이 이미 있으면 덮어쓰지 않고 오류.
   - prompt: course.yaml `cards`에 없는 ID면 오류("먼저 막힘 지점과 카드를 course.yaml에 등록하라").
   - module·kit: 대상 폴더에 scaffold를 복사한다. course.yaml은 수정하지 않고, 등록할 한 줄을 안내 메시지로 출력한다.
   - **course.yaml과 다른 등록부를 수정하지 않는다.**
   - 순수 함수(대상 경로 계산, 이름 검증)는 export하고 `tests/unit/new-content.test.ts`로 테스트한다(TDD).
5. **scaffold 내용**
   - 교시 뼈대에는 CONTENT_GUIDE 1절의 공통 필수 섹션 제목과 유형별 섹션 제목만 둔다. 본문은 "작성 예정"으로 둔다.
   - 카드 뼈대에는 PROMPT_GUIDE 2절 필드와 3절 5칸 뼈대를 둔다.
   - 가상 자료 표기 문구 자리를 둔다.

## 수정 허용 경로

`scripts/content_hash.py`, `scripts/review_approve.py`, `scripts/new_content.mjs`, `scripts/scaffold/*`, `scripts/test_content_hash.py`, `scripts/test_review_approve.py`, `scripts/validate_course.py`, `scripts/test_validate_course.py`, `docs/QUALITY_CHECKLIST.md`, `package.json`, `tests/unit/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
python -m pytest scripts/test_content_hash.py scripts/test_review_approve.py -q
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 임시 폴더에서 다음을 확인한다.
   - `node scripts/new_content.mjs lesson <없는 ID>`가 non-zero로 끝나는가
   - 이미 있는 파일을 덮어쓰지 않는가
3. `git diff content/`가 비어 있는지 확인한다(실제 콘텐츠와 등록부를 바꾸지 않았음).
4. 아키텍처 체크리스트:
   - 해시가 LF 정규화 후 계산되는가(테스트 존재)?
   - review_approve가 course.yaml의 주석·형식을 보존하는가(테스트 존재)?
   - 기존 validator 규칙의 동작이 그대로인가(기존 테스트 통과)?
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 4를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "생성 명령·승인 명령·V-REV-002 추가와 해시 규칙을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 실제 `content/course.yaml`에 대해 review_approve를 실행하지 마라. 어떤 항목도 reviewed로 바꾸지 마라. 이유: reviewed는 사람만 올린다(CLAUDE.md CRITICAL, ADR-005).
- course.yaml을 `yaml.safe_dump`로 통째로 다시 쓰지 마라. 이유: 주석과 인라인 형식이 사라지고 모든 줄이 바뀐다.
- 줄바꿈 정규화 없이 해시를 계산하지 마라. 이유: Windows와 CI에서 해시가 달라 모든 승인이 깨진다.
- 뼈대 생성 명령이 course.yaml이나 다른 등록부를 수정하게 만들지 마라. 이유: 등록부 변경은 사람이 설계 단계에서 한다.
- `content/` 아래에 파일을 만들지 마라. 이유: 이 step은 도구만 만든다.
- 기존 테스트를 깨뜨리지 마라.
