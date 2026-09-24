# Step 6: d1-03-project

## 읽어야 할 파일

- `/CLAUDE.md` — CRITICAL 규칙, course.yaml 수정 예외 범위
- `/docs/CONTENT_GUIDE.md`, `/docs/PRACTICE_DESIGN.md`(2절 전/후 비교, 6절 빼보기 실험, 9절 시간), `/docs/TOOL_GUIDE.md`(Project·지침란·파일), `/docs/LEARNING_OBJECTIVES.md`, `/docs/HARNESS_ELEMENTS.md`, `/docs/UI_GUIDE.md`
- `/docs/ADR.md` — CD-20(맞춤형 GPT 대신 프로젝트 공유)
- `/content/course.yaml` — `d1-project` 항목
- **실습형 기준 예시(reviewed)**: `/content/day1/04.mdx`, `/content/instructor/day1/04.md`
- 앞 교시: `/content/day1/01.mdx`(기준 질문 5개와 기준 답 기록), `/content/day1/02.mdx`(지침서 v1)
- `/content/product-features.yaml` — `chatgpt-projects`, `chatgpt-project-sharing`, `chatgpt-project-duplicate`
- `/content/external-links.yaml`

## 작업 목적

D1-03 `d1-project`(ChatGPT Project로 비서 만들기)를 만든다. D1-02에서 쓴 지침서 v1을 Project 지침란에 넣어 "매번 같은 규칙으로 답하는" 환경을 만들고, D1-01 기준 답과 나란히 비교한다. 지침이 **환경**에 들어가야 효과가 있다는 것을 체험하는 시간이다.

## 작업

1. `content/day1/03.mdx`(`lesson_id: d1-project`) — 기준 예시 구조를 따른다.
   - 강사 시연: Project 개념과 만들기(메뉴 정보는 `<Feature>`로만).
   - 함께 따라하기: Project 생성과 지침 입력. 막힘 지점 sp-d1-03-a(지침을 채팅창에 붙여 넣음)에 대한 잘못된 결과 예시.
   - 실습: 기준 질문 5개 재질문, D1-01 기준 답과 적용 전·후 비교(하네스 대장 "적용 전·후 비교" 탭). 기록은 판단 하나 + 붙여 넣기로 줄인다(PRACTICE_DESIGN 9절).
   - 선택: 동료 공유(가능 시) 또는 빼보기 실험(지침 한 줄 지우고 다시 묻기). 공유 기능 정보는 `<Feature>`로만.
   - 예상 결과 / 잘못된 결과 예시와 어디가 왜 틀렸는지.
   - "Harness에서 무엇을 바꿨는가": 지침이 Project 환경에 들어갔다(아직 근거 자료는 없음 → 기준 질문 1번 같은 기한 답은 여전히 근거가 없다).
   - "다음 교시 연결": D1-04에서 근거 자료(교육용 가상 규정)를 연결한다.
2. `content/instructor/day1/03.md` — 공개 가능한 진행 안내만.
3. `content/course.yaml` — **`d1-project` 항목 안에서만** 예외 범위로 고친다(이 교시에는 카드가 없다).
4. `content/external-links.yaml` — "적용 전·후 비교" 탭을 **추가만**(예: 번호 / 질문 / 전 답 요약 / 후 답 요약 / 형식·범위 개선(예/아니오)).

## 수정 허용 경로

`content/day1/03.mdx`, `content/instructor/day1/03.md`, `content/course.yaml`(예외 범위), `content/external-links.yaml`(탭 추가만), `public/images/d1-project/*`.

## Acceptance Criteria

```bash
npm run verify -- --scope lesson:d1-project
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `git diff content/course.yaml`에 `d1-project` 항목 밖의 변경이 없는지 확인한다.
3. 체크리스트: 기준 예시와 구조가 맞는가 / 제품 정보를 `<Feature>`로만 썼는가(프로젝트 복제는 확인 전 [TBD: OQ-02] — 지침 버전 탭으로 대체) / 예상 결과·잘못된 결과 예시 / status draft까지.
4. 결과에 따라 `phases/2-day1-content/index.json`의 step 6을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 파일, 추가한 탭 ID, 넘기는 산출물(Project v1, 비교표)"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/kits/`, `content/day1/01.mdx`, `content/day1/04.mdx`를 수정하지 마라. 이유: reviewed 해시가 깨진다.
- 이 교시에 카드를 새로 만들거나 course.yaml `cards`를 바꾸지 마라. 이유: course.yaml에 이 교시 카드가 없고, 카드는 막힘 지점이 있을 때만 만든다(V-CRS-008).
- 맞춤형 GPT를 가르치지 마라. 이유: CD-20.
- 등록부에 없는 제품 기능을 쓰지 마라. 필요하면 blocked.
- status를 reviewed로 올리거나 `npm run review:approve`를 실행하지 마라. Codex를 등장시키지 마라.
- 기존 테스트를 깨뜨리지 마라.
