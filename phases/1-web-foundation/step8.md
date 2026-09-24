# Step 8: review-rules-docs

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 배경을 파악하라:

- `/CLAUDE.md`
- `/docs/QUALITY_CHECKLIST.md` — 3절 사람 검토 루브릭, 1절 규칙 표(구현 열 규칙)
- `/docs/LEARNING_OBJECTIVES.md` — 2절 목표 작성 규칙, 3절 결과 확인 작성 규칙
- `/docs/CONTENT_GUIDE.md` — 1절 템플릿, 4절 용어, 5절 직접 쓰지 않는 것
- `/docs/PRACTICE_DESIGN.md`, `/docs/UI_GUIDE.md`, `/docs/ARCHITECTURE.md`(2절 데이터 흐름, 4절 스키마, 6절 컴포넌트 규약, 8절 강사 안내), `/docs/PRODUCT_FEATURES.md`
- `/content/external-links.yaml`, `/content/glossary.yaml`, `/content/course.yaml`(`d1-harness-intro` 항목)
- `/content/day1/01.mdx` — 사람 검토에서 문제가 발견된 개념형 기준 예시
- `/src/components/Feature.astro`, `/src/components/ExternalLink.astro`, `/src/layouts/LessonLayout.astro` — 현재 동작 확인용(수정하지 않는다)

## 배경 (사람 검토 결과)

사람이 D1-01을 QUALITY_CHECKLIST 3절 루브릭으로 검토했다. 결과는 목표 달성 1 · 초보자 지원 1 · 하네스 관점 2 · 정확성 1로 승인되지 않았다. 원인 대부분은 **이후 모든 교시에서 반복될 규칙 공백**이다. 이 step은 그 규칙을 docs와 등록부에 먼저 반영한다. 코드와 D1-01 수정은 step 9~12가 한다.

| ID | 발견된 문제 | 규칙 보완 방향 |
|---|---|---|
| B1 | 학습목표를 확인하는 결과 확인이 없어도 검증을 통과한다(목표 2개가 산출물 하나만 가리키고, 결과 확인도 1개) | 학습목표마다 그것을 확인하는 결과 확인 항목을 연결한다 |
| B2 | 준비 전(planned) 외부 링크를 참조하고, 그 대안이 존재하지 않는 자료("빌드 시 생성되는 xlsx")를 가리킨다 | 외부 링크의 대안은 지금 바로 쓸 수 있어야 한다. 표 양식은 등록부에 두고 컴포넌트가 표시한다 |
| B3 | 기능의 대안 문구를 본문에 다시 써서 등록부와 어긋났다. `<Feature>`는 상세 설명과 대안을 표시하지 않는다 | 대안·설명은 등록부에서 컴포넌트로 표시하고 본문 재서술을 금지한다 |
| B4 | 강사 안내가 페이지에 렌더링되지 않는다 | 규칙은 이미 있음(ARCHITECTURE 8절). step 11이 구현한다. 이 step에서는 문서를 바꾸지 않는다 |
| B5 | CONTENT_GUIDE는 "필수 경로를 맨 위에"라고 하지만 레이아웃은 학습목표를 먼저 표시한다 | 레이아웃에 맞춰 문구를 정정한다 |
| B6 | AI에게 여러 번 묻는 활동의 시간 기준이 없어 분 배분이 비현실적이다 | AI 왕복 활동 시간 기준을 추가한다 |
| B7 | 과정 고유 용어("하네스 대장", "비개인화")가 설명 없이 등장한다 | 용어집에 등록하고 첫 등장 설명 규칙을 추가한다 |

## 작업 목적

B1~B3, B5~B7의 규칙을 docs와 등록부에 반영한다. step 9~12가 이 규칙을 읽고 구현·수정한다.

## 수정/생성 대상

- 수정: `docs/LEARNING_OBJECTIVES.md`, `docs/CONTENT_GUIDE.md`, `docs/PRACTICE_DESIGN.md`, `docs/UI_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/PRODUCT_FEATURES.md`, `docs/QUALITY_CHECKLIST.md`
- 수정: `content/glossary.yaml`(항목 추가만), `content/external-links.yaml`(`sheet-harness-ledger` 항목만)

## 작업 범위

1. **B1 — 학습목표와 결과 확인 연결**
   - `LEARNING_OBJECTIVES.md` 3절: 결과 확인은 `{id, text}` 형식으로 쓰고, 학습목표마다 `checks`(결과 확인 ID 목록)로 연결한다. 규칙: 학습목표마다 결과 확인이 1개 이상 있다. 결과 확인은 수강생이 스스로 확인할 수 있는 관찰 가능한 문장이다.
   - `CONTENT_GUIDE.md` 8절 작성 순서: "학습목표마다 수강생이 증거를 남기는 활동(말하기·쓰기·체크·기록)을 본문에 둔다"를 추가한다.
   - `ARCHITECTURE.md` 4절 스키마 표: `lessons[].objectives[].checks`, `lessons[].checks[]`의 `{id, text}` 형식을 적는다. 기존 문자열 형식은 planned 교시에서만 허용되는 과거 형식이라고 적는다.
2. **B2 — 외부 링크의 대안**
   - `ARCHITECTURE.md` 2절·6절: `external-links.yaml`에 `fallback_kind`(`template` | `download` | `none`)와 `fallback_templates`(탭 이름 → 열 이름 목록)를 둔다. `<ExternalLink id tab>`는 링크가 준비되기 전이면 해당 탭의 표 양식을 복사 가능한 형태로 표시한다.
   - `CONTENT_GUIDE.md` 5절 표에 한 줄 추가: 준비 전 외부 자원을 참조하려면 등록부에 바로 쓸 수 있는 대안(`fallback_kind: template` 또는 실제 존재하는 다운로드)이 있어야 한다.
   - `content/external-links.yaml`의 `sheet-harness-ledger` 항목:
     - `fallback`을 "아래 표 양식을 복사해 메모장이나 내 구글 시트에 붙여 넣어 기록합니다(대장 템플릿 준비 전 임시)"로 바꾼다.
     - `fallback_kind: template`을 추가한다.
     - `fallback_templates`에 `baseline`(기준 질문 기록) 탭을 추가한다. 열: 번호, 질문, 답(붙여 넣기), 근거를 밝혔나(예/아니오), 메모.
     - **다른 항목과 다른 필드는 바꾸지 않는다.**
3. **B3 — 등록부 정보는 컴포넌트로 표시**
   - `ARCHITECTURE.md` 6절: `Feature`에 `show` 옵션(`detail` | `fallback`)을 추가한다. `detail`은 등록부 `detail`을, `fallback`은 등록부 `fallback`을 본문 안에 표시한다.
   - `CONTENT_GUIDE.md` 5절: 기능의 대안·상세 설명을 본문에 다시 쓰지 않고 `<Feature id show="fallback"/>`·`<Feature id show="detail"/>`로 표시한다는 줄을 추가한다. 이유: 등록부와 어긋난다(D1-01 사례).
   - `UI_GUIDE.md` 컴포넌트 절: `Feature`의 두 표시 형식과 `ExternalLink` 대안 표 양식의 모양(표 + 복사 버튼)을 적는다.
   - `PRODUCT_FEATURES.md` 2절 `fallback` 설명: "본문은 `<Feature show="fallback">`으로만 표시한다"를 덧붙인다.
4. **B5 — 필수 경로 위치**: `CONTENT_GUIDE.md` 1절의 "필수 경로는 페이지 맨 위에 둔다"를 "학습목표는 레이아웃이 자동 표시하므로, 본문의 첫 섹션은 '이번 시간에 할 일'과 '필수 경로'로 시작한다"로 정정한다.
5. **B6 — AI 왕복 활동 시간 기준**: `PRACTICE_DESIGN.md`에 절을 추가한다.
   - 초보자 기준으로 AI 질문 1회(붙여 넣기 → 답 읽기 → 기록)에 최소 2분을 잡는다.
   - 활동 분은 "질문 수 × 2분 + 비교·정리 시간" 이상으로 설계한다.
   - 기록 항목은 판단 하나(예/아니오 등)와 붙여 넣기로 줄인다.
6. **B7 — 과정 고유 용어**
   - `content/glossary.yaml`에 두 항목을 추가한다(기존 항목 수정 금지, `student_label` 포함):
     - `harness-ledger`: "하네스 대장" — 지침 버전·자료 목록·평가·로그를 기록하는 시트
     - `unpersonalized-chat`: "비개인화 임시 채팅" — 메모리와 맞춤 지침을 쓰지 않는 임시 채팅
   - `CONTENT_GUIDE.md` 4절: "과정 고유 용어는 처음 나올 때 한 줄로 풀어 쓴다"를 추가한다.
7. **QUALITY_CHECKLIST 1절**: step 9가 구현할 규칙 두 개를 `예정(P1)`으로 추가한다.
   - `V-LSN-005`(AUTO-오류): draft·reviewed 교시는 학습목표마다 결과 확인이 연결되어 있다. planned 교시는 경고.
   - `V-LNK-001`(AUTO-경고, `--require-reviewed`에서 오류): 교시가 준비 전 외부 링크를 참조하는데 그 링크의 `fallback_kind`가 `template`이 아니거나 실제 다운로드 파일이 없다.

## 수정 허용 경로

`docs/LEARNING_OBJECTIVES.md`, `docs/CONTENT_GUIDE.md`, `docs/PRACTICE_DESIGN.md`, `docs/UI_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/PRODUCT_FEATURES.md`, `docs/QUALITY_CHECKLIST.md`, `content/glossary.yaml`, `content/external-links.yaml`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다. V-QUA-001이 새 `예정(P1)` 행을 받아들이는지, V-TAG-001·V-DOC-002가 오류 0인지 확인한다.
2. `git diff content/external-links.yaml`이 `sheet-harness-ledger` 항목만 바꿨는지 확인한다.
3. `git diff content/glossary.yaml`이 추가뿐인지 확인한다.
4. 아키텍처 체크리스트:
   - 문서 사이에 서로 모순되는 문장이 남지 않았는가(특히 CONTENT_GUIDE 1절과 5절, ARCHITECTURE 6절)?
   - 수치를 docs에 직접 쓰지 않았는가(시간 기준 "질문 1회 2분"은 설계 원칙이므로 허용)?
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 8을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "B1~B3·B5~B7 규칙 반영 위치와 external-links fallback_kind·templates 필드를 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 코드(`src/*`, `scripts/*`)를 수정하지 마라. 이유: 규칙 구현은 step 9~11의 범위다.
- `content/day1/01.mdx`와 `content/course.yaml`을 수정하지 마라. 이유: D1-01 수정은 step 12의 범위다.
- `content/external-links.yaml`에서 `sheet-harness-ledger` 외 항목을 바꾸지 마라. `content/glossary.yaml`의 기존 항목도 바꾸지 마라. 이유: 공유 등록부는 소유 항목만 수정한다.
- QUALITY_CHECKLIST의 기존 규칙 행 의미를 바꾸지 마라. 이유: validator와 테스트가 의존한다.
- 기존 테스트를 깨뜨리지 마라.
