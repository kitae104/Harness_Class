# 강의 준비 체크리스트 (강사용, 개설 전 삭제)

위에서부터 차례로 진행하면서 `- [ ]`를 `- [x]`로 바꿉니다. VS Code 미리보기나 GitHub에서는 체크 상자로 보입니다.

**브라우저에서 체크하려면** `npm run prep:checklist`를 실행하고 http://127.0.0.1:4380 을 엽니다. 진행 기록은 `prep/checklist-progress.json`에 남습니다. 같은 항목을 담은 대화형 준비표입니다.

- **📨 결과 보내기**가 붙은 항목은 결과를 Claude 세션에 붙여 주세요. 반영과 수정은 AI가 합니다. 보내는 형식은 `examples/` 폴더를 참고합니다.
- AI는 승인(`review:approve`)을 할 수 없습니다. **승인은 반드시 직접** 합니다.
- 명령은 저장소 폴더(`D:\Githubs\Harness_WS\Harness_Class`)의 PowerShell에서 실행합니다.

> **순서가 중요한 이유**: 카드 테스트(3단계)와 OQ-03(4단계) 결과로 카드와 D1-06이 바뀔 수 있습니다. 승인(6단계)을 먼저 하면 파일이 바뀔 때 다시 승인해야 합니다.

---

## 0단계. 시작 전 확인 (5분)
- [ ] `git status`가 깨끗하고, 브랜치가 `feat-course-complete`인지 확인합니다.
- [ ] `npm run verify`가 "통과"로 끝나는지 확인합니다.
- [ ] 검토용 Preview가 열리는지 확인합니다: https://harness-class-git-feat-course-complete-aqua0405-2866s-projects.vercel.app
- [ ] `npm run prep:list`로 강의 준비 표시 목록(현재 35건)을 한 번 훑어봅니다.

## 1단계. 결정하기
- [ ] **구글 자원 소유 계정**을 정합니다(OQ-06). 강의 전용 계정을 권합니다. **📨 결과 보내기**: 정한 역할명(예: "강의용 계정")만 보내고 이메일 주소는 보내지 않습니다.
- [ ] **(선택) 남은 작은 결정**을 합니다. 모르겠으면 "AI 추천대로"라고 보내면 됩니다.
  - [ ] D2-3의 "시간 부족 시 생략" 목록에 있는 "공문 PDF 요약"을 **뺄지**, 가상 공문 PDF를 **키트에 넣을지**
  - [ ] Day 2 새 Project의 지침 버전을 기록할 때 "어느 Project인지" 열을 **더할지**

## 2단계. 구글 시트·폼 만들기 (`prep/google-sheets-forms.md`)
링크를 만들 때마다 **📨 결과 보내기**: "항목 이름 + 링크". 링크를 등록하고 본문의 준비 표시를 실제 링크로 바꾸는 일은 AI가 합니다.
- [ ] 하네스 대장 템플릿 시트: `/templates` 페이지의 탭을 **같은 이름·같은 열**로 만듭니다. 탭은 기준 질문 기록, 자료 목록, 지침 버전, 적용 전·후 비교, 평가, 개정 기록, 분류 대장, 초안 검토 기록, 로그 대장, 민원 하네스 완성본, 적용 로드맵입니다. 공유는 "보기"로 하고 `/copy` 링크를 씁니다.
- [ ] 강사 공용 민원 접수 폼(키트 `day2-civil-intake/form-questions.md`): 이메일 수집을 끄고 응답 시트를 연결합니다. 시트는 강사만 봅니다.
- [ ] 점검표 12항목 상호평가 폼(`/templates`의 점검표): 이메일 수집 끔, 사본 링크
- [ ] 업무용 폼 사본 ① 현장 점검(`field-inspection/form-template.md`): 사진 문항은 **선택**으로 둡니다.
- [ ] 업무용 폼 사본 ② 수요조사(`demand-survey/survey-form.md`): 문항 3은 "최대 2개"로 설정합니다.
- [ ] 수료 설문: 기관 설문이 있으면 그 링크를, 없으면 구글 폼을 준비합니다.
- [ ] 구글 폼 **파일 업로드 문항**이 응답자 로그인을 요구하는지, 파일이 드라이브에 저장되는지 공식 도움말로 확인합니다(OQ-24). **📨 결과 보내기**

## 3단계. 카드 14장 실사용 테스트 (`prep/card-tests.md`)
교육용 Plus 계정으로 테스트합니다. 테스트 전용 Project **"카드 테스트(가상)"**를 만들고, 지침과 파일은 `card-tests.md`의 "준비"대로 넣습니다.

카드마다 세 가지를 봅니다.
1. **check**를 모두 만족하는가
2. **do_not_trust**에 적힌 문제가 나타나는가
3. 기록 한 줄을 적었는가

**📨 결과 보내기**: 14줄 기록 표. 형식은 `examples/01-card-test-log.md`입니다.

**Day 1 카드 6장** (이미 승인됨. 테스트 뒤 다시 승인합니다)
- [ ] `card-source-rule-snippet`: Project **지침란**. D1-04 질문 5개
- [ ] `card-guideline-critique`: Project 밖 **새 채팅**. "단어만 바꾼 v1"
- [ ] `card-eval-question-critique`: **새 채팅**. D1-05의 잘못된 문항 2개와 좋은 문항 1개
- [ ] `card-batch-grading`: Project 밖 **비개인화 임시 채팅**. 7번 답에 "보통 5만 원 안팎입니다."를 일부러 넣었을 때 **0점으로 잡는지** 봅니다.
- [ ] `card-failure-cause`: Project **새 대화**. 12번은 질문과 받은 답만 넣습니다. 결과가 **"원인: 근거"**인지 봅니다.
- [ ] `card-help-long-output`: **답이 끊긴 그 대화**. 끊김을 재현하지 못하면 "모의"로 적습니다.

**Day 2 카드 8장** (draft)
- [ ] `card-classify-attachment`: Project 채팅 + `civil-requests-30.csv` 첨부. 확인 필요 6건(5·7·12·15·22·27)을 잡는지, 개인정보를 옮기지 않는지 봅니다.
- [ ] `card-help-broken-table`: Project 채팅. 탭으로 나뉜 표가 **구글 시트에 칸별로 붙는지** 확인합니다.
- [ ] `card-draft-replies`: Project 채팅. 5건 초안 모두에 "초안·검토 필요"가 붙는지 봅니다. 5번에서 금액을 단정하는지, 24번에서 개인정보를 옮기는지도 봅니다.
- [ ] `card-risk-finder`: **새 채팅**. 내 지침에서 위험 4가지를 짚고, 규칙을 대신 써 주지는 않는지 봅니다.
- [ ] `card-work-analysis`: **새 채팅**. 업무 설명을 6요소로 비판만 하고, 설계서를 대신 쓰지 않는지 봅니다.
- [ ] `card-design-to-guideline`: **새 채팅**. 지침 초안에 들어간 "사실"을 짚는지 봅니다.
- [ ] `card-improvement-finder`: Project 채팅. 판별 질문 3분류로 고칠 곳을 하나만 고르는지 봅니다.
- [ ] `card-help-odd-result`: Project 채팅. 지침·근거·입력 가운데 어디가 문제인지 진단만 하고, 답을 고쳐 쓰지 않는지 봅니다.

**양식 키트 채점 확인**
- [ ] 수요조사 또는 회의록 키트로 채점 카드를 한 번 돌립니다. D2-6에서 덧붙이는 "출처 = 양식 항목" 한 줄이 제대로 먹히는지 봅니다.

## 4단계. OQ-03 테스트 (`prep/oq03-test.md`, 약 20분)
카드 테스트와 **다른** Project **"OQ-03 테스트(가상)"**에서 합니다.
- [ ] 만들 때 보이는 메모리 설정 값을 메모합니다.
- [ ] T1: 새 대화에서 12번(가족 대리 서류)을 묻습니다. "확인 필요"가 정상입니다.
- [ ] T2: 다른 대화에 "위임장, 대리인 신분증, 신고인 신분증이 필요합니다. 기억해 두세요."를 넣습니다.
- [ ] T3: 또 다른 새 대화에서 12번을 다시 묻습니다. 위임장이 나오면 **영향 있음**입니다.
- [ ] T4: 영향이 있었다면 T2 대화를 지우고 다시 묻습니다.
- [ ] T5: 그래도 남으면 메모리 설정을 바꾸거나 새 Project에서 다시 묻습니다.
- [ ] T6: 애매하면 T2~T3을 한 번 더 합니다.
- [ ] **📨 결과 보내기**: 한 줄 결과(A 영향 없음 / B 삭제로 막힘 / C 삭제로도 남음). 형식은 `examples/02-oq03-result.md`입니다.

## 5단계. 제품 기능 실사용 확인 (가능한 것만)
- [ ] 프로젝트 **복제 메뉴**가 있는지 확인합니다(OQ-02).
- [ ] **프로젝트 안에서 임시 채팅**을 시작할 수 있는지 확인합니다(OQ-04).
- [ ] Project 채팅에 **CSV를 첨부**하면 Project 파일 목록에 들어가는지, xlsx도 첨부되는지 확인합니다(OQ-05).
- [ ] **데이터 제어** 메뉴(모델 개선 끄기)의 위치와 이름이 등록부와 같은지 확인합니다(D2-4).
- [ ] **📨 결과 보내기**: 항목마다 "있음·없음·다름 + 한 줄"

## 6단계. 교육장 PC 점검 (개설 4주 전 권장)
- [ ] chatgpt.com, 이 사이트(Preview 또는 Production), 구글 시트·폼 접속
- [ ] 키트 zip 내려받기와 압축 풀기
- [ ] Project 파일 업로드. 막히면 "본문 붙여 넣기" 대안이 되는지 확인합니다.
- [ ] CSV 첨부, CSV를 열었을 때 **한글이 깨지지 않는지**
- [ ] 구글 로그인(폼 응답)
- [ ] 사이트가 막히면 오프라인 번들을 씁니다: `npm run build:offline` → `dist-offline.zip`
- [ ] **📨 결과 보내기**: 막힌 것만

## 7단계. 강의 자료 재검토 (OQ-23, 교시당 10~15분)
Preview에서 **수강생 입장**으로 읽습니다. 교시마다 루브릭 4항목이 **모두 2점**인지 봅니다.
- 목표 달성: 실습 결과로 목표를 확인할 수 있는가
- 초보자 지원: 막히는 곳마다 도움이 있는가
- 하네스 관점: 절차마다 이유가 있는가
- 정확성: 정보가 틀리지 않았는가

빨간 점선 상자와 강사 안내의 "강의 준비" 절은 강사가 할 일입니다.

**📨 결과 보내기**: "교시 / 위치 / 무엇을 어떻게". 형식은 `examples/03-instructor-review.md`입니다.

**Day 1**
- [ ] D1-01 하네스 엔지니어링 이해 `/course/day1/01/`
- [ ] D1-02 업무 지침서 작성
- [ ] D1-03 ChatGPT Project로 비서 만들기
- [ ] D1-04 근거 자료 연결과 출처 답변
- [ ] D1-05 평가세트 설계
- [ ] D1-06 일괄 평가 실행(4단계 결과를 반영한 뒤 다시 확인)
- [ ] D1-07 실패 분석과 재평가

**Day 2**
- [ ] D2-01 구글 폼으로 입력 구조화 `/course/day2/01/`
- [ ] D2-02 여러 건 분류·요약
- [ ] D2-03 초안 생성과 사람 검토
- [ ] D2-04 안전장치 점검과 기록
- [ ] D2-05 내 업무 하네스 설계(프로젝트형 기준 예시)
- [ ] D2-06 내 업무 하네스 제작
- [ ] D2-07 개선·상호평가·적용 로드맵

**키트 6개** (각 키트의 `instructor-notes.md` "사람 검토" 절 기준: 규정·FAQ·기대 답변이 서로 맞는지, 가상 표기가 있는지)
- [ ] `day2-civil-intake` (민원 접수·분류·초안 검토)
- [ ] `rule-qa` (규정 Q&A)
- [ ] `civil-draft` (대형 생활폐기물 민원)
- [ ] `field-inspection` (현장 점검)
- [ ] `demand-survey` (수요조사)
- [ ] `meeting-minutes` (회의록)

**안내 페이지 6개**
- [ ] `/before` 사전 준비
- [ ] `/templates` 템플릿(대장 탭, 설계서, 점검표)
- [ ] `/project` 예시 5종
- [ ] `/resources` 용어·출처·제품 정보·알려진 문제
- [ ] `/practice` 실습 목록
- [ ] `/optional/codex` 선택 심화

## 8단계. AI가 결과를 반영한 뒤 확인
- [ ] AI가 반영한 수정을 Preview에서 다시 봅니다.
  - 카드 `tested_at`
  - OQ-03 결과에 따른 D1-06 수정
  - 등록한 링크
  - 재검토에서 나온 수정
- [ ] `npm run verify`가 통과하는지 확인합니다.

## 9단계. 승인 (직접 실행)
편집이 모두 끝난 뒤 **한 번에** 합니다. 먼저 `git status --short`로 파일 전체가 바뀐 것처럼 보이는지 확인합니다. 그렇다면 멈추고 알려 주세요.

**Day 2 교시 7개**
- [ ] `npm run review:approve d2-forms`
- [ ] `npm run review:approve d2-batch-classify`
- [ ] `npm run review:approve d2-drafts`
- [ ] `npm run review:approve d2-guardrails`
- [ ] `npm run review:approve d2-project-design`
- [ ] `npm run review:approve d2-project-build`
- [ ] `npm run review:approve d2-wrapup`

**카드 14장** (Day 1 카드는 `tested_at`을 채우면 해시가 바뀌어 다시 승인합니다)
- [ ] `card-guideline-critique` · [ ] `card-source-rule-snippet` · [ ] `card-eval-question-critique`
- [ ] `card-batch-grading` · [ ] `card-failure-cause` · [ ] `card-help-long-output`
- [ ] `card-classify-attachment` · [ ] `card-help-broken-table` · [ ] `card-draft-replies` · [ ] `card-risk-finder`
- [ ] `card-work-analysis` · [ ] `card-design-to-guideline` · [ ] `card-improvement-finder` · [ ] `card-help-odd-result`

**키트 6개**
- [ ] `day2-civil-intake` · [ ] `rule-qa` · [ ] `civil-draft` · [ ] `field-inspection` · [ ] `demand-survey` · [ ] `meeting-minutes`

**수정으로 해시가 바뀐 교시** (해당할 때만)
- [ ] `d1-eval-run`(OQ-03 반영 시) · [ ] 그 밖에 재검토로 고친 교시

**확인**
- [ ] `python scripts/validate_course.py --production`에서 V-REV 오류가 **0**인지 확인합니다. 남은 항목이 있으면 그 ID를 승인합니다.
- [ ] `npm run verify`가 통과하는지 확인합니다.
- [ ] 커밋과 push를 합니다. 커밋 메시지 예: `chore: approve reviewed course material`

## 10단계. 확인 사항 닫기
- [ ] OQ-23(재검토·카드 테스트)을 닫습니다. **📨 결과 보내기**: "OQ-23 끝". 기록은 AI가 합니다.
- [ ] OQ-03, OQ-06, OQ-24(와 확인한 OQ-02·04·05)가 닫혔는지 `docs/OPEN_QUESTIONS.md`에서 확인합니다.

## 11단계. 병합 (Production 공개)
> main에 병합하면 harness-class.vercel.app에 **바로 공개**됩니다. 10단계가 끝난 뒤에만 합니다(CD-22).
- [ ] PR #6(Day 1)을 Ready로 바꾸고 → CI 통과 → 병합합니다.
- [ ] PR #7(Day 2 등)의 base를 main으로 바꾸고 → Update branch → CI 통과 → 병합합니다.
- [ ] Production 사이트에서 Day 1~2를 한 번 훑어봅니다.

## 12단계. 개설 직전 정리 (CD-25)
- [ ] `npm run prep:strip`을 실행합니다(준비 표시를 모두 지움).
- [ ] `npm run prep:list -- --check`가 **0건**인지 확인합니다.
- [ ] `prep/README.md`의 "제거 절차"대로 `prep/` 폴더, `PrepNote.astro`, `prep_notes.mjs`와 그 테스트, `package.json`의 `prep:*` 두 줄, CSS 블록을 지웁니다.
- [ ] 바뀐 교시·키트를 다시 승인합니다(9단계와 같은 방법).
- [ ] `python scripts/validate_course.py --production`과 `npm run verify`가 통과하는지 확인합니다.
- [ ] 커밋 → PR → 병합합니다.
- [ ] (선택) 제안서 개정본(CD-08, `deliverables/course_proposal_v2.md`) 작성을 AI에게 요청합니다.

---
**진행 상황 요약**: 끝낸 단계 옆에 날짜를 적어 두면 다음 세션에서 이어 가기 쉽습니다.

| 단계 | 날짜 | 메모 |
|---|---|---|
| 0 | | |
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| 9 | | |
| 10 | | |
| 11 | | |
| 12 | | |
