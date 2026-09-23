#!/usr/bin/env bash
# PreToolUse 훅: 위험한 셸 명령을 차단한다.
# 입력은 stdin JSON(tool_input.command). exit 2 = 차단, stderr 메시지는 Claude에게 전달된다.
input=$(cat)

pattern='rm[[:space:]]+-[a-zA-Z]*[rR][a-zA-Z]*f|rm[[:space:]]+-[a-zA-Z]*f[a-zA-Z]*[rR]|git[[:space:]]+push([[:space:]].*)?[[:space:]](--force|-f)([[:space:]]|$|")|git[[:space:]]+reset[[:space:]]+--hard|DROP[[:space:]]+TABLE|Remove-Item[^|;]*-Recurse[^|;]*-Force|Remove-Item[^|;]*-Force[^|;]*-Recurse'

if printf '%s' "$input" | grep -qiE "$pattern"; then
  echo "BLOCKED: 위험한 명령어가 감지되었습니다 (rm -rf, force push, reset --hard, DROP TABLE, Remove-Item -Recurse -Force). 더 안전한 방법을 사용하세요." >&2
  exit 2
fi
exit 0
