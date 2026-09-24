---
# AI에게 도움받기 카드 뼈대 — npm run new:prompt로 만들었다(PROMPT_GUIDE 2~4절).
# id·stuck_point·where·default_level은 course.yaml에서 채웠다. 상태(status)는 이 파일이 아니라 course.yaml에만 있다.
# 바꿀 부분은 [대괄호]로 쓰고 replace 목록과 1:1로 맞춘다. 모델명·메뉴 위치·한도는 쓰지 않는다.
# 모든 단계에 "모르는 정보는 '확인 필요'" 문장과 "실제 개인정보를 넣지 마세요" 안내를 넣는다.
id: {{id}}
stuck_point: {{stuck_point}}
where: {{where}}
when: 작성 예정
input: 작성 예정 (실제 개인정보를 넣지 마세요. 교육용 가상 자료만 씁니다.)
l3_structure: |
  [역할] 너는 ○○ 업무를 돕는 ○○다.
  [입력] 아래는 [내가 넣는 자료]다.
  [규칙] 반드시 지킬 것 / 하지 말 것
  [출력 형식] 이런 모양으로 답하라.
  [모를 때] 모르는 정보는 지어내지 말고 "확인 필요"라고 표시하라.
l2_template: |
  너는 [내 업무] 업무를 돕는 검토자다.
  작성 예정
  모르는 정보는 지어내지 말고 "확인 필요"라고 표시하라.
l1_full: |
  작성 예정
  모르는 정보는 지어내지 말고 "확인 필요"라고 표시하라.
default_level: {{default_level}}
line_notes:
  - {line: "작성 예정", element: instructions, why: 작성 예정}
replace: ["[내 업무]"]
check: [작성 예정]
do_not_trust: [작성 예정]
next: 작성 예정 (반복되는 규칙은 Project 지침으로 옮기라고 안내한다)
tested_at: null
tested_by: null
---
