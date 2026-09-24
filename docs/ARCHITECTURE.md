# 아키텍처

이 문서는 저장소 구조, 데이터 흐름, 스키마 담당, 사이트 구조, 확장 절차를 정의한다. 기술 선택의 이유는 [ADR.md](ADR.md).

## 1. 디렉터리 구조
```
CLAUDE.md                 # 모든 step에 주입되는 규칙
docs/                     # 명세(사람과 합의한 설계). 수치는 적지 않는다
content/
  course.yaml             # 과정 구조의 단일 원천 (COURSE_MAP 데이터)
  product-features.yaml   # 변경 가능한 제품 정보
  sources.yaml            # 출처·법령 조문
  external-links.yaml     # 저장소 밖 자원(구글 시트·폼)
  glossary.yaml           # 용어(수강생 표기 포함)
  banned-terms.yaml       # 금지 표현
  day1/ day2/             # 교시 본문 MDX            (Phase 3·5)
  modules/                # 교시가 아닌 추가 실습     (확장용)
  prompts/                # AI에게 도움받기 카드, 평평한 폴더 (Phase 3·5)
  kits/<kit-id>/          # 실습 키트 원본(kit.yaml + 자료) (Phase 2·4)
  templates/ project/ resources/ optional/codex/
  instructor/             # 공개 가능한 진행 안내만 (CD-02)
public/                   # 이미지, 가상 데이터. downloads는 빌드 산출물
src/                      # Astro 표준 구조 (Phase 1)
scripts/                  # execute.py, validate_course.py, 생성·승인 명령, 테스트
deliverables/             # 제안서 개정본 등 사이트 밖 산출물
phases/                   # Harness phase·step
references/               # 비공개 원본(.gitignore, 커밋 금지)
```

## 2. 데이터 흐름
```
content/course.yaml ──┬─> 사이트 내비게이션·시간표·이전/다음 (Phase 1)
                      ├─> 교시 페이지의 목표·산출물·결과 확인 블록
                      └─> validate_course.py (구조·추적성·커버리지)
content/prompts/*.md ─> 교시 본문 <PromptCard id> ─> /prompts 자동 목록
product-features.yaml ─> <Feature id show> (확인일 자동 표시, unavailable이면 fallback 표시, show로 detail·fallback 본문 표시)
sources.yaml ─────────> <Source id article> (시행일·조문 표시)
external-links.yaml ──> <ExternalLink id tab> (준비 전이면 fallback_kind에 따라 표 양식 또는 다운로드)
content/kits/ ────────> 빌드 시 zip·xlsx 다운로드 생성 (public/downloads에 직접 커밋 금지)
```
원칙: 한 정보는 한 곳에만 있다. 목록 페이지(/prompts, /practice)는 수작업으로 만들지 않고 원천에서 생성한다.

## 3. 스키마 담당 (중복 금지)
| 대상 | 검사 주체 | 이유 |
|---|---|---|
| 등록부 yaml(`content/*.yaml`) | `scripts/validate_course.py`(Python)만 | 교차 파일 규칙이 많고 Phase 0부터 필요 |
| MDX frontmatter(교시·카드·모듈) | `src/content.config.ts`(zod)만 | 빌드 단계에서 차단, 웹 편집도 걸러짐 |
| 둘 사이의 교차 규칙(카드 ID 존재 등) | validator | zod는 파일 단위만 본다 |

같은 규칙을 두 곳에 구현하지 않는다. 규칙 ID와 층은 [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md).

## 4. course.yaml 스키마 요약
| 키 | 내용 |
|---|---|
| `course` | 과정명, `edition`(개설 차수) |
| `constraints` | 총 시간, Day 수, 교시 수, 교시 분, 핵심 활동 상한, 요소 최소 교시 수, 카드 상한, 확인일 경과 기준 — **validator는 이 값을 읽고 하드코딩하지 않는다** |
| `elements` · `subjects` · `supports` · `activity_kinds` | 허용값 사전 (6요소, 교과목 7개, 지원 방식 9종, 활동 종류) |
| `completion` | 필수·선택 산출물, 참여 조건, 사전·사후 자기진단 |
| `cards[]` | id, lesson(교시 ID 또는 common), title, category(A~I), level(1~3), where, track, **status, reviewed_hash** |
| `lessons[]` | id(의미형 고정), day, number, title, type(concept/practice/project), subject, track, **status, reviewed_hash**, elements, activities[kind,name,minutes], objectives[id,text,outputs,checks], outputs[id,text,used_by], checks[id,text], cards, stuck_points[id,text,supports,card], skip_if_short |
| `modules[]` | 교시가 아닌 추가 콘텐츠(시간 합계 제외): id, title, track, status, path |

- `objectives[].checks`는 그 목표를 확인하는 `lessons[].checks[].id` 목록이다. 학습목표마다 1개 이상(V-LSN-005, [LEARNING_OBJECTIVES.md](LEARNING_OBJECTIVES.md) 3절).
- `checks`를 문자열 목록으로 쓰는 기존 형식은 과거 형식이며 planned 교시에서만 허용된다. draft로 올리는 교시는 `{id, text}` 형식으로 바꾼다.

external-links.yaml의 대안 필드:
| 키 | 내용 |
|---|---|
| `fallback` | 링크가 준비되기 전 수강생이 할 일(한 문장) |
| `fallback_kind` | `template`(등록부의 표 양식을 표시) / `download`(실제 존재하는 다운로드 파일) / `none`(대안 없음 — 준비 전에는 교시에서 참조할 수 없음) |
| `fallback_templates` | `fallback_kind: template`일 때 탭 ID → `title`(탭 이름), `columns`(열 이름 목록) |

## 5. 사이트 구조와 URL 규칙 (Phase 1에서 구현)
| URL | 원천 |
|---|---|
| `/` | 과정 소개, 2일 지도, 6요소 한 장 |
| `/before` | 사전 준비(계정·접속 확인, 두 창 나란히 쓰기, 예시 5종 미리보기) |
| `/course`, `/course/day{d}/{nn}` | course.yaml + `content/day{d}/{nn}.mdx`. 정규 14교시만 번호형 URL |
| `/practice`, `/practice/<slug>` | 교시 실습 자동 목록 + `content/modules/` |
| `/prompts` | `content/prompts/` 자동 생성(분류 × 교시 필터) |
| `/templates`, `/project`, `/resources` | 템플릿, 예시 5종 키트, 용어집·출처·제품 정보·알려진 문제 |
| `/optional/codex` | 선택 심화(첫 줄: 몰라도 수료에 지장 없음) |

- status가 `planned`인 교시는 "준비 중" 페이지로 빌드된다. 따라서 일부 교시만 만든 상태에서도 빌드와 링크 검사가 통과한다.
- 교시 파일명은 번호(`03.mdx`), 교시 ID는 frontmatter `lesson_id`로 course.yaml과 연결한다.

## 6. 컴포넌트 규약 (Phase 1에서 구현, 내부 구현은 step 재량)
| 컴포넌트 | 입력 | 규칙 |
|---|---|---|
| `PromptCard` | `id` | 카드 파일을 읽어 5칸 뼈대·문장별 해설·붙여넣을 곳 배지·복사 버튼·3단계 펼침을 표시. 기본 단계는 카드의 `default_level` |
| `CopyButton` | 대상 텍스트 | Clipboard API 우선, 실패 시 선택 후 복사. "대괄호를 모두 바꿨나요?" 확인 |
| `Feature` | `id`, `show`(선택: `detail` / `fallback`) | 기능명과 확인일 표시. status가 unavailable이면 fallback 문구 표시. `show="detail"`은 등록부 `detail`을, `show="fallback"`은 등록부 `fallback`을 본문 안에 표시한다 |
| `ExternalLink` | `id`, `tab`(선택) | active이고 url이 있으면 링크. 준비 전이면 `fallback` 문구와 함께, `fallback_kind: template`이면 `tab`에 해당하는 `fallback_templates` 표 양식을 복사 가능한 형태로 표시 |
| `Source` | `id`, `article` | 법령명·조문·시행일 표시 |
| `Callout` | `kind`(주의·팁·검토) | 주의사항 강조 |
| `Checklist` | 항목 | 진행 체크(localStorage), 진행 초기화 버튼 |
| `TrackBadge` | `track` | 필수/선택 배지 |
| `LessonNav` | 교시 ID | 이전/다음, 현재 Day·교시 |

## 7. 빌드 두 가지와 오프라인 제약
- `npm run verify` → lint(eslint + astro check) + build + vitest + pytest + validate. `--scope` 인자는 validator에만 전달한다. Windows·Linux 모두에서 python 실행 파일을 자동으로 고른다.
- `npm run test:e2e` → Playwright(Chromium). verify와 분리(ADR-012).
- `npm run build` → `dist/` (Vercel)
- `npm run build:offline` → `dist-offline/` + zip (CD-05). 링크를 상대경로와 `.html`로 변환한다.
- **Chrome은 file://에서 모듈 스크립트를 차단한다.** 복사·체크리스트 등 인터랙션 스크립트는 인라인 비모듈 스크립트(Astro `is:inline`)로 쓴다. 펼침은 가능하면 `<details>`로 JS 없이 만든다.
- 외부 CDN·웹폰트에 의존하지 않는다(교육망 차단 대비).

## 8. 강사 안내 렌더링
- `content/instructor/`의 공개 가능한 진행 안내(소요시간, 시연 순서, 흔한 오류, 생략 항목)는 교시 페이지 하단 접이식 "강사 안내"로 표시한다.
- 예상 질문의 답, 운영 내부 메모, 수강생 정보는 저장소에 두지 않는다(CD-02).

## 9. 에셋 규칙
- 이미지는 `public/images/<lesson-id>/`, 파일명에 캡처 대상 기능 ID를 넣는다(예: `chatgpt-projects-create.png`).
- 캡처는 sources.yaml 또는 product-features.yaml에 캡처일과 함께 등록한다. 계정 식별정보를 가린다.
- 도식은 SVG로 만들고 텍스트는 SVG 안의 실제 텍스트로 둔다(접근성).

## 10. 검토 상태와 승인 (ADR-005, ADR-011)
- `status: planned → draft → reviewed`. 교시·카드의 status와 `reviewed_hash`는 **course.yaml에만** 둔다. 교시 MDX와 카드 파일 frontmatter에는 상태 필드를 두지 않는다.
- AI step은 course.yaml에서 자기 교시·카드의 status만 `draft`로 바꾼다.
- `npm run review:approve <id>`(Phase 1) — 사람이 실행한다. 대상 콘텐츠 파일(교시 MDX 또는 카드 파일)의 해시를 계산해 course.yaml 해당 항목의 `reviewed_hash`에 기록하고 status를 `reviewed`로 바꾼다. 콘텐츠 파일은 수정하지 않는다.
- **해시 규칙**: 파일을 UTF-8로 읽고 줄바꿈을 LF로 바꾼 뒤 SHA-256을 계산한다. Windows 작업 폴더(CRLF)와 CI(LF)에서 같은 값이 나와야 한다.
- 이후 콘텐츠 파일이 바뀌면 validator가 해시 불일치를 오류로 보고한다(V-REV-002). 다시 검토하려면 수정 후 `review:approve`를 다시 실행한다.

## 11. 확장 절차
| 추가 대상 | 절차 | AC |
|---|---|---|
| 새 실습(모듈) | `npm run new:module <slug>` → `content/modules/<slug>.mdx` 작성 → course.yaml `modules`에 1줄 추가 | `npm run verify -- --scope module:<slug>` |
| 교시 교체 | course.yaml 해당 교시 항목 교체(ID는 새로 부여) → 기존 ID를 참조하던 카드·산출물의 used_by를 validator 보고대로 수정 | `validate_course.py` 오류 0 |
| 카드 추가 | 막힘 지점을 course.yaml `stuck_points`에 먼저 추가 → `cards`에 등록 → `npm run new:prompt <id>` | V-CRS-008 통과 |
| 키트 추가 | `npm run new:kit <id>` → kit.yaml 필수 구성요소 채움 | 키트 규칙 통과(Phase 2) |
| 제품 기능·출처 추가 | 등록부에 항목 추가(확인일·출처 필수) → 본문에서 ID로 참조 | V-REG-001~004 |
| 개설 차수 갱신 | `validate_course.py --pre-launch` → 만료된 제품 정보·법령 재확인 → 바뀐 콘텐츠를 draft로 되돌려 재검토 → `edition` 갱신·git 태그·CHANGELOG | `--production` 통과 |

새 작업은 `/harness`로 새 phase를 만들어 진행한다. 기존 교시 번호 URL은 바꾸지 않는다.
