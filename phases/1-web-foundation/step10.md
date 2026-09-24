# Step 10: registry-display

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 배경을 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 6절 컴포넌트 규약(step 8에서 보완한 `Feature show`, `ExternalLink` 대안 표 양식), 7절 오프라인 제약
- `/docs/UI_GUIDE.md` — 컴포넌트 절(step 8에서 보완), 접근성, 애니메이션
- `/docs/CONTENT_GUIDE.md` — 5절(대안·상세는 컴포넌트로 표시, 본문 재서술 금지)
- `/docs/PRODUCT_FEATURES.md` — 2절 `detail`·`fallback`
- `/content/product-features.yaml`, `/content/external-links.yaml`(`fallback_kind`, `fallback_templates`)
- `/src/components/Feature.astro`, `/src/components/ExternalLink.astro`, `/src/components/CopyButton.astro`, `/src/lib/registries.ts`, `/src/lib/types.ts`
- step 9 산출물: `/src/lib/types.ts`의 변경 내용

## 작업 목적

등록부의 정보를 본문에 다시 쓰지 않아도 되도록 컴포넌트가 직접 표시하게 만든다.

- `Feature`가 기능의 상세 설명과 대안을 표시한다.
- `ExternalLink`가 링크 준비 전에 대안 표 양식을 표시한다.

## 수정/생성 대상

- 수정: `src/components/Feature.astro`, `src/components/ExternalLink.astro`, `src/lib/registries.ts`·`src/lib/types.ts`(새 필드 읽기), 필요하면 `src/styles/*`
- 필요하면 수정: `src/components/CopyButton.astro`(여러 줄 텍스트 복사 지원이 없을 때만)
- 테스트: `tests/unit/*`, `tests/fixtures/*`

## 작업 범위

1. **`Feature`에 `show` 속성 추가** (`show?: 'detail' | 'fallback'`)
   - 없으면 현재 동작과 같다(기능명 + 확인일 + unavailable이면 대안 박스).
   - `show="detail"`: 기능명 뒤에 등록부 `detail`을 한 문장으로 표시한다.
   - `show="fallback"`: 등록부 `fallback`을 "대신 이렇게 합니다:" 문구와 함께 표시한다. status와 무관하게 "잘 안 될 때" 절에서 쓴다.
   - 없는 id면 지금처럼 빌드 실패.
2. **`ExternalLink`에 `tab` 속성 추가** (`tab?: string`)
   - 링크가 active이고 url이 있으면 지금처럼 링크만 표시한다.
   - 준비 전이고 `fallback_kind: template`이면:
     - `fallback` 안내 문장을 보여 준다.
     - `fallback_templates[tab]`의 열로 만든 빈 표를 보여 준다.
     - 그 표를 **탭으로 구분한 머리행 텍스트**로 복사하는 CopyButton을 둔다(구글 시트에 붙이면 열이 나뉘게).
   - 준비 전인데 `tab`이 없거나 템플릿에 그 탭이 없으면 빌드를 실패시킨다(오류 메시지에 id와 tab 포함).
   - `fallback_kind`가 `download`나 `none`이면 현재처럼 `fallback` 문장만 표시한다.
3. **순수 함수(TDD)**: 표 양식을 텍스트로 만드는 함수(예: `templateToTsv(columns)`)와 대안 선택 로직을 `src/lib/*`에 export하고 테스트를 먼저 쓴다.
4. 스크립트는 기존 CopyButton의 `is:inline` 방식을 재사용한다. 새 모듈 스크립트를 만들지 않는다.

## 수정 허용 경로

`src/components/Feature.astro`, `src/components/ExternalLink.astro`, `src/components/CopyButton.astro`, `src/lib/*`, `src/styles/*`, `tests/unit/*`, `tests/fixtures/*`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
npm run lint
npm run build
npm test
python -m pytest scripts -q
```

(step 9에서 설명한 대로 `npm run verify` 전체는 D1-01의 V-LSN-005 오류 때문에 step 12 전까지 실패할 수 있다. 그래서 validator를 뺀 네 단계를 AC로 쓴다. `python scripts/validate_course.py`의 오류가 D1-01의 V-LSN-005뿐인지도 확인한다.)

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. `dist/`에 `<script type="module"`이 없는지 확인한다.
3. 아키텍처 체크리스트:
   - 제품 정보·링크 정보를 컴포넌트 안에 하드코딩하지 않고 등록부에서 읽었는가?
   - 기존 `Feature`·`ExternalLink` 사용처(D1-01)가 속성 없이도 그대로 빌드되는가?
4. 결과에 따라 `phases/1-web-foundation/index.json`의 step 10을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "Feature show 옵션과 ExternalLink tab 대안 표 양식(TSV 복사)을 한 줄로"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- `content/*`를 수정하지 마라. 이유: 등록부 변경은 step 8, D1-01 변경은 step 12의 범위다.
- 대안 문구나 표 열 이름을 컴포넌트에 하드코딩하지 마라. 이유: 등록부가 단일 원천이다(CLAUDE.md CRITICAL).
- 모듈 스크립트를 쓰지 마라. 이유: file://에서 차단된다(ADR-008).
- 애니메이션을 넣지 마라. 이유: UI_GUIDE.
- 기존 테스트를 깨뜨리지 마라.
