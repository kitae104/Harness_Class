# 강의 준비 안내 (개설 전 삭제)

이 폴더는 **강의를 준비하는 동안만** 쓰는 강사용 안내입니다. 강의 자료(교시·카드·키트)는 AI가 draft까지 작성했고(CD-24), 사람이 확인하고 설정해야 할 곳에는 **강의 준비 표시**를 남겼습니다(CD-25). 준비가 끝나면 이 폴더와 표시를 모두 지웁니다.

## 표시를 보는 곳
| 표시 | 어디에 | 모양 |
|---|---|---|
| `<PrepNote>` | 교시 본문(Day 2), 안내 페이지(`/before`, `/templates`) | 사이트에 빨간 점선 상자 "강의 준비 · … 개설 전 삭제" |
| `## 강의 준비` 절 | 강사 안내(`content/instructor/day*/*.md`, 교시 페이지 하단 "강사 안내"), 키트 강사용 설명(`content/kits/*/instructor-notes.md`) | 강사 안내 맨 끝 절 |
| 안내 파일 | 이 폴더 | 설명이 긴 작업 |

Day 1 교시 본문은 이미 승인(reviewed)되어 본문에 표시를 넣지 않았습니다(해시가 깨짐). Day 1의 준비 항목은 강사 안내의 `## 강의 준비` 절에 있습니다.

전체 목록 보기: `npm run prep:list`

**하나씩 체크하며 진행하려면 [CHECKLIST.md](CHECKLIST.md)를 쓰세요.** 아래 순서를 체크 상자로 풀어 둔 문서입니다.

## 권장 순서
1. **결정할 것**: 구글 계정(OQ-06) — [google-sheets-forms.md](google-sheets-forms.md) 0절.
2. **외부 자원 만들기**: 하네스 대장 템플릿, 강사 공용 폼, 상호평가 폼, 업무용 폼 사본, 수료 설문 — [google-sheets-forms.md](google-sheets-forms.md).
3. **실사용 테스트**: 카드 14장(Day 1 6장 + Day 2 8장) — [card-tests.md](card-tests.md). OQ-03 — [oq03-test.md](oq03-test.md).
4. **교육장 점검**: 강의실 PC에서 chatgpt.com·이 사이트·구글 시트/폼 접속, 파일 업로드·CSV 첨부(OQ-05), CSV 한글 깨짐.
5. **재검토·승인·검사**: [review-and-approve.md](review-and-approve.md). 승인 대상은 `python scripts/validate_course.py --production`의 V-REV-001 목록(현재 draft 21건: Day 2 교시 7, 카드 8, 키트 6)과 해시가 바뀐 항목입니다.
6. **개설 직전 정리**: 아래 "제거 절차".

## 아직 열려 있는 확인 사항 (docs/OPEN_QUESTIONS.md)
| OQ | 내용 | 막는가 |
|---|---|---|
| OQ-02 | 프로젝트 복제 메뉴 | 아니오(지침 버전 탭으로 대체) |
| OQ-03 | 같은 Project의 다른 대화가 평가에 주는 영향 | 개설 전 D1-06 재검토([oq03-test.md](oq03-test.md)) |
| OQ-04 | 프로젝트 안 임시 채팅 | 아니오 |
| OQ-05 | 채팅 첨부 CSV가 Project 파일로 들어가는가, xlsx | D2-2 절차 확인 |
| OQ-06 | 구글 자원 소유 계정 | 외부 자원 만들기 |
| OQ-23 | 선승인·AI 작성 항목의 강사 재검토, 카드 실테스트 | 개설·Production 공개 |
| OQ-24 | 구글 폼 파일 업로드 문항의 로그인·드라이브 저장 | 아니오(사진 문항 선택) |

## 제거 절차 (개설 직전)
```
npm run prep:strip                 # 본문 <PrepNote>와 강사 안내·키트의 "## 강의 준비" 절을 지움
npm run prep:list -- --check       # 0건이면 통과
```
그다음 아래를 지웁니다.
- `prep/` 폴더
- `src/components/PrepNote.astro`
- `scripts/prep_notes.mjs`, `tests/unit/prep-notes.test.ts`
- `package.json`의 `prep:list`, `prep:strip` 두 줄
- `src/styles/global.css`의 "강의 준비 표시(CD-25, 개설 전 삭제)" 블록
- `docs/CONTENT_GUIDE.md` 7-1절과 `docs/QUALITY_CHECKLIST.md` 개설 전 관문의 `prep:list` 조건(원하면 남겨 둬도 됩니다)

`prep:strip`은 교시·키트 파일을 바꾸므로 해시가 달라집니다. 바뀐 항목을 다시 승인하고 `npm run verify`와 `python scripts/validate_course.py --production`을 돌립니다([review-and-approve.md](review-and-approve.md)).
