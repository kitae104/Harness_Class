# 프로젝트: 공무원을 위한 하네스 엔지니어링 — 웹 강의자료

2일 14시간 과정의 강의자료를 HTML 웹 강의 사이트로 만든다. 지금 단계의 목표는 콘텐츠가 아니라 **좋은 콘텐츠를 계속 만들 수 있는 Harness**다. 목적·범위는 [docs/PRD.md](docs/PRD.md), 결정 이력은 [docs/ADR.md](docs/ADR.md).

## 기술 스택
- Astro 정적 사이트 + MDX + Content Collections(zod) — Phase 1에서 도입 [PROVISIONAL]
- 검증: Python 3.11+ `scripts/validate_course.py`(PyYAML), pytest, Vitest, Playwright
- 배포: GitHub(Public) → GitHub Actions CI → Vercel, 불가 시 오프라인 번들

## 정보 우선순위
1. 사용자 결정(ADR의 CD 항목) 2. 제안서 PDF(비공개 원본) 3. 공식 최신 문서 4. 기타
PDF와 다르게 정한 것은 ADR CD 항목의 "PDF 원문" 필드에 기록한다.

## CRITICAL 규칙
- CRITICAL: 수치·구조(시간, 교시, 목표, 산출물, 카드 배치)는 `content/course.yaml`에만, 제품 정보는 `content/product-features.yaml`에만, 출처·법령 조문은 `content/sources.yaml`에만, 외부 링크는 `content/external-links.yaml`에만 둔다. 본문과 docs에 직접 쓰지 말고 ID로 참조한다.
- CRITICAL: ID(교시·목표·산출물·카드·출처·기능)는 한번 정하면 바꾸지 않는다. 이유: 여러 파일의 참조가 조용히 깨진다.
- CRITICAL: AI는 콘텐츠 status를 `draft`까지만 올린다. `reviewed`는 사람이 `npm run review:approve <id>`로만 올린다. reviewed 콘텐츠를 수정하면 해시가 달라져 다시 검토 대상이 된다.
- CRITICAL: step 파일의 "수정 허용 경로" 밖을 수정하지 않는다. 공유 등록부(`content/*.yaml`)에는 추가만 한다.
- CRITICAL: 등록부에 없는 제품 기능·법령 조문은 서술하지 않는다. 필요하면 `[TBD: OQ-xx]`로 표시하고 [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md)에 등록한다.
- CRITICAL: 실제 개인정보, 실제 기관 문서, 비공개 원본(`references/`)을 커밋하지 않는다. 가상 자료는 "가상"으로 표기하고 전화번호는 `010-0000-XXXX`만 쓴다. 캡처는 계정 식별정보를 가린다.
- CRITICAL: Codex와 optional 콘텐츠를 core 교시의 선행 조건으로 만들지 않는다.
- CRITICAL: 원작자 허락 전에는 Public 저장소로 push하지 않는다(CD-15).

## 정보 상태 태그
- `[PROVISIONAL]` 잠정안 · `[TBD: OQ-xx]` 추가 확인 필요(OQ ID 필수) · `[AS-OF: feature-id]` 변경 가능한 제품 정보
- 태그가 없으면 CONFIRMED로 본다. validator가 형식과 참조를 검사한다.

## 개발 프로세스
- 코드(스크립트·컴포넌트)는 테스트를 먼저 쓰고 구현한다(TDD).
- 콘텐츠는 검증 규칙(course.yaml, validator 규칙)을 먼저 정하고 쓴다.
- 커밋은 conventional commits(feat:, fix:, docs:, refactor:, chore:).
- 새 작업은 `/harness`로 phase·step을 설계하고 `python scripts/execute.py <phase-dir>`로 실행한다.

## 명령어
```
python -m pytest scripts -q                     # Harness 테스트
python scripts/validate_course.py --docs-only    # Phase 1 이전 AC
python scripts/validate_course.py --scope lesson:<id> --require-reviewed
npm run verify -- --scope <대상>                  # Phase 1 이후 AC (lint + build + test + validate)
npm run dev | npm run build | npm run preview    # Phase 1 이후
```
