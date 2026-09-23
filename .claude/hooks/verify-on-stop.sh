#!/usr/bin/env bash
# Stop 훅: 대화형 세션이 끝날 때 전체 검증을 실행한다.
# - package.json이 없으면(Phase 1 이전) 건너뛴다.
# - execute.py가 실행한 세션(HARNESS_EXECUTING=1)은 step AC가 검증하므로 건너뛴다.
# - 이미 한 번 막았으면(stop_hook_active) 무한 반복을 막기 위해 통과시킨다.
input=$(cat)
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if [ "${HARNESS_EXECUTING:-}" = "1" ]; then exit 0; fi
if [ ! -f package.json ]; then exit 0; fi
if printf '%s' "$input" | grep -qE '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then exit 0; fi

if ! out=$(npm run verify 2>&1); then
  printf '%s\n' "$out" | tail -n 40 >&2
  echo "npm run verify 실패: 위 오류를 수정하세요." >&2
  exit 2
fi
exit 0
