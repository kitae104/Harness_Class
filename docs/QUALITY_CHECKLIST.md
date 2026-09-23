# 품질 체크리스트

품질 기준을 **자동 검사(AUTO)** 와 **사람 검토(HUMAN)** 로 나눈다. AUTO 규칙은 `scripts/validate_course.py`의 규칙 ID와 1:1로 대응한다. 구현 열이 `구현`인 규칙은 코드에 있어야 하고, 코드에 있는 규칙은 `구현`으로 표시되어야 한다(V-QUA-001이 이 표와 코드를 대조한다).

- 층: `AUTO-오류`(AC 실패) · `AUTO-경고`(보고) · `AUTO-정보` · `HUMAN`(reviewed 승격 조건)
- 구현 열: `구현`(현재 동작) · `예정(Pn)`(해당 phase에서 추가 예정. 구현하는 step이 `구현`으로 바꾼다)

## 1. 자동 검사 규칙
| ID | 층 | 검사 내용 | 구현 |
|---|---|---|---|
| V-DOC-001 | AUTO-오류 | 필수 docs 18개 존재 | 구현 |
| V-DOC-002 | AUTO-오류 | docs와 CLAUDE.md의 상대 링크가 실제 파일을 가리킴 | 구현 |
| V-CRS-001 | AUTO-오류 | course.yaml 스키마와 허용값(유형·트랙·상태·요소·교과목·활동 종류·지원 방식) | 구현 |
| V-CRS-002 | AUTO-오류 | Day·교시 수와 총 시간이 constraints와 일치, 교시 번호 중복·누락 없음 | 구현 |
| V-CRS-003 | AUTO-오류 | 교시 핵심 활동 합계가 max_core_minutes 이하 | 구현 |
| V-CRS-004 | AUTO-오류 | 모든 교시에 학습목표·산출물·결과 확인·실습 활동 존재 | 구현 |
| V-CRS-005 | AUTO-오류 | 학습목표→산출물→다음 교시(used_by) 추적성 | 구현 |
| V-CRS-006 | AUTO-오류 | 6요소별 최소 교시 수 | 구현 |
| V-CRS-007 | AUTO-오류 | 교시·목표·산출물·막힘 지점·카드·모듈 ID 중복 없음 | 구현 |
| V-CRS-008 | AUTO-오류 | 카드 무결성: 존재, 교시 일치, 막힘 지점 근거, 분류·단계·붙여넣을 곳 허용값 | 구현 |
| V-CRS-009 | AUTO-오류 | core 교시가 optional 카드나 Codex 내용에 의존하지 않음 | 구현 |
| V-CRS-010 | AUTO-오류 | 실습형 교시에 예상 결과(4)와 잘못된 결과 예시(5) 지원 | 구현 |
| V-CRS-011 | AUTO-경고 | 교시당 카드 수, core 카드 총량 상한 | 구현 |
| V-REG-001 | AUTO-오류 | 제품 정보: 필드·허용값·fallback, 확인된 기능은 확인일·출처, 미확인은 OQ | 구현 |
| V-REG-002 | AUTO-오류 | 출처: 필드·유형, 법령은 시행일·조문, 공개 출처는 URL | 구현 |
| V-REG-003 | AUTO-경고 | 제품 정보·출처·링크 확인일 경과(`--pre-launch`에서 오류) | 구현 |
| V-REG-004 | AUTO-오류 | 외부 링크: 필드·허용값, active는 URL·확인일 | 구현 |
| V-TAG-001 | AUTO-오류 | 정보 상태 태그: TBD는 존재하는 OQ, AS-OF는 존재하는 기능 ID | 구현 |
| V-TAG-002 | AUTO-경고 | 닫힌 OQ를 가리키는 TBD | 구현 |
| V-TAG-003 | AUTO-정보 | 정보 상태 태그 집계 | 구현 |
| V-PII-001 | AUTO-오류 | 실제 형식 전화번호·주민등록번호(가상 번호 010-0000-XXXX 제외) | 구현 |
| V-TXT-001 | AUTO-오류 | 수강생 콘텐츠의 금지 표현(banned-terms) | 구현 |
| V-SEC-001 | AUTO-오류 | 비공개 원본(references/)이 git에 추적되지 않음 | 구현 |
| V-QUA-001 | AUTO-오류 | 이 표의 구현 열과 실제 구현된 규칙이 일치 | 구현 |
| V-REV-001 | AUTO-오류 | `--require-reviewed`: 범위 안 항목이 모두 reviewed | 구현 |
| V-CLI-001 | AUTO-오류 | `--scope` 대상 존재 | 구현 |
| V-LSN-001 | AUTO-오류 | 교시 MDX가 course.yaml 교시와 1:1 연결(lesson_id), planned는 준비 중 페이지 | 예정(P1) |
| V-LSN-002 | AUTO-오류 | 교시 유형별 필수 섹션 존재 | 예정(P1) |
| V-LSN-003 | AUTO-경고 | 학습목표 동사 휴리스틱("이해한다" 등), 문장 길이 | 예정(P1) |
| V-PRM-001 | AUTO-오류 | 카드 파일이 course.yaml 카드와 1:1, 필수 필드, 대괄호↔replace 일치 | 예정(P1) |
| V-PRM-002 | AUTO-오류 | 직접 쓰기(L3) 카드에 바꿔 쓰기(L2) 대안 존재 | 예정(P1) |
| V-PRM-003 | AUTO-경고 | 카드 tested_at 경과 | 예정(P1) |
| V-REV-002 | AUTO-오류 | reviewed 항목의 콘텐츠 파일 해시(LF 정규화)가 course.yaml의 reviewed_hash와 일치 | 예정(P1) |
| V-WEB-001 | AUTO-오류 | 빌드 산출물 내부 링크·이미지 경로 | 예정(P1) |
| V-WEB-002 | AUTO-오류 | 오프라인 번들 상대경로, 외부 CDN·웹폰트 없음 | 예정(P1) |
| V-WEB-003 | AUTO-오류 | 복사 버튼·이전/다음·375px 표시·file:// 동작·외부 요청 차단 상태 표시(Playwright, `npm run test:e2e`) | 예정(P1) |
| V-KIT-001 | AUTO-오류 | kit.yaml 필수 구성요소, 근거가 sources.yaml ID를 가리킴 | 예정(P2) |
| V-PRP-001 | AUTO-오류 | 제안서 개정본의 시간·교시·산출물이 course.yaml과 일치 | 예정(P9) |

## 2. 사람 검토 항목 (reviewed 승격 조건)
| ID | 검토 내용 | 누가 |
|---|---|---|
| H-01 | 법령 인용과 교육용 FAQ의 해석이 정확하다 | 법령 해석 검토자 [TBD: OQ-12] |
| H-02 | 교시가 학습목표를 50분 안에 달성할 수 있다(흐름: 개념→시연→따라하기→실습→검증→개선) | 강사 |
| H-03 | 초보자가 막힐 지점에 지원이 있고, 카드가 생각을 대신하지 않는다 | 강사 |
| H-04 | 카드를 교육용 Plus 계정에서 실제 실행했고 결과가 `check`를 만족한다 | 강사 또는 보조강사 |
| H-05 | 캡처가 현재 화면과 같고 계정 식별정보가 가려져 있다 | 강사 |
| H-06 | 가상 자료가 실제 인물·기관을 연상시키지 않는다 | 강사 |
| H-07 | "긴 프롬프트 = 하네스"로 읽힐 부분이 없다 | 강사 |

## 3. 사람 검토 루브릭 (교시 1개 기준)
| 항목 | 2 충분 | 1 보완 필요 | 0 다시 쓰기 |
|---|---|---|---|
| 목표 달성 가능성 | 실습 결과로 목표를 확인할 수 있다 | 일부 목표만 확인 가능 | 목표와 실습이 따로 논다 |
| 초보자 지원 | 막힘 지점마다 지원이 있다 | 일부 누락 | 빈 화면에서 시작한다 |
| 하네스 관점 | 도구 절차마다 이유가 있다 | 이유가 일부 빠짐 | 기능 사용법 위주 |
| 정확성 | 법령·제품 정보가 등록부와 일치 | 표현이 모호 | 틀린 정보 |
모든 항목 2점이어야 `review:approve`한다.

## 4. 테스트 기록 양식 (카드 실제 실행, H-04)
| 날짜 | 카드 ID | 테스트한 사람 | 붙여넣은 곳 | 결과 요약 | check 충족 | 믿으면 안 되는 부분이 나타났나 | 조치 |
|---|---|---|---|---|---|---|---|

## 5. 배포 관문
| 관문 | 조건 |
|---|---|
| Phase 1 이전 step AC | `python -m pytest scripts -q` + `python scripts/validate_course.py --docs-only` 오류 0 |
| step AC(Phase 1 이후) | `npm run verify -- --scope <대상>` 오류 0 |
| human-review step | `validate_course.py --scope phase:<id> --require-reviewed` 오류 0 (phase index.json의 `review_targets`만 검사, `phase:` 범위 구현 전에는 `--scope lesson:<id>`) |
| 오프라인·UI 변경 | `npm run build:offline && npm run test:e2e` 통과 |
| Preview | CI 통과 + 강사가 Preview URL에서 해당 교시 확인(저장소 연결 전에는 `npm run preview`) |
| Production | `validate_course.py --production` 오류 0(core 전부 reviewed, 해시 일치, 링크 오류 0) |
| 개설 전 | `validate_course.py --pre-launch` 오류 0 + 교육망 접속 테스트 + 법령 개정 확인 |
