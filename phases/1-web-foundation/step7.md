# Step 7: validator-web

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/QUALITY_CHECKLIST.md` — 1절 규칙 표(예정 규칙), 5절 배포 관문
- `/docs/ARCHITECTURE.md` — 3절 스키마 담당, 5절 URL 규칙, 7절 오프라인, 10절 검토 상태
- `/docs/ADR.md` — ADR-004(검사 담당), ADR-011
- `/docs/CONTENT_GUIDE.md` — 1절 유형별 필수 섹션, 5절 직접 쓰면 안 되는 것
- `/docs/PROMPT_GUIDE.md` — 2절 카드 필드, 4절 대괄호↔replace
- `/docs/LEARNING_OBJECTIVES.md` — 2절 목표 동사 규칙
- `/.claude/commands/harness.md` — human-review step 규칙(`review_targets`, `--scope phase:`)
- `/scripts/validate_course.py`, `/scripts/test_validate_course.py`, `/scripts/content_hash.py`
- `/phases/1-web-foundation/index.json` — `review_targets` 예시
- step 2·5·6 산출물: `/src/pages/course/[day]/[num].astro`, `/content/day1/01.mdx`, `/scripts/build_offline.mjs`

## 작업 목적

사이트와 콘텐츠가 생긴 뒤에야 검사할 수 있는 규칙을 Python 검증기에 추가한다. 추가하는 것은 교시·카드 파일 규칙, 빌드 결과 규칙, 그리고 human-review step이 쓰는 `phase:` 범위다.

## 수정/생성 대상

- 수정: `scripts/validate_course.py`, `scripts/test_validate_course.py`, `docs/QUALITY_CHECKLIST.md`(구현한 규칙의 구현 열을 `구현`으로, 새 규칙 행 추가)

## 작업 범위 (모두 TDD: 규칙마다 실패하는 테스트를 먼저 쓴다)

1. **V-LSN-001 (오류)**: `content/day{d}/{nn}.mdx`의 frontmatter `lesson_id`가 같은 위치(day, number)의 course.yaml 교시 ID와 일치한다. course.yaml에 없는 교시 파일은 오류다. status가 draft·reviewed인데 파일이 없어도 오류다.
2. **V-LSN-002 (오류)**: 교시 MDX에 CONTENT_GUIDE 1절 공통 필수 섹션 제목이 있다. 실습형은 "예상 결과"와 "잘못된 결과 예시" 섹션도 있어야 한다. 제목 문자열 목록은 validator 상수로 두고, CONTENT_GUIDE와 같은 표현을 쓴다.
3. **V-LSN-003 (경고)**: 학습목표가 "이해한다/안다/알아본다"로 끝나면 경고. 교시 본문에서 한 문장이 120자를 넘으면 경고.
4. **V-LSN-004 (경고, 새 규칙)**: 교시 MDX 본문에 제품 정보를 직접 쓴 흔적이 있으면 경고.
   - 대상 패턴: `설정 >`, `> 데이터 제어` 같은 메뉴 경로 화살표, "파일 N개", "N MB", "N GB"
   - 코드 블록과 컴포넌트 태그 안은 제외한다.
   - QUALITY_CHECKLIST 1절에 행을 추가한다.
5. **V-PRM-001 (오류)**: `content/prompts/*.md`마다 course.yaml `cards`에 같은 ID가 있다. frontmatter 필수 필드가 있다. `l2_template`·`l1_full`의 대괄호 목록과 `replace` 목록이 일치한다. course.yaml에서 status가 draft·reviewed인 카드는 파일이 있어야 한다.
6. **V-PRM-002 (오류)**: course.yaml level이 3인 카드는 파일에 `l2_template`가 비어 있지 않다.
7. **V-PRM-003 (경고)**: 카드 `tested_at`이 없거나 constraints.freshness_days를 넘었다.
8. **V-WEB-001 (오류)**: `dist/`의 HTML에서 내부 링크(`href="/..."`)와 이미지 경로가 실제 파일을 가리킨다. `dist/`가 없으면 규칙을 건너뛰고 정보 메시지를 남긴다. `--docs-only`에서는 건너뛴다.
9. **V-WEB-002 (오류)**:
   - `dist/`와 `dist-offline/`(있으면)에 외부 URL을 불러오는 `<script src>`, `<link rel="stylesheet">`, `@font-face url(http...)`이 없다.
   - `<script type="module"`이 없다.
   - `dist-offline/`의 내부 링크는 상대경로다.
   - `--docs-only`에서는 건너뛴다.
10. **`--scope phase:<dir>` 구현**:
    - `phases/<dir>/index.json`의 `review_targets`(`lesson:<id>`, `card:<id>` 목록)를 읽어 그 항목만 검사 범위로 삼는다.
    - `review_targets`가 없거나 phase 폴더가 없으면 V-CLI-001 오류.
    - `--require-reviewed`와 함께 쓰면 그 항목들만 reviewed인지 본다.
    - `card:<id>` 범위도 지원한다.
11. **QUALITY_CHECKLIST**
    - 구현한 규칙(V-LSN-001~004, V-PRM-001~003, V-WEB-001~002)의 구현 열을 `구현`으로 바꾼다.
    - 구현하지 않은 규칙은 `예정(Pn)`으로 둔다.
    - V-QUA-001이 표와 코드를 대조하므로 둘이 정확히 일치해야 한다.

## 수정 허용 경로

`scripts/validate_course.py`, `scripts/test_validate_course.py`, `docs/QUALITY_CHECKLIST.md`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
python scripts/validate_course.py --scope phase:1-web-foundation
```

## 검증 절차

1. 위 AC 커맨드를 실행한다. 두 번째 명령은 오류 0이어야 한다(`--require-reviewed` 없이).
2. `python scripts/validate_course.py --scope phase:1-web-foundation --require-reviewed`가 **V-REV-001 오류로 실패하는지** 확인한다(D1-01이 아직 draft이므로 정상적인 실패다). 실패 메시지에 `d1-harness-intro`가 있어야 한다.
3. `python scripts/validate_course.py --docs-only`가 dist 없이도 오류 0인지 확인한다.
4. 아키텍처 체크리스트:
   - 기존 규칙의 동작이 그대로인가(기존 테스트 전부 통과)?
   - zod가 이미 하는 검사(frontmatter 필드 타입)를 중복하지 않았는가? V-PRM-001은 **course.yaml과의 교차 규칙**에 집중한다(ADR-004).
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 7을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "추가한 규칙 ID와 phase/card 범위 지원을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 콘텐츠(`content/*`)를 고쳐서 규칙을 통과시키지 마라. D1-01이 새 규칙에 걸리면 규칙이 CONTENT_GUIDE와 맞는지 먼저 확인한다. 규칙이 맞다면 error_message에 위반 내용을 보고하라. 이유: 콘텐츠는 허용 경로가 아니고 사람 검토 대상이다.
- 기존 26개 규칙의 ID·의미·수준을 바꾸지 마라. 이유: QUALITY_CHECKLIST와 테스트가 그 의미에 의존한다.
- 네트워크에 접속해 링크를 검사하지 마라. 외부 URL은 존재 여부만 검사한다. 이유: 교육망·CI에서 불안정하다.
- `--docs-only`에서 빌드 결과를 요구하지 마라. 이유: Phase 1 이전 AC와 Stop 훅 호환.
- 기존 테스트를 깨뜨리지 마라.
