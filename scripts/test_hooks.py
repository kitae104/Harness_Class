"""
.claude/hooks 스크립트 테스트.
훅은 stdin으로 JSON을 받고, exit 2일 때만 차단한다.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / ".claude" / "hooks"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash가 필요하다")


def run_hook(name, payload, env=None, cwd=None):
    import os
    full_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [BASH, str(HOOKS / name)],
        input=json.dumps(payload, ensure_ascii=False), capture_output=True, text=True,
        encoding="utf-8", env=full_env, cwd=cwd,
    )


def bash_call(command, tool="Bash"):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}}


class TestBlockDangerous:
    @pytest.mark.parametrize("cmd", [
        "rm -rf dist",
        "rm -fr node_modules",
        "git push --force origin main",
        "git push -f origin main",
        "git reset --hard HEAD~1",
        "psql -c 'DROP TABLE users'",
        "Remove-Item -Recurse -Force dist",
        "Remove-Item dist -Force -Recurse",
    ])
    def test_blocks_dangerous(self, cmd):
        r = run_hook("block-dangerous.sh", bash_call(cmd))
        assert r.returncode == 2
        assert "BLOCKED" in r.stderr

    @pytest.mark.parametrize("cmd", [
        "git status",
        "rm dist/old.txt",
        "git push -u origin feat-1-web-foundation",
        "git reset HEAD -- file",
        "python -m pytest scripts -q",
        "Remove-Item old.txt",
    ])
    def test_allows_safe(self, cmd):
        r = run_hook("block-dangerous.sh", bash_call(cmd))
        assert r.returncode == 0


class TestVerifyOnStop:
    def test_skips_without_package_json(self, tmp_path):
        r = run_hook("verify-on-stop.sh", {"hook_event_name": "Stop"},
                     env={"CLAUDE_PROJECT_DIR": str(tmp_path), "HARNESS_EXECUTING": ""})
        assert r.returncode == 0

    def test_skips_when_harness_executing(self, tmp_path):
        (tmp_path / "package.json").write_text('{"scripts": {"verify": "exit 1"}}', encoding="utf-8")
        r = run_hook("verify-on-stop.sh", {"hook_event_name": "Stop"},
                     env={"CLAUDE_PROJECT_DIR": str(tmp_path), "HARNESS_EXECUTING": "1"})
        assert r.returncode == 0

    def test_skips_when_stop_hook_active(self, tmp_path):
        (tmp_path / "package.json").write_text('{"scripts": {"verify": "exit 1"}}', encoding="utf-8")
        r = run_hook("verify-on-stop.sh", {"hook_event_name": "Stop", "stop_hook_active": True},
                     env={"CLAUDE_PROJECT_DIR": str(tmp_path), "HARNESS_EXECUTING": ""})
        assert r.returncode == 0

    @pytest.mark.skipif(shutil.which("npm") is None, reason="npm이 필요하다")
    def test_blocks_stop_when_verify_fails(self, tmp_path):
        (tmp_path / "package.json").write_text('{"scripts": {"verify": "node -e \\"process.exit(1)\\""}}', encoding="utf-8")
        r = run_hook("verify-on-stop.sh", {"hook_event_name": "Stop", "stop_hook_active": False},
                     env={"CLAUDE_PROJECT_DIR": str(tmp_path), "HARNESS_EXECUTING": ""})
        assert r.returncode == 2
        assert "verify" in r.stderr
