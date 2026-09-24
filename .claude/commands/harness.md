이 프로젝트는 Harness 프레임워크를 사용한다. 아래 워크플로우에 따라 작업을 진행하라.

---

## 워크플로우

### A. 탐색

`/docs/` 하위 문서(PRD, ARCHITECTURE, ADR 등)를 읽고 프로젝트의 기획·아키텍처·설계 의도를 파악한다. 필요시 Explore 에이전트를 병렬로 사용한다.

### B. 논의

구현을 위해 구체화하거나 기술적으로 결정해야 할 사항이 있으면 사용자에게 제시하고 논의한다.

### C. Step 설계

사용자가 구현 계획 작성을 지시하면 여러 step으로 나뉜 초안을 작성해 피드백을 요청한다.

설계 원칙:

1. **Scope 최소화** — 하나의 step에서 하나의 레이어 또는 모듈만 다룬다. 여러 모듈을 동시에 수정해야 하면 step을 쪼갠다.
2. **자기완결성** — 각 step 파일은 독립된 Claude 세션에서 실행된다. "이전 대화에서 논의한 바와 같이" 같은 외부 참조는 금지한다. 필요한 정보는 전부 파일 안에 적는다.
3. **사전 준비 강제** — 관련 문서 경로와 이전 step에서 생성/수정된 파일 경로를 명시한다. 세션이 코드를 읽고 맥락을 파악한 뒤 작업하도록 유도한다.
4. **시그니처 수준 지시** — 함수/클래스의 인터페이스만 제시하고 내부 구현은 에이전트 재량에 맡긴다. 단, 설계 의도에서 벗어나면 안 되는 핵심 규칙(멱등성, 보안, 데이터 무결성 등)은 반드시 명시한다.
5. **AC는 실행 가능한 커맨드** — "~가 동작해야 한다" 같은 추상적 서술이 아닌 실제 실행 가능한 검증 커맨드를 포함한다. 이 프로젝트의 기본 AC는 `npm run verify -- --scope <대상>`이며, Phase 1 이전에는 `python -m pytest scripts -q && python scripts/validate_course.py --docs-only`를 쓴다.
6. **주의사항은 구체적으로** — "조심해라" 대신 "X를 하지 마라. 이유: Y" 형식으로 적는다.
7. **네이밍** — step name은 kebab-case slug로, 해당 step의 핵심 모듈/작업을 한두 단어로 표현한다 (예: `project-setup`, `api-layer`, `auth-flow`).
8. **수정 허용 경로** — 모든 step에 `allowed_paths`(glob 목록)를 지정한다. 공유 등록부(`content/*.yaml`)는 해당 step이 소유할 때만 포함하고, 그 경우에도 "추가만" 하도록 금지사항에 적는다.
9. **콘텐츠는 draft까지만** — AI step은 콘텐츠 `status`를 `draft`까지만 올린다. `reviewed`는 사람이 `npm run review:approve <id>`로만 올린다.
10. **콘텐츠 Phase의 처음과 끝** — 교시 유형의 첫 콘텐츠(기준 예시)는 phase의 첫 step으로 만들고 바로 뒤에 `human-review` step을 둔다. 콘텐츠 phase의 마지막 step도 `human-review`다.

### D. 파일 생성

사용자가 승인하면 아래 파일들을 생성한다.

#### D-1. `phases/index.json` (전체 현황)

여러 task를 관리하는 top-level 인덱스. 이미 존재하면 `phases` 배열에 새 항목을 추가한다.

```json
{
  "phases": [
    {
      "dir": "1-web-foundation",
      "status": "pending",
      "depends_on": ["0-foundation"]
    }
  ]
}
```

- `dir`: task 디렉토리명.
- `depends_on`: 선행 phase 디렉토리 목록. execute.py는 선행 phase가 `main`에 병합되어 있고 모든 step이 completed인지 확인한 뒤에만 실행한다. 새 브랜치는 `main`에서 만든다.
- `summary`: phase 완료 시 execute.py가 step summary를 모아 자동 기록하며, 이후 phase 프롬프트에 "이전 Phase 요약"으로 주입된다. 생성 시 넣지 않는다.
- `status`: `"pending"` | `"completed"` | `"error"` | `"blocked"`. execute.py가 실행 중 자동으로 업데이트한다.
- 타임스탬프(`completed_at`, `failed_at`, `blocked_at`)는 execute.py가 상태 변경 시 자동 기록한다. 생성 시 넣지 않는다.

#### D-2. `phases/{task-name}/index.json` (task 상세)

```json
{
  "project": "<프로젝트명>",
  "phase": "<task-name>",
  "guardrail_docs": ["PROMPT_GUIDE.md", "PRACTICE_DESIGN.md"],
  "steps": [
    { "step": 0, "name": "d1-04-exemplar", "status": "pending", "allowed_paths": ["content/day1/04.mdx", "content/prompts/*"] },
    { "step": 1, "name": "human-review", "status": "pending", "allowed_paths": [] },
    { "step": 2, "name": "d1-02", "status": "pending", "allowed_paths": ["content/day1/02.mdx", "content/prompts/*"] }
  ]
}
```

필드 규칙:

- `project`: 프로젝트명 (CLAUDE.md 참조).
- `phase`: task 이름. 디렉토리명과 일치시킨다.
- `guardrail_docs`: 이 phase에 추가로 주입할 docs 파일명. 고정 core 문서(PRD, ARCHITECTURE, ADR, CONTENT_GUIDE)와 CLAUDE.md는 항상 주입된다. 필드를 생략하면 docs 전체가 주입된다.
- `steps[].step`: 0부터 시작하는 순번.
- `steps[].name`: kebab-case slug.
- `steps[].status`: 초기값은 모두 `"pending"`.
- `steps[].allowed_paths`: 이 step이 수정할 수 있는 경로(glob). 자기 phase 디렉토리는 항상 허용된다. 범위 밖 변경이 있으면 execute.py가 completed를 인정하지 않고 에러로 재시도시킨다. 빈 목록이면 어떤 파일도 수정하지 않는 step이다.

human-review step 규칙:

- **human-review step마다** `steps[].review_targets`(예: `["kit:day1-civil", "lesson:d1-context", "card:card-source-rule-snippet"]`)로 그 시점에 승인받아야 할 항목만 적는다. 대상 형식: `lesson:<id>` · `card:<id>` · `kit:<id>`.
- AC는 `python scripts/validate_course.py --scope phase:<phase-dir>:step<N> --require-reviewed`이다. validator는 그 step의 `review_targets`만 검사하므로, phase 안에 사람 검토 step을 여러 개 둘 수 있다.
- phase 전체 한 번만 검토하는 경우에는 phase 수준 `review_targets`와 `--scope phase:<phase-dir>`도 쓸 수 있다(하위 호환).
- 미승인 항목이 있으면 목록을 `blocked_reason`에 적고 `blocked`로 멈춘다.
- 사람이 `npm run review:approve <id>`로 승인한 뒤 status를 `pending`으로 되돌려 다시 실행하면 AC가 통과해 `completed`가 된다.

상태 전이와 자동 기록 필드:

| 전이 | 기록되는 필드 | 기록 주체 |
|------|-------------|----------|
| → `completed` | `completed_at`, `summary` | Claude 세션 (summary), execute.py (timestamp) |
| → `error` | `failed_at`, `error_message` | Claude 세션 (message), execute.py (timestamp) |
| → `blocked` | `blocked_at`, `blocked_reason` | Claude 세션 (reason), execute.py (timestamp) |

`summary`는 step 완료 시 산출물을 한 줄로 요약한 것으로, execute.py가 다음 step 프롬프트에 컨텍스트로 누적 전달한다. 따라서 다음 step에 유용한 정보(생성된 파일, 핵심 결정 등)를 담아야 한다.

`created_at`은 execute.py가 최초 실행 시 task 레벨에 한 번만 기록한다. step 레벨의 `started_at`도 execute.py가 각 step 시작 시 자동 기록한다. 생성 시 넣지 않는다.

#### D-3. `phases/{task-name}/step{N}.md` (각 step마다 1개)

```markdown
# Step {N}: {이름}

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {이전 step에서 생성/수정된 파일 경로}

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

{구체적인 구현 지시. 파일 경로, 클래스/함수 시그니처, 로직 설명을 포함.
코드 스니펫은 인터페이스/시그니처 수준만 제시하고, 구현체는 에이전트에게 맡겨라.
단, 설계 의도에서 벗어나면 안 되는 핵심 규칙은 명확히 박아넣어라.}

## 수정 허용 경로

{phase index.json의 allowed_paths와 동일하게 적는다. 이 밖의 파일은 수정하지 마라.}

## Acceptance Criteria

```bash
npm run verify -- --scope {대상}   # lint + build + test + validate_course
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 스택을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
   - 수치·제품 정보·출처를 본문에 직접 쓰지 않고 등록부 ID로 참조했는가?
   - 콘텐츠 status를 draft까지만 올렸는가?
3. 결과에 따라 `phases/{task-name}/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 (API 키, 외부 인증, 수동 설정 등) → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- {이 step에서 하지 말아야 할 것. "X를 하지 마라. 이유: Y" 형식}
- 기존 테스트를 깨뜨리지 마라
```

### E. 실행

```bash
python scripts/execute.py {task-dir}        # 순차 실행 (Windows는 python, macOS/Linux는 python3)
python scripts/execute.py {task-dir} --push  # 실행 후 push (CD-15: 원작자 허락 전에는 사용 금지)
```

execute.py가 자동으로 처리하는 것:

- 선행 phase 확인 — `depends_on`의 phase가 `main`에 병합·완료되지 않았으면 중단
- `feat-{task-name}` 브랜치 생성/checkout (새 브랜치는 `main`에서 생성)
- 가드레일 주입 — CLAUDE.md + core docs + `guardrail_docs`를 매 step 프롬프트에 포함 (UTF-8, stdin 전달)
- 컨텍스트 누적 — 완료된 step의 summary와 이전 phase의 summary를 다음 step 프롬프트에 전달
- 수정 허용 경로 검사 — `allowed_paths` 밖 변경이 있으면 completed를 인정하지 않고 재시도
- `HARNESS_EXECUTING=1` 설정 — 실행 중에는 Stop 훅이 전체 verify를 반복하지 않음
- 자가 교정 — 실패 시 최대 3회 재시도하며, 이전 에러 메시지를 프롬프트에 피드백
- 2단계 커밋 — 코드 변경(`feat`)과 메타데이터(`chore`)를 분리 커밋
- 타임스탬프 — started_at, completed_at, failed_at, blocked_at 자동 기록

에러 복구:

- **error 발생 시**: `phases/{task-name}/index.json`에서 해당 step의 `status`를 `"pending"`으로 바꾸고 `error_message`를 삭제한 뒤 재실행한다.
- **blocked 발생 시**: `blocked_reason`에 적힌 사유를 해결한 뒤, `status`를 `"pending"`으로 바꾸고 `blocked_reason`을 삭제한 뒤 재실행한다.
