---
# 테스트 전용 가짜 카드 — 실제 카드가 아니다(content/prompts/에 두지 않는다).
id: card-sample
stuck_point: sp-sample
where: new-chat
when: 테스트할 때
input: 테스트 입력
l3_structure: |
  [역할] 너는 ○○ 업무를 돕는 ○○다.
  [입력] 아래는 [내가 넣는 자료]다.
  [규칙] 반드시 지킬 것 / 하지 말 것
  [출력 형식] 이런 모양으로 답하라.
  [모를 때] 모르는 정보는 지어내지 말고 "확인 필요"라고 표시하라.
l2_template: |
  너는 [내 업무] 업무를 돕는 검토자다.
  아래는 내가 쓴 [검토할 문서]다.
  [내 업무] 기준으로 빠진 것을 찾아라.
  모르는 정보는 지어내지 말고 "확인 필요"라고 표시하라.
l1_full: |
  너는 전입신고 민원 업무를 돕는 검토자다.
  아래는 내가 쓴 지침 초안이다.
  모르는 정보는 지어내지 말고 "확인 필요"라고 표시하라.
default_level: 2
line_notes:
  - {line: "너는 [내 업무] 업무를 돕는 검토자다.", element: instructions, why: 역할을 정한다}
replace: ["[내 업무]", "[검토할 문서]"]
check: [빠진 항목이 표시되었다]
do_not_trust: [지어낸 조문]
next: 반복되는 규칙은 Project 지침으로 옮긴다.
tested_at: null
tested_by: null
---
