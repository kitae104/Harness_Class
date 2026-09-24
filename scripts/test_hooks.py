"""
.claude/hooks 스크립트 테스트.
훅은 stdin으로 JSON을 받고, exit 2일 때만 차단한다.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / ".claude" / "hooks"


def _is_wsl_launcher(path):
    """Windows의 System32·WindowsApps bash.exe는 WSL 실행기다. Windows 경로의 \\를 지워 훅을 찾지 못한다."""
    low = str(path).lower().replace("/", "\\")
    return "\\windows\\system32\\" in low or "\\windowsapps\\" in low


def find_bash():
    """훅을 실행할 bash. Windows에서는 Claude Code처럼 Git for Windows의 bash를 쓴다."""
    if sys.platform != "win32":
        return shutil.which("bash")
    candidates = []
    git = shutil.which("git")
    if git:
        # ...\Git\cmd\git.exe → ...\Git\bin\bash.exe
        candidates.append(Path(git).resolve().parent.parent / "bin" / "bash.exe")
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"), os.environ.get("LOCALAPPDATA")):
        if base:
            candidates += [Path(base) / "Git" / "bin" / "bash.exe", Path(base) / "Programs" / "Git" / "bin" / "bash.exe"]
    found = shutil.which("bash")
    if found and not _is_wsl_launcher(found):
        candidates.insert(0, Path(found))
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


BASH = find_bash()

pytestmark = pytest.mark.skipif(BASH is None, reason="bash(Windows는 Git Bash)가 필요하다")


def run_hook(name, payload, env=None, cwd=None):
    full_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [BASH, (HOOKS / name).as_posix()],
        input=json.dumps(payload, ensure_ascii=False), capture_output=True, text=True,
        encoding="utf-8", env=full_env, cwd=cwd,
    )


def bash_call(command, tool="Bash"):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}}


class TestFindBash:
    @pytest.mark.parametrize("path", [
        r"C:\Windows\System32\bash.exe",
        r"C:\Users\u\AppData\Local\Microsoft\WindowsApps\bash.exe",
    ])
    def test_wsl_launcher_detected(self, path):
        assert _is_wsl_launcher(path)

    def test_git_bash_not_wsl(self):
        assert not _is_wsl_launcher(r"C:\Program Files\Git\bin\bash.exe")

    def test_selected_bash_is_not_wsl(self):
        assert not _is_wsl_launcher(BASH)


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
