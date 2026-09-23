# Step 3: ui-components

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 6절 컴포넌트 규약, 7절 오프라인 제약, 10절 검토 상태
- `/docs/UI_GUIDE.md` — 컴포넌트(AI에게 도움받기 카드 도식), 색상, 접근성, 애니메이션, 인쇄
- `/docs/PROMPT_GUIDE.md` — 카드 스키마, 5칸 뼈대, 3단계 겹침, 붙여넣을 곳 4종
- `/docs/PRACTICE_DESIGN.md` — 5절 기술별 단계, 6절 "왜" 이해 장치(문장별 해설)
- `/docs/PRODUCT_FEATURES.md` — `<Feature>`의 fallback 규칙
- `/content/glossary.yaml` — 수강생 화면 용어(따라 쓰기 / 바꿔 쓰기 / 직접 쓰기, AI에게 도움받기, 필수 / 선택)
- step 1 산출물: `/src/lib/course.ts`, `/src/lib/registries.ts`, `/src/lib/types.ts`, `/src/content.config.ts`
- step 2 산출물: `/src/layouts/*`, `/src/components/*`, `/src/styles/global.css`

## 작업 목적

교시 본문이 쓰는 **UI 컴포넌트**를 만든다. AI에게 도움받기 카드, 복사 버튼, 제품 정보·출처·외부 링크 표시, 주의 박스, 체크리스트, 배지, 발표 모드. 모든 인터랙션은 인터넷 없이 file://에서도 동작해야 한다.

## 수정/생성 대상

- 생성: `src/components/PromptCard.astro`, `src/components/CopyButton.astro`, `src/components/Feature.astro`, `src/components/Source.astro`, `src/components/ExternalLink.astro`, `src/components/Callout.astro`, `src/components/Checklist.astro`, `src/components/TrackBadge.astro`, `src/components/PresentationToggle.astro`
- 생성: `src/lib/prompt-text.ts`(대괄호 파싱 등 순수 함수), `tests/unit/prompt-text.test.ts`, `tests/fixtures/prompt-sample.md`(테스트 전용 가짜 카드)
- 수정: `src/styles/global.css`, `src/layouts/*`(발표 모드 토글 위치만)

## 작업 범위

1. **PromptCard** (`id` 입력)
   - `prompts` 컬렉션에서 카드를, course.yaml에서 카드 메타(level, where, category)를 읽는다.
   - **없는 id면 빌드를 실패시킨다.** 카드 파일이 없으면 "준비 중 카드" 자리표시를 보여 준다.
   - 제목 "AI에게 도움받기"와 붙여넣을 곳 배지를 둔다: 지침란 / Project 채팅 / 새 채팅 / 임시 채팅.
   - 언제·무엇을 넣나를 표시한다.
   - 기본 단계(course.yaml `level`)의 내용을 먼저 보여 준다. 나머지 단계는 `<details>`로 "힌트 보기(바꿔 쓰기)"와 "전체 보기(따라 쓰기)"로 펼친다. 직접 쓰기 단계는 5칸 뼈대만 보여 준다.
   - 프롬프트 블록에서 대괄호 부분은 배경색과 밑줄로 강조한다.
   - CopyButton과 "대괄호를 모두 바꿨나요?" 체크를 둔다.
   - 문장별 해설(요소 배지 ①~⑥ + 이유), 확인할 것, 그대로 믿으면 안 되는 부분, 다음 행동은 `<details>`로 둔다.
2. **CopyButton**
   - 대상 텍스트를 복사한다. 먼저 `navigator.clipboard.writeText`를 쓰고, 실패하면 textarea를 선택한 뒤 `document.execCommand('copy')`로 대체한다.
   - 성공하면 "복사됨" 텍스트를 표시한다(색만으로 알리지 않음). 키보드로 누를 수 있어야 한다.
   - **스크립트는 `<script is:inline>`** 한 번만 정의한다. 페이지에 버튼이 여러 개여도 전역 함수를 중복 정의하지 않는다.
3. **Feature** (`id`): product-features에서 기능명과 "확인일 YYYY-MM-DD"를 표시한다. status가 `unavailable`이면 `fallback` 문구를 주의 박스로 표시하고, `unverified`면 "확인 중" 표시를 붙인다. 없는 id면 빌드를 실패시킨다.
4. **Source** (`id`, `article?`): 출처 제목, 조문, 시행일(법령)을 표시한다. 없는 id면 빌드 실패.
5. **ExternalLink** (`id`): url이 있고 status가 `active`면 링크를 표시한다. 아니면 `fallback` 안내를 표시한다. 없는 id면 빌드 실패.
6. **Callout** (`kind`: 주의 | 팁 | 검토 | 확인필요): 왼쪽 굵은 선 + 옅은 배경. 아이콘만으로 의미를 전달하지 않는다.
7. **Checklist** (`id`, 항목 목록): 체크 상태를 `localStorage`에 저장한다. `localStorage` 접근은 try/catch로 감싼다(file://나 차단 환경). "진행 초기화" 버튼을 둔다. 스크립트는 `is:inline`.
8. **TrackBadge** (`track`): "필수" / "선택" 텍스트 배지.
9. **PresentationToggle**: 본문 글자를 키우고 사이드바를 숨기는 발표 모드. `is:inline` 스크립트로 `<html>`에 클래스를 토글하고 localStorage에 기억한다.
10. **`src/lib/prompt-text.ts`** (TDD): 순수 함수를 export하고 테스트를 먼저 쓴다.
    - `splitBrackets(text): Array<{text: string; bracket: boolean}>`
    - `listBrackets(text): string[]`
    - `levelLabel(level): string`(1→따라 쓰기, 2→바꿔 쓰기, 3→직접 쓰기, glossary와 일치)
    - `whereLabel(where): string`
11. 인쇄 CSS: 사이드바·버튼을 숨기고 `<details>`를 모두 펼친다.

## 수정 허용 경로

`src/components/*`, `src/layouts/*`(발표 모드 토글 배치만), `src/styles/*`, `src/lib/*`, `tests/unit/*`, `tests/fixtures/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run verify
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `dist/` 전체에서 `<script type="module"`이 없는지, 외부 URL을 불러오는 태그가 없는지 확인한다.
3. 아키텍처 체크리스트:
   - 카드 파일·교시 파일에서 status를 읽지 않고 course.yaml을 썼는가?(ADR-011)
   - 제품 정보·출처를 컴포넌트 안에 하드코딩하지 않았는가?
   - 모든 버튼에 텍스트 레이블이 있고 키보드로 쓸 수 있는가?
4. 결과에 따라 `phases/1-web-foundation/index.json`의 step 3을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "만든 컴포넌트 목록과 인라인 스크립트 방식을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/prompts/`에 실제 카드 파일을 만들지 마라. 테스트용 카드는 `tests/fixtures/`에만 둔다. 이유: 실제 카드는 막힘 지점 근거와 사람 검토가 필요한 콘텐츠다(PROMPT_GUIDE 1절).
- Astro 기본 `<script>`(모듈 번들)를 쓰지 마라. `is:inline`이나 `<details>`만 쓴다. 이유: file://에서 모듈 스크립트가 차단된다(ADR-008).
- 모델명, 메뉴 경로, 요금제 한도를 컴포넌트 문자열에 쓰지 마라. 이유: 제품 정보는 product-features.yaml에만 둔다(CLAUDE.md CRITICAL).
- 개발 용어("LEVEL 1", "Prompt Card", "플레이스홀더")를 화면 문구로 쓰지 마라. 이유: 수강생 화면 용어 규칙(banned-terms student scope).
- 애니메이션을 넣지 마라(펼침 0.15초 이하 전환과 복사 완료 표시만 허용). 이유: UI_GUIDE.
- 기존 테스트를 깨뜨리지 마라.
