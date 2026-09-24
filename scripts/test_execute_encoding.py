"""
execute.py의 UTF-8 처리 테스트.

Windows의 기본 로캘 인코딩(cp949)에서 subprocess를 text=True로만 실행하면
UTF-8 출력(한글·기호)을 읽는 스레드가 UnicodeDecodeError로 죽고 stdout이 None이 된다.
여기서는 실제 자식 프로세스를 띄워 그 상황을 재현하고, 공통 실행 함수가
로캘과 무관하게 UTF-8로 처리하는지 검증한다.
"""

import io
import json
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import execute as ex
from test_execute import tmp_project, phase_dir, top_index, executor  # noqa: F401 (pytest fixtures)

KOREAN = "전입신고 14일 이내 ✓ ⚠ 확인 필요"


def py(code):
    return [sys.executable, "-c", code]


# ---------------------------------------------------------------------------
# run_process — 공통 subprocess 실행 함수
# ---------------------------------------------------------------------------

class TestRunProcess:
    def test_decodes_utf8_stdout_regardless_of_locale(self):
        code = f"import sys; sys.stdout.buffer.write({KOREAN!r}.encode('utf-8'))"
        r = ex.run_process(py(code))
        assert r.returncode == 0
        assert r.stdout == KOREAN

    def test_sends_stdin_as_utf8(self):
        code = "import sys; data = sys.stdin.buffer.read(); sys.stdout.buffer.write(data)"
        r = ex.run_process(py(code), input_text=KOREAN)
        assert r.stdout == KOREAN

    def test_invalid_utf8_stdout_raises_clear_error(self):
        code = "import sys; sys.stdout.buffer.write(b'{\"a\": \"\\xff\\xfe\"}')"
        with pytest.raises(ex.SubprocessDecodeError) as exc_info:
            ex.run_process(py(code))
        msg = str(exc_info.value)
        assert "UTF-8" in msg
        assert "\\xff" in msg

    def test_invalid_utf8_stdout_can_be_preserved_when_requested(self):
        code = "import sys; sys.stdout.buffer.write(b'ok \\xff end')"
        r = ex.run_process(py(code), stdout_errors="backslashreplace")
        assert r.stdout == "ok \\xff end"

    def test_stderr_invalid_bytes_are_preserved_not_dropped(self):
        code = "import sys; sys.stderr.buffer.write('오류 '.encode('utf-8') + b'\\xff')"
        r = ex.run_process(py(code))
        assert r.stderr == "오류 \\xff"

    def test_stdout_is_never_none(self):
        r = ex.run_process(py("pass"))
        assert r.stdout == "" and r.stderr == ""

    @pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
    def test_old_text_mode_would_fail_on_this_locale(self):
        """재현 기준: 로캘이 UTF-8이 아닐 때 기존 방식은 stdout이 None이 될 수 있다."""
        import locale
        if locale.getpreferredencoding(False).lower().replace("-", "") in ("utf8",):
            pytest.skip("로캘이 이미 UTF-8이라 기존 문제를 재현할 수 없다")
        code = f"import sys; sys.stdout.buffer.write({KOREAN!r}.encode('utf-8'))"
        old = subprocess.run(py(code), capture_output=True, text=True)
        # 로캘에 따라 None(디코딩 스레드 사망) 또는 깨진 문자열이 된다. 어느 쪽이든 원문과 다르다.
        assert old.stdout != KOREAN


# ---------------------------------------------------------------------------
# _run_git — 실제 git 저장소에서 한글 JSON 읽기
# ---------------------------------------------------------------------------

GIT = shutil.which("git")


@pytest.mark.skipif(GIT is None, reason="git이 필요하다")
class TestGitUtf8:
    def _repo_with_dep(self, tmp_project):
        def git(*args):
            subprocess.run(["git", *args], cwd=tmp_project, check=True, capture_output=True)
        git("init", "-q", "-b", "main")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "테스트")
        dep = tmp_project / "phases" / "0-base"
        dep.mkdir(parents=True, exist_ok=True)
        dep_index = {
            "project": "공무원을 위한 하네스 엔지니어링",
            "phase": "0-base",
            "steps": [{"step": 0, "name": "기반", "status": "completed", "summary": "한글 요약 ✓ ⚠"}],
        }
        (dep / "index.json").write_text(json.dumps(dep_index, ensure_ascii=False), encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "기반 phase")
        return dep_index

    def test_run_git_reads_korean_json(self, executor, tmp_project):
        dep_index = self._repo_with_dep(tmp_project)
        r = executor._run_git("show", "main:phases/0-base/index.json")
        assert r.returncode == 0
        assert json.loads(r.stdout) == dep_index

    def test_check_dependencies_with_korean_dependency_index(self, executor, tmp_project):
        self._repo_with_dep(tmp_project)
        top = {"phases": [
            {"dir": "0-base", "status": "completed"},
            {"dir": "0-mvp", "status": "pending", "depends_on": ["0-base"]},
        ]}
        p = tmp_project / "phases" / "index.json"
        p.write_text(json.dumps(top), encoding="utf-8")
        executor._top_index_file = p
        executor._check_dependencies()  # 예외 없이 통과해야 한다

    def test_changed_files_with_korean_path(self, executor, tmp_project):
        self._repo_with_dep(tmp_project)
        (tmp_project / "docs" / "한글문서.md").write_text("내용", encoding="utf-8")
        assert "docs/한글문서.md" in executor._changed_files()


# ---------------------------------------------------------------------------
# _check_dependencies — 원인을 알 수 있는 오류
# ---------------------------------------------------------------------------

class TestDependencyErrors:
    def _top(self, executor, tmp_project):
        top = {"phases": [
            {"dir": "0-base", "status": "completed"},
            {"dir": "0-mvp", "status": "pending", "depends_on": ["0-base"]},
        ]}
        p = tmp_project / "phases" / "index.json"
        p.write_text(json.dumps(top), encoding="utf-8")
        executor._top_index_file = p

    def test_none_stdout_gives_clear_message(self, executor, tmp_project, capsys):
        self._top(executor, tmp_project)
        executor._run_git = lambda *a: MagicMock(returncode=0, stdout=None, stderr="")
        with pytest.raises(SystemExit) as exc_info:
            executor._check_dependencies()
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        assert "0-base" in out and "비어" in out

    def test_invalid_json_gives_clear_message(self, executor, tmp_project, capsys):
        self._top(executor, tmp_project)
        executor._run_git = lambda *a: MagicMock(returncode=0, stdout="{깨진 json", stderr="")
        with pytest.raises(SystemExit) as exc_info:
            executor._check_dependencies()
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        assert "0-base" in out and "JSON" in out and "{깨진 json" in out

    def test_decode_error_gives_clear_message(self, executor, tmp_project, capsys):
        self._top(executor, tmp_project)

        def boom(*a):
            raise ex.SubprocessDecodeError("git show 출력을 UTF-8로 해석하지 못했습니다")
        executor._run_git = boom
        with pytest.raises(SystemExit) as exc_info:
            executor._check_dependencies()
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        assert "0-base" in out and "UTF-8" in out


# ---------------------------------------------------------------------------
# 콘솔 출력 — ✓ ⏸ ↻ 같은 기호가 cp949 콘솔·파이프에서 깨지지 않게
# ---------------------------------------------------------------------------

class TestConsole:
    def test_configure_console_switches_to_utf8(self):
        buf = io.BytesIO()
        stream = io.TextIOWrapper(buf, encoding="cp949")
        ex.configure_console(stream)
        stream.write("✓ ⏸ ↻ 한글")
        stream.flush()
        assert buf.getvalue().decode("utf-8") == "✓ ⏸ ↻ 한글"

    def test_configure_console_ignores_streams_without_reconfigure(self):
        ex.configure_console(io.StringIO())  # 예외 없이 지나가야 한다
