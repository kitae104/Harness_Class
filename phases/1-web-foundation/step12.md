# Step 12: d1-01-revise

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 배경을 파악하라:

- `/CLAUDE.md` — status 규칙, course.yaml 수정 예외(자기 교시 항목만)
- `/docs/CONTENT_GUIDE.md` — 전체(step 8에서 보완한 1·4·5·8절)
- `/docs/LEARNING_OBJECTIVES.md` — 2·3절(학습목표↔결과 확인 연결)
- `/docs/PRACTICE_DESIGN.md` — AI 왕복 활동 시간 기준(step 8에서 추가), 2절 전/후 비교
- `/docs/HARNESS_ELEMENTS.md`, `/docs/QUALITY_CHECKLIST.md` — 3절 루브릭(이 수정의 기준)
- `/content/course.yaml` — `d1-harness-intro` 항목
- `/content/product-features.yaml` — `chatgpt-temporary-chat`(detail, fallback)
- `/content/sources.yaml` — `law-resident-registration`(제16조, 제40조)
- `/content/external-links.yaml` — `sheet-harness-ledger`(fallback_templates `baseline`)
- `/content/glossary.yaml` — `harness-ledger`, `unpersonalized-chat`
- `/content/day1/01.mdx`, `/content/instructor/day1/01.md`
- step 9~11 산출물: `/src/components/Feature.astro`(show 속성), `/src/components/ExternalLink.astro`(tab 속성), `/src/layouts/LessonLayout.astro`, `/src/components/InstructorNotes.astro`

## 배경 (사람 검토에서 나온 D1-01 문제)

| # | 문제 | 수정 |
|---|---|---|
| A1 | 체험 질문에 과태료("늦으면 어떻게 되나요")가 있는데 근거로 제16조만 들었다 | 제16조와 제40조를 함께 `<Source>`로 인용한다. 판정은 여전히 D1-4로 넘긴다 |
| A2 | "잘 안 될 때"의 대안 문구를 본문에 다시 써서 등록부 fallback(메모리·맞춤 지침을 끈 새 대화)과 어긋났다 | 본문 문구를 지우고 `<Feature id="chatgpt-temporary-chat" show="fallback"/>`로 표시한다 |
| A3 | 목표 1("설명한다")과 목표 2("말한다")를 확인하는 활동과 결과 확인이 없다 | 목표마다 수강생이 증거를 남기는 활동을 넣는다: 짝에게 한 문장으로 설명하기, 6요소 이름 체크. course.yaml에 결과 확인과 "6요소 메모" 산출물을 추가한다 |
| A4 | "비개인화 임시 채팅"과 "하네스 대장"이 설명 없이 등장한다 | 처음 나올 때 한 줄로 풀어 쓴다. `<Feature ... show="detail"/>`를 활용한다 |
| A5 | 두 답이 거의 같게 나올 때 볼 예시가 없다 | (선택) 두 답이 다른 가상 예시를 접이식으로 둔다. "교육용 가상 자료"로 표기하고, 법령 내용을 단정하지 않는다 |
| A6 | 기록할 곳이 없고, 5분 안에 5개를 묻고 요약하는 일정이 비현실적이다 | `<ExternalLink id="sheet-harness-ledger" tab="baseline"/>`로 표 양식을 표시한다. 기록은 "답 붙여 넣기 + 근거를 밝혔나(예/아니오)"로 줄인다. 활동 분을 B6 기준으로 조정한다 |

## 작업 목적

D1-01을 루브릭 네 항목이 모두 2점이 되도록 고친다. 개념형 기준 예시로서, 이후 개념형 교시가 따를 모범이 되어야 한다.

## 수정/생성 대상

- 수정: `content/day1/01.mdx`, `content/instructor/day1/01.md`
- 수정: `content/course.yaml` — **`d1-harness-intro` 항목 안에서만**: activities, objectives, outputs, checks, stuck_points, skip_if_short
- 필요하면 수정: `public/images/d1-harness-intro/*`(그림 A는 문제가 지적되지 않았으므로 바꾸지 않는 것이 기본)

## 작업 범위

1. **course.yaml `d1-harness-intro` 항목**
   - `checks`를 `{id, text}` 형식으로 바꾼다(ID 예: `d1-01-c1` …).
   - 결과 확인 최소 3개:
     - 기준 질문 5개와 답이 대장(또는 표 양식)에 기록되어 있다
     - 짝에게 "같은 질문에 답이 달랐던 이유와 하네스가 필요한 이유"를 한 문장으로 말했다
     - 6요소 이름을 모두 체크했다
   - `objectives[].checks`로 목표 1·2를 각각 결과 확인에 연결한다.
   - 산출물 `d1-01-p2`("6요소 한 줄 메모")를 추가하고 목표 2와 연결한다. `used_by`는 `d2-project-design`(설계서 6칸 작성에 쓰임).
   - activities를 PRACTICE_DESIGN의 AI 왕복 시간 기준에 맞게 조정한다. 권장안:
     - 입과 10(CD-11 고정)
     - 체험 10
     - 개념 8
     - 짝 설명·6요소 체크 2 (`check`)
     - 기준 질문 기록 10
     - 합계 40 = constraints.max_core_minutes 이하
   - 막힘 지점에 "기록할 곳이 없다"(지원 방식 3·9)와 "비개인화가 무엇인지 모른다"(지원 방식 6·7)를 추가할 수 있다. 기존 ID는 바꾸지 않는다.
   - `status`는 `draft`를 유지한다. **다른 교시 항목, cards, constraints 등은 바꾸지 않는다.**
2. **`content/day1/01.mdx`**: A1~A6을 반영한다.
   - CONTENT_GUIDE의 섹션 구조와 본문 첫 섹션 규칙(이번 시간에 할 일·필수 경로)을 유지한다.
   - 필수 경로는 새 활동(짝 설명·6요소 체크, 기록)을 반영해 3~5단계로 다시 쓴다.
   - 등록부 정보는 모두 컴포넌트로 표시한다(`Feature show`, `ExternalLink tab`, `Source`).
3. **`content/instructor/day1/01.md`**: 짝 설명 진행 방법, 표 양식 기록 안내, 조정된 생략 항목(course.yaml `skip_if_short`와 일치)을 반영한다. 공개 가능한 진행 안내만 쓴다(CD-02).
4. 문체: "~합니다" 강의체, 한 문장 60자 안팎, 한 문단 3문장 이내, 수강생 화면 용어.

## 수정 허용 경로

`content/day1/01.mdx`, `content/instructor/day1/01.md`, `public/images/d1-harness-intro/*`, `content/course.yaml`(`d1-harness-intro` 항목 안에서만)

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-harness-intro
npm run verify
npm run build:offline
npm run test:e2e
```

## 검증 절차

1. 위 AC 커맨드를 실행한다. step 9 이후 실패하던 `npm run verify` 전체가 이제 통과해야 한다(V-LSN-005 해소).
2. `git diff content/course.yaml`이 `d1-harness-intro` 항목 안만 바꿨는지 확인한다.
3. `python scripts/validate_course.py --scope phase:1-web-foundation --require-reviewed`를 실행한다. **오류가 V-REV-001(아직 draft)뿐인지** 확인한다. V-LNK-001 오류가 있으면 안 된다.
4. 루브릭 자가 점검(사람 검토를 대신하지 않음). QUALITY_CHECKLIST 3절 네 항목에 대해 이 수정이 무엇을 보완했는지 summary에 적는다.
5. 결과에 따라 `phases/1-web-foundation/index.json`의 step 12를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "A1~A6 반영 내용, course.yaml 변경(checks 연결·p2 산출물·활동 분), 남은 V-REV-001만 있음을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 규칙을 어기지 않고는 해결할 수 없는 문제(예: 규칙끼리 충돌)가 있으면 → `"status": "error"`, `"error_message": "충돌하는 규칙과 위치"` 후 중단

## 금지사항

- status를 `reviewed`로 올리거나 `reviewed_hash`를 쓰지 마라. 이유: 사람만 승인한다(ADR-005, ADR-011).
- course.yaml에서 `d1-harness-intro` 밖의 줄을 바꾸지 마라. 이유: 공유 등록부이고 다른 교시는 각자의 step이 작성한다.
- 기존 ID(목표·산출물·막힘 지점)를 바꾸거나 지우지 마라. 추가만 한다. 이유: CLAUDE.md CRITICAL(ID 불변).
- 등록부의 대안·설명·표 양식을 본문에 다시 쓰지 마라. 이유: 등록부와 어긋난다(B3, D1-01 사례).
- 전입신고 기한, 과태료 금액을 본문에 단정하지 마라. 이유: 판정은 D1-4에서 근거 자료로 한다. 과태료 금액은 원문 확인 전이다(OQ-07).
- 카드(`content/prompts/*`)를 만들지 마라. Codex를 언급하지 마라.
- 기존 테스트를 깨뜨리지 마라.
