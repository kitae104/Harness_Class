# Step 0: repo-connect

## 읽어야 할 파일

먼저 아래 파일들을 읽고 이 step의 역할을 파악하라:

- `/CLAUDE.md` — CRITICAL: 원작자 허락 전 push 금지(CD-15), `references/` 커밋 금지
- `/docs/ADR.md` — ADR-007(브랜치·CI·main 보호), ADR-009(Public 저장소 공개 범위), ADR-010(호스팅 요금제), ADR-013(이 phase를 분리한 이유), CD-15
- `/docs/DEPLOYMENT.md` — 1절 전제, 3절 저장소 연결, 4절 CI, 5절 Vercel 연결, 6절 Preview
- `/docs/OPEN_QUESTIONS.md` — OQ-01(원작자 허락), OQ-09(Vercel 요금제), OQ-11(저장소 URL), OQ-13(라이선스)
- `/.github/workflows/verify.yml` — 1-web-foundation step 0에서 만든 CI 파일
- `/.gitignore` — `references/` 제외 확인

## 작업 목적

GitHub 저장소와 Vercel을 연결하는 작업이 **사람이 할 일을 모두 마쳤는지 확인하고 기록하는 관문**이다. 이 phase는 콘텐츠 phase와 분리되어 있어서, 원작자 허락을 기다리는 동안에도 콘텐츠 제작은 진행된다(ADR-013). 배포 phase만 이 phase에 의존한다.

Claude는 push·저장소 생성·Vercel 설정을 **직접 하지 않는다.** 사람이 끝낸 결과를 확인하고, 해결된 OQ를 기록한다.

## 수정/생성 대상

- 수정: `docs/OPEN_QUESTIONS.md` — 확인된 OQ만 `closed`로 바꾸고 해결 내용을 적는다
- 수정: `docs/DEPLOYMENT.md` — 1절 "현재 상태와 전제"를 연결 완료 상태로 갱신
- 생성(조건부): `LICENSE` — OQ-13에서 사용자가 라이선스를 정했고 그 문구를 제공한 경우에만

## 작업 범위

1. **선행 조건 확인** — 아래가 모두 사실이어야 진행한다. 하나라도 아니면 3번으로 간다.
   - `docs/OPEN_QUESTIONS.md`에서 OQ-01(원작자 허락)과 OQ-11(저장소 URL)의 해결 내용이 사용자에 의해 기록되어 있다. 또는 이 step을 실행하기 전 사용자가 step 파일 끝의 "사용자 입력" 절에 값을 적어 두었다.
   - `git remote get-url origin`이 `jha0313/harness_framework`가 아닌 사용자 저장소를 가리킨다.
   - `git ls-files references`의 출력이 비어 있다.
   - `.github/workflows/verify.yml`이 있다.
2. **확인되면**
   - `npm run verify`를 실행해 통과를 확인한다.
   - 사용자가 CI 실행 결과·Vercel Preview URL을 "사용자 입력"에 적었으면 그 내용을 DEPLOYMENT.md 1절에 기록한다.
   - OQ-01·OQ-11을 closed로 바꾸고 해결 내용을 적는다. OQ-09(요금제)와 OQ-13(라이선스)은 사용자가 결정을 적은 경우에만 closed로 바꾼다.
   - 해결된 OQ를 가리키는 `[TBD: OQ-01]`, `[TBD: OQ-11]` 태그가 이 step의 허용 경로 안에 남아 있으면 지운다. 허용 경로 밖에 남은 태그는 목록으로 summary에 적는다(V-TAG-002 경고로 추적된다).
3. **확인되지 않으면** 아무 파일도 고치지 말고 blocked로 기록한다. `blocked_reason`에 사용자가 할 일을 적는다:
   1. 원작자에게 사용 허락 또는 라이선스를 받는다(OQ-01).
   2. 사용자 계정에 Public 저장소를 만든다.
   3. `git remote set-url origin <URL>` 후 main과 완료된 phase 브랜치를 push한다. push 전 `git ls-files references`의 출력이 비어 있는지 확인한다.
   4. main 브랜치 보호를 설정한다(PR 필수, CI 통과 필수, force push 금지).
   5. Vercel에서 저장소를 Import한다(Astro 자동 인식, Build `npm run build`, Output `dist`). 요금제는 OQ-09 결정을 따른다.
   6. 첫 CI 실행과 Preview URL을 확인한다.
   7. 결과를 이 파일 끝 "사용자 입력" 절에 적고, step status를 `pending`으로 되돌린 뒤 `python scripts/execute.py 1b-repo-connect`를 다시 실행한다.

## 수정 허용 경로

`docs/OPEN_QUESTIONS.md`, `docs/DEPLOYMENT.md`, `LICENSE`

이 밖의 파일은 수정하지 마라.

## Acceptance Criteria

```bash
git ls-files references
git remote get-url origin
npm run verify
```

- 첫 명령의 출력이 비어 있어야 한다.
- 두 번째 명령의 출력에 `jha0313/harness_framework`가 없어야 한다.
- 세 번째 명령이 통과해야 한다.

## 검증 절차

1. 위 AC 커맨드를 실행하고 세 조건을 확인한다.
2. `python scripts/validate_course.py`로 OPEN_QUESTIONS 수정 후에도 오류 0인지 확인한다(V-TAG-001).
3. 결과에 따라 `phases/1b-repo-connect/index.json`의 step 0을 업데이트한다:
   - 모두 충족 → `"status": "completed"`, `"summary": "저장소 URL, CI·Preview 확인 결과, 닫은 OQ 목록을 한 줄로"`
   - 선행 조건 미충족 → `"status": "blocked"`, `"blocked_reason": "작업 범위 3의 사용자 작업 목록과 현재 미충족 조건"` 후 즉시 중단
   - 그 밖의 오류 → `"status": "error"`, `"error_message": "구체적 에러 내용"`

## 금지사항

- `git push`, `git remote set-url`, `gh repo create`, Vercel CLI 배포를 실행하지 마라. 이유: 원작자 허락과 저장소 결정은 사람의 일이다(CD-15). 공개는 되돌릴 수 없다.
- `execute.py --push`를 쓰지 마라. 이유: 같은 이유.
- 사용자가 결정하지 않은 라이선스 문구를 만들어 LICENSE를 생성하지 마라. 이유: 법적 선택이다(OQ-13).
- `references/`나 비공개 자료를 git에 추가하지 마라. 이유: CLAUDE.md CRITICAL, ADR-009.
- 3회 재시도 동안 선행 조건이 그대로면 추가 시도 없이 blocked로 기록하라. 이유: 사람 개입 없이는 결과가 바뀌지 않는다.

## 사용자 입력

(사용자가 연결 작업을 마친 뒤 아래를 채운다. 비어 있으면 이 step은 blocked로 끝난다.)

- 원작자 허락(OQ-01): 
- 저장소 URL(OQ-11): 
- 첫 CI 실행 결과 링크: 
- Vercel Preview URL: 
- Vercel 요금제 결정(OQ-09): 
- 라이선스 결정과 문구 출처(OQ-13): 
