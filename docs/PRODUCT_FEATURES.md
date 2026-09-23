# 제품 정보 관리 정책

ChatGPT·Codex·Google·Vercel의 요금제, 기능, 한도, 메뉴 위치, 모델명은 바뀐다. 이런 정보는 **[`content/product-features.yaml`](../content/product-features.yaml)에만** 적고, 교육 원리(docs, 교시 본문)와 분리한다.

## 1. 원칙
- 본문은 `<Feature id="..."/>`, docs는 `[AS-OF: id]`로만 참조한다. 없는 ID를 가리키면 오류(V-TAG-001).
- 모델명은 핵심 콘텐츠에 쓰지 않는다(banned-terms).
- 확인되지 않은 기능은 `status: unverified`로 등록하고 `tbd`에 OQ를 적는다(V-REG-001).

## 2. 필드
| 필드 | 내용 |
|---|---|
| `id` | 고정 ID(예: `chatgpt-projects`) |
| `product`, `plan` | 제품, 요금제(기준: 개인 ChatGPT Plus, CD-01) |
| `name`, `detail` | 기능명, 현재 상태 설명 |
| `status` | available / limited / unavailable / unverified |
| `verified_at`, `verified_by` | 확인일, 확인 방법(web = 공식 문서, hands-on = 실제 계정) |
| `source` | 공식 출처 URL |
| `ui_path` | 메뉴 위치(개념 설명과 분리) |
| `fallback` | 기능이 없거나 바뀌었을 때 수업에서 할 일 — **필수**. `<Feature>`는 status가 unavailable이면 이 문구를 표시한다 |
| `used_in` | 이 기능을 쓰는 교시·모듈 ID |
| `tbd` | unverified일 때 OQ 태그 |

## 3. 확인 절차
1. 공식 문서(help.openai.com, developers.openai.com, vercel.com/docs 등)로 확인하고 `verified_by: web`.
2. 공식 문서로 알 수 없는 동작(예: 프로젝트 안 임시 채팅)은 교육용 Plus 계정으로 직접 해 보고 `verified_by: hands-on`.
3. 확인일이 constraints.freshness_days를 넘으면 경고(V-REG-003), `--pre-launch`에서는 오류.

## 4. 개설 전 재확인
`python scripts/validate_course.py --pre-launch`로 확인일이 지난 기능과 `used_in` 교시를 뽑아 재확인한다. 바뀐 기능이 있으면 detail·fallback을 고치고, 영향받은 교시를 draft로 되돌려 다시 검토한다.

## 5. 현재 확인 결과에서 수업에 영향을 준 것 (2026-09-24)
- 맞춤형 GPT는 개인 Plus에서 새로 만들 수 없다 → 가르치지 않는다(CD-20) [AS-OF: chatgpt-custom-gpt-creation].
- 프로젝트 전용 메모리는 같은 프로젝트의 다른 대화를 참조할 수 있다 → 평가 대화 분리 규칙 [AS-OF: chatgpt-project-memory].
- 임시 채팅은 비개인화를 고를 수 있다 → D1-1 기준 답변에 사용 [AS-OF: chatgpt-temporary-chat].
- Vercel Hobby는 비상업 용도만 → 요금제 결정 필요 [AS-OF: vercel-hobby-commercial] [TBD: OQ-09].
