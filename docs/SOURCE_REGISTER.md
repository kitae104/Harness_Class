# 출처 관리 정책

모든 출처는 **[`content/sources.yaml`](../content/sources.yaml)에만** 등록한다. 본문은 `<Source id="..." article="..."/>`로 인용한다.

## 1. 출처 유형
| type | 예 | 필수 필드 |
|---|---|---|
| `law` | 주민등록법, 국가공무원 복무규정 | url, **effective_date(시행일)**, **articles(조문)**, version |
| `guideline` | 국가정보원 AI보안 가이드북 | url, published |
| `official-doc` | OpenAI·GitHub·Vercel 공식 문서 | url |
| `proposal` | 과정 제안서 PDF | 비공개 원본 표시(url 없음) |
| `user-decision` | 사용자 결정 CD-01~ | ADR 위치 |
| `fictional` | 가상 민원, 역할카드, 교육용 FAQ, 교육용 가상 규정(CD-21) | "가상" 표기 방법. 가상 규정은 `articles`(가상 조문 목록) |
모든 항목에 `accessed_at`(접근일)과 `license`(이용조건)가 필요하다(V-REG-002).

## 2. 법령 인용 규칙 (CD-04)
- 국가법령정보센터(law.go.kr) 현행 원문을 기준으로 한다.
- **조문 단위**로 인용한다. 법령 단위로만 인용하면 개정 시 영향 범위를 찾을 수 없다.
- 시행일과 법령 번호(version)를 함께 기록한다. 교시 본문은 `<Source>`가 시행일을 자동 표시한다.
- 조문을 요약·재구성한 교육용 FAQ는 원문이 아니라는 것을 밝히고, 근거 조문 ID를 붙인다.
- 과태료 금액처럼 별표에 있는 값은 원문 확인 전까지 본문에 쓰지 않는다 [TBD: OQ-07].
- 법령은 저작권법상 보호받지 못하는 저작물이지만, 편람·해설서 등 기관 저작물은 복제하지 않는다.

## 3. 비공개 원본
- 제안서 PDF(`proposal-2026-09`)는 저장소 밖(`references/`, .gitignore)에 둔다. 내부 운영 메모와 강사 인적사항이 있어 공개 저장소에 올리지 않는다(CD-02, ADR-009).
- 인용할 때는 요약만 쓰고, 운영 메모의 내용은 공개 콘텐츠에 옮기지 않는다.

## 4. 이미지·캡처
- 캡처 이미지는 대상 기능 ID와 캡처일을 등록한다(product-features 또는 sources). 계정 식별정보를 가린다.
- 제안서의 그림 A~C·1~8은 사이트에서 다시 만든다(도식은 SVG, 화면은 교육용 계정 캡처, Phase 9).

## 5. 정보 우선순위와 충돌 처리
1. 사용자 결정 2. 제안서 PDF 3. 공식 최신 문서 4. 기타.
- 충돌하면 상위 출처를 따르고, 제안서와 달라진 내용은 [ADR.md](ADR.md) CD 항목의 "PDF 원문"에 기록한다.
- 2차 자료(언론 기사 등)는 1차 자료를 찾기 전까지 `[TBD: OQ-xx]`와 함께만 쓴다.

## 6. 재확인
- 접근일이 constraints.freshness_days를 넘으면 경고(V-REG-003).
- 개설 전(`--pre-launch`) 법령 개정 여부를 확인한다. 개정되면 version·effective_date·articles를 갱신하고 해당 키트와 교시를 재검토한다.
