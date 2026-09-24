# Step 9: day1-flow-check

## 읽어야 할 파일

- `/CLAUDE.md`
- `/docs/COURSE_MAP.md` — Day 1 흐름과 산출물 재사용
- `/docs/HARNESS_ELEMENTS.md` — 6요소 정의
- `/docs/CONTENT_GUIDE.md` — 1절 공통 필수 섹션("Harness에서 무엇을 바꿨는가", "다음 교시 연결"), 7절 핵심 메시지
- `/content/course.yaml` — Day 1 교시의 `elements`, `outputs[].used_by`
- Day 1 교시 전체: `/content/day1/01.mdx`~`05.mdx`, `07.mdx`와 `/content/instructor/day1/*.md`

## 작업 목적

Day 1은 교시의 나열이 아니라 **앞 교시의 결과를 다음 교시에서 다시 쓰는 누적 구조**여야 한다. 개념 흐름은 Prompt(D1-01) → Instructions(D1-02·03) → Context(D1-04) → Evals(D1-05·06) → Harness(D1-07)다. 이 step은 각 교시 step이 따로 쓴 D1-02·03·05·07의 **연결 부분만** 점검하고 고친다. 새 내용을 만들지 않는다.

## 작업

1. 다음을 점검한다.
   - 각 교시 "Harness에서 무엇을 바꿨는가"가 앞 교시와 이어지고, 6요소가 누적되는 모습이 보이는가(course.yaml `elements`와 일치). Day 1에서 다루지 않는 도구(Tools)는 Day 2로 명시되어 있는가.
   - 각 교시 "다음 교시 연결"이 실제 다음 교시의 첫 활동과 맞는가.
   - course.yaml `outputs[].used_by`에 적힌 재사용(예: 기준 답 → D1-03 비교, 비교표 → D1-07, 자료 목록 → D1-07)이 본문에서 실제로 언급되는가.
   - 하네스 대장 탭 이름과 `<ExternalLink tab>` 사용이 교시마다 일관되는가.
   - 용어(glossary `student_label`)와 문체가 교시마다 같은가.
   - "긴 프롬프트 = 하네스"로 읽힐 문장이 없는가.
   - D1-07이 평가 절차를 다시 쓰지 않고 D1-06을 가리키는가.
2. 어긋남은 **D1-02·03·05·07과 그 강사 안내 안에서만** 고친다. 고친 목록을 summary에 적는다.
3. D1-01·D1-04(reviewed) 쪽을 고쳐야만 맞출 수 있는 어긋남은 고치지 말고 summary에 "reviewed 쪽 어긋남"으로 보고한다(step 10에서 사람이 판단).

## 수정 허용 경로

`content/day1/02.mdx`, `content/day1/03.mdx`, `content/day1/05.mdx`, `content/day1/07.mdx`, `content/instructor/day1/02.md`, `content/instructor/day1/03.md`, `content/instructor/day1/05.md`, `content/instructor/day1/07.md`.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 결과에 따라 `phases/2-day1-content/index.json`의 step 9를 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "고친 연결 목록, reviewed 쪽 어긋남(있으면), 6요소 누적 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/day1/01.mdx`, `content/day1/04.mdx`, 카드 파일, `content/kits/`, `content/course.yaml`을 수정하지 마라. 이유: reviewed 해시가 깨지거나 이 step의 허용 경로 밖이다.
- 학습목표·실습 활동을 새로 추가하거나 빼지 마라. 이유: 연결 점검 step이다. 교시 구성은 course.yaml이 원천이다.
- 기존 테스트를 깨뜨리지 마라.
