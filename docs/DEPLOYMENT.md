# 배포 가이드

Claude Code에서 자료 수정 → 로컬 검증 → commit → GitHub push → Vercel Preview 확인 → main 반영 → Production 갱신. Phase 1 이전에는 사이트가 없으므로 1~2절의 Phase 0 절차만 적용된다. 사이트 명령(`npm run ...`)은 Phase 1에서 구현되며, 이 문서는 Phase 8에서 확정한다 [PROVISIONAL].

## 1. 현재 상태와 전제 (2026-09-24 확인)
- 원작자 사용 허락: 사용자가 직접 확인했다(CD-15, OQ-01 closed). 콘텐츠 라이선스는 아직 정하지 않았다(OQ-13 open, LICENSE 없음).
- GitHub: Public 저장소 https://github.com/kitae104/Harness_Class, origin이 이 저장소를 가리킨다(OQ-11 closed). `git ls-files references` 출력은 비어 있다.
- CI: `.github/workflows/verify.yml`의 verify workflow 성공을 사용자가 확인했다.
- main Ruleset: Pull Request 필수, verify status check 통과 필수, branch up-to-date 필수, force push 금지.
- Vercel Production: https://harness-class.vercel.app/ (D1-01: https://harness-class.vercel.app/course/day1/01/) 배포 성공.
- Vercel Preview: 브랜치 `feat-repo-connect` → https://harness-class-git-feat-repo-connect-aqua0405-2866s-projects.vercel.app/ (D1-01: `/course/day1/01/`). 사용자가 확인했다. Preview는 Vercel 배포 보호가 켜져 있어 로그인하지 않으면 Vercel 로그인 화면이 보인다.
- 요금제: 개인적·비상업적 강의자료 제작 프로젝트이므로 현재 Vercel Hobby를 유지한다(OQ-09 closed). 유료 강의 운영 등 상업적 이용으로 바뀌면 다시 검토한다 [AS-OF: vercel-hobby-commercial].

## 2. 로컬 실행과 검증
```bash
pip install -r requirements-dev.txt       # PyYAML, pytest
python -m pytest scripts -q               # Harness 테스트
python scripts/validate_course.py --docs-only   # Phase 0 AC

# Phase 1 이후
npm install
npm run dev          # 개발 서버
npm run build        # dist/ 생성
npm run preview      # 빌드 결과 확인 (Vercel 대신 강사 PC에서 수업할 때도 사용)
npm run build:offline  # dist-offline/ + zip (교육망에서 Vercel이 막힐 때)
npm run verify -- --scope <대상>   # lint(eslint + astro check) + build + vitest + pytest + validate
npm run test:e2e     # Playwright(Chromium) 브라우저 테스트, 최초 1회 npx playwright install chromium
```
Windows는 `python`, macOS·Linux는 `python3`를 쓴다.

**Windows Smart App Control**: 서명 없는 네이티브 모듈(`.node`)을 막을 수 있다. 실제로 Astro 컴파일러(`@astrojs/compiler-binding-win32-x64-msvc`)가 때때로 막혔다(2026-09-25). 그래서 `npm install`·`npm ci` 뒤 `postinstall`(`scripts/ensure_astro_wasi.mjs`)이 Windows에서 같은 버전의 WebAssembly 대체 패키지(`@astrojs/compiler-binding-wasm32-wasi`)를 넣고, Astro는 네이티브가 막힐 때 자동으로 그것을 쓴다. WSL 없이 Windows에서 모든 명령을 실행한다. 대체 경로를 직접 시험하려면 `NAPI_RS_FORCE_WASI=1`로 `npm run verify`를 돌린다. Linux(CI·Vercel)에서는 아무것도 하지 않는다.

## 3. GitHub 저장소 연결 (`1b-repo-connect` phase, 사용자 작업, ADR-013)
1. 원작자 허락을 받는다(CD-15).
2. 사용자 계정에 Public 저장소를 만든다.
3. `git remote set-url origin <사용자 저장소 URL>` 후 main과 phase 브랜치를 push한다.
4. `references/`가 추적되지 않는지 확인한다(`git ls-files references`가 비어 있어야 함, V-SEC-001).
5. main 브랜치 보호: PR 필수, CI 통과 필수, force push 금지.

## 4. CI (GitHub Actions, Phase 1에서 추가)
- `.github/workflows/verify.yml`: PR과 main push에서 setup-node(.nvmrc), setup-python, `pip install -r requirements-dev.txt`, `npm ci`, `npm run verify`.
- Vercel 빌드는 Python 검사를 돌리지 않으므로 CI가 등록부·교차 규칙을 강제한다(ADR-004, ADR-007).

## 5. Vercel 프로젝트 연결
1. Vercel에서 GitHub 저장소를 Import한다. 프로젝트는 1개.
2. Framework preset은 Astro(자동 인식), Build command `npm run build`, Output `dist`.
3. Production branch는 `main`.
4. 요금제는 OQ-09 결정에 따른다.

## 6. Preview 확인
- phase 브랜치를 push하고 PR을 열면 Vercel이 Preview URL을 만든다 [AS-OF: vercel-preview-deployments].
- 강사는 Preview URL에서 이번 phase의 교시를 열어 확인한다: 필수 경로, 복사 버튼, 이전/다음, 휴대폰 폭 화면.
- 허락 전에는 `npm run build && npm run preview`로 대신한다.

## 7. Production 배포 기준
- CI 통과 + Preview 확인 완료
- `python scripts/validate_course.py --production` 오류 0 (core 전부 reviewed, 해시 일치)
- 원작자 허락(CD-15)과 요금제 결정(OQ-09) 완료

## 8. 배포 실패 시 확인
| 증상 | 확인할 곳 |
|---|---|
| CI 실패 | Actions 로그의 validator 규칙 ID → [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md)에서 규칙 의미 확인 |
| Vercel 빌드 실패 | Vercel 배포 로그, 로컬 `npm run build` 재현 |
| Preview는 되는데 교육망에서 안 열림 | 교육망 예외 도메인 목록에 사이트 도메인이 있는지, 없으면 오프라인 번들 |
| 오프라인 번들에서 복사 버튼이 안 됨 | 인라인 비모듈 스크립트 규칙(ARCHITECTURE 7절), V-WEB-002 |

## 9. 롤백
- Vercel 대시보드 Instant Rollback. Hobby는 직전 배포로만 가능 [AS-OF: vercel-instant-rollback].
- 또는 `git revert <커밋>` → PR → 병합(새 배포가 만들어짐). force push와 `reset --hard`는 쓰지 않는다(훅이 차단한다).

## 10. 오프라인 배포 (Vercel 불가 시, CD-05)
- `npm run build:offline`으로 만든 zip을 GitHub Releases 또는 USB로 배포한다.
- 수강생은 압축을 풀고 `index.html`을 브라우저로 연다. 복사·이동이 file://에서 동작하는지 Playwright로 검사한다(V-WEB-003).
- 강사 PC에서 `npm run preview`로 띄워 화면 공유하는 방법도 있다.
