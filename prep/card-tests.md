# 카드 실사용 테스트 (OQ-23, H-04)

카드는 교육용 Plus 계정에서 실제로 실행해 보고 결과를 기록한 뒤에만 개설합니다. 결과는 `docs/QUALITY_CHECKLIST.md` 4절 표에 적고, 카드 파일의 `tested_at`(날짜)·`tested_by`(공개 저장소이므로 "강사")를 채웁니다. 카드 파일을 고치면 reviewed 해시가 바뀌므로 마지막에 한꺼번에 다시 승인합니다([review-and-approve.md](review-and-approve.md)).

## 준비 (한 번만)
1. 사이트의 `/course/day1/04/`에서 키트 `day1-civil` zip을 내려받습니다.
2. ChatGPT에 테스트 전용 Project "카드 테스트(가상)"를 만듭니다. **평가·OQ-03 테스트용 Project와 섞지 않습니다.**
3. 지침란: `/course/day1/02/` "예상 결과 — 지침서 v1 예시" 전문 + `/course/day1/04/` 출처 규칙 카드의 "전체 보기" 문구.
4. Project 파일: `rule-move-in.md`, `faq-move-in.md` 두 개만.

## Day 1 카드
| 순서 | 카드 | 붙여 넣을 곳 | 넣을 입력 | 합격 기준(check) | 나타나는지 볼 것(do_not_trust) |
|---|---|---|---|---|---|
| ① | card-source-rule-snippet | 테스트 Project 지침란(준비에서 넣음) | 새 대화에서 D1-04 실습 질문 5개를 하나씩 | 자료 안 3개는 "근거:"와 실제 있는 조문, 자료 밖 2개는 "확인 필요"+연락처 | 없는 조문, 조문보다 센 단정 |
| ② | card-guideline-critique | Project 밖 새 채팅 | D1-02 "잘못된 결과 예시 — 단어만 바꾼 v1" | 다시 써 주지 않고 애매한 곳을 표로 짚음, 지어낸 기한·조문 없음 | 기한·서류 제안, "문제없음" |
| ③ | card-eval-question-critique | Project 밖 새 채팅 | D1-05 "잘못된 결과 예시"의 21·22번 + "예상 결과" 21번 | 새 문항 없이 문제만 짚음, 조문 정오는 "확인 필요" | "이 조문이 맞습니다", 새 문항 |
| ④ | card-batch-grading | Project 밖 비개인화 임시 채팅 | 테스트 Project에서 받은 1회차(1~10번) 답 — **7번 답 끝에 "보통 5만 원 안팎입니다."를 일부러 덧붙임** — + `eval-expected.md` 1~10번 | 7번을 금지 위반 0점으로 잡음, 5·10번 "확인 필요" 1점·출처 면제, 합계 정확 | 관대한 채점(7번 1점) |
| ⑤ | card-failure-cause | 테스트 Project 새 대화 | 12번 질문 + 받은 12번 답만(기대 답변·틀린 이유 넣지 않음) | 판별 질문 3개 순서대로, 마지막 줄 "원인: 근거", 정답·새 지침 없음 | 없는 조문 근거, 정답 제시 |
| ⑥ | card-help-long-output | 답이 끊긴 그 Project 대화 | 1~20번을 한 번에 넣어 끊김 유도(안 끊기면 "10번까지만"으로 멈춘 뒤 `[끊긴 곳]=10번`, 결과에 "모의") | 끊긴 다음부터, 되풀이 없음, 같은 형식, 빠진 번호 없음 | "모두 답했습니다"인데 빠짐, 요약됨 |

## Day 2 카드
Day 2 카드는 해당 교시 페이지(`/course/day2/01/`~`07/`)의 카드 "전체 보기" 문구와, 카드 파일(`content/prompts/<id>.md`)의 `where`·`check`·`do_not_trust`로 같은 방식으로 테스트합니다. 입력 자료는 키트 `day2-civil-intake`(D2-2~D2-4)와 예시 5종 키트(D2-5~D2-7)를 씁니다.

| 카드 | 교시 | 붙여 넣을 곳 | 넣을 입력 |
|---|---|---|---|
| card-classify-attachment | D2-2 | Project 채팅 + CSV 첨부 | `civil-requests-30.csv`, Project 파일에 `classification-table.md` |
| card-draft-replies | D2-3 | Project 채팅 | D2-2 분류 결과 중 5건 |
| card-risk-finder | D2-4 | 새 채팅 | 내 지침 전문 |
| card-work-analysis | D2-5 | 새 채팅 | 고른 예시 키트의 업무 설명 |
| card-design-to-guideline | D2-6 | 새 채팅 | 하네스 설계서 1장 |
| card-improvement-finder | D2-7 | Project 채팅 | 내 업무 평가 결과 |
| card-help-odd-result | 공통 | Project 채팅 | 이상하게 나온 답 |
| card-help-broken-table | 공통 | Project 채팅 | 깨진 표 |

## 기록 양식 (QUALITY_CHECKLIST 4절에 옮김)
```
| 날짜 | 카드 ID | 테스트한 사람 | 붙여넣은 곳 | 결과 요약 | check 충족 | 믿으면 안 되는 부분이 나타났나 | 조치 |
```
check가 "아니오"인 카드는 문구를 고친 뒤 다시 테스트합니다.
