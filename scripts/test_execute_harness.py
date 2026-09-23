"""
execute.py 교육자료 Harness 확장 기능 테스트.
guardrail_docs 선택 주입, depends_on, phase_summary, allowed_paths.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import execute as ex
from test_execute import tmp_project, phase_dir, top_index, executor  # noqa: F401 (pytest fixtures)


# ---------------------------------------------------------------------------
# guardrail_docs 선택 주입 (core 고정 + phase별 선택)
# ---------------------------------------------------------------------------

class TestGuardrailSelection:
    def _write_docs(self, tmp_project, names):
        for n in names:
            (tmp_project / "docs" / n).write_text(f"# {n} 내용", encoding="utf-8")

    def _set_guardrail_docs(self, executor, docs):
        idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
        idx["guardrail_docs"] = docs
        executor._index_file.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")

    def test_without_selection_loads_all_docs(self, executor, tmp_project):
        self._write_docs(tmp_project, ["PRD.md", "QUALITY.md"])
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "QUALITY.md 내용" in result
        assert "# Architecture" in result

    def test_selection_loads_core_plus_listed_only(self, executor, tmp_project):
        self._write_docs(tmp_project, ["PRD.md", "ADR.md", "QUALITY.md", "UI_GUIDE.md"])
        self._set_guardrail_docs(executor, ["QUALITY.md"])
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "PRD.md 내용" in result      # core
        assert "ADR.md 내용" in result      # core
        assert "QUALITY.md 내용" in result  # listed
        assert "UI_GUIDE.md 내용" not in result
        assert "# Guide" not in result      # guide.md: core도 아니고 선택도 안 됨

    def test_core_docs_always_included_even_if_not_listed(self, executor, tmp_project):
        self._write_docs(tmp_project, list(ex.StepExecutor.CORE_DOCS))
        self._set_guardrail_docs(executor, [])
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        for name in ex.StepExecutor.CORE_DOCS:
            assert f"{name} 내용" in result

    def test_listed_doc_missing_exits(self, executor, tmp_project):
        self._set_guardrail_docs(executor, ["NOPE.md"])
        with patch.object(ex, "ROOT", tmp_project):
            with pytest.raises(SystemExit) as exc_info:
                executor._load_guardrails()
        assert exc_info.value.code == 1

    def test_reads_korean_docs_as_utf8(self, executor, tmp_project):
        (tmp_project / "docs" / "PRD.md").write_text("# 공무원을 위한 하네스", encoding="utf-8")
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "공무원을 위한 하네스" in result


# ---------------------------------------------------------------------------
# depends_on — 선행 phase가 main에 병합·완료되었는지 확인
# ---------------------------------------------------------------------------

class TestCheckDependencies:
    def _top(self, executor, tmp_project, deps):
        top = {"phases": [
            {"dir": "0-base", "status": "completed"},
            {"dir": "0-mvp", "status": "pending", "depends_on": deps},
        ]}
        p = tmp_project / "phases" / "index.json"
        p.write_text(json.dumps(top), encoding="utf-8")
        executor._top_index_file = p

    def _git_show(self, responses):
        calls = []

        def fake_git(*args):
            calls.append(args)
            key = args[1] if args and args[0] == "show" else None
            return responses.get(key, MagicMock(returncode=128, stdout="", stderr="missing"))
        return fake_git, calls

    def test_no_depends_on_passes(self, executor, tmp_project):
        self._top(executor, tmp_project, [])
        executor._run_git = MagicMock()
        executor._check_dependencies()
        executor._run_git.assert_not_called()

    def test_dependency_merged_and_completed_passes(self, executor, tmp_project):
        self._top(executor, tmp_project, ["0-base"])
        dep_index = {"steps": [{"step": 0, "name": "a", "status": "completed"}]}
        fake, calls = self._git_show({
            "main:phases/0-base/index.json": MagicMock(returncode=0, stdout=json.dumps(dep_index), stderr=""),
        })
        executor._run_git = fake
        executor._check_dependencies()
        assert ("show", "main:phases/0-base/index.json") in calls

    def test_dependency_not_on_main_exits(self, executor, tmp_project):
        self._top(executor, tmp_project, ["0-base"])
        fake, _ = self._git_show({})
        executor._run_git = fake
        with pytest.raises(SystemExit) as exc_info:
            executor._check_dependencies()
        assert exc_info.value.code == 1

    def test_dependency_incomplete_on_main_exits(self, executor, tmp_project):
        self._top(executor, tmp_project, ["0-base"])
        dep_index = {"steps": [
            {"step": 0, "name": "a", "status": "completed"},
            {"step": 1, "name": "b", "status": "blocked"},
        ]}
        fake, _ = self._git_show({
            "main:phases/0-base/index.json": MagicMock(returncode=0, stdout=json.dumps(dep_index), stderr=""),
        })
        executor._run_git = fake
        with pytest.raises(SystemExit) as exc_info:
            executor._check_dependencies()
        assert exc_info.value.code == 1

    def test_no_top_index_passes(self, executor, tmp_path):
        executor._top_index_file = tmp_path / "none.json"
        executor._run_git = MagicMock()
        executor._check_dependencies()


class TestCheckoutFromBase:
    def test_new_branch_created_from_base_branch(self, executor):
        calls = []
        responses = iter([
            MagicMock(returncode=0, stdout="feat-0-foundation\n", stderr=""),  # 현재 브랜치
            MagicMock(returncode=1, stdout="", stderr="not found"),           # 대상 브랜치 없음
            MagicMock(returncode=0, stdout="", stderr=""),                    # checkout -b
        ])

        def fake_git(*args):
            calls.append(args)
            return next(responses)
        executor._run_git = fake_git
        executor._checkout_branch()
        assert calls[-1] == ("checkout", "-b", "feat-mvp", ex.StepExecutor.BASE_BRANCH)


# ---------------------------------------------------------------------------
# phase_summary — phase 간 맥락 전달
# ---------------------------------------------------------------------------

class TestPhaseSummary:
    def test_build_phase_summary_joins_step_summaries(self):
        index = {"steps": [
            {"step": 0, "name": "a", "status": "completed", "summary": "문서 작성"},
            {"step": 1, "name": "b", "status": "completed", "summary": "검증기 구현"},
        ]}
        result = ex.StepExecutor._build_phase_summary(index)
        assert "문서 작성" in result and "검증기 구현" in result

    def test_build_phase_summary_is_truncated(self):
        index = {"steps": [
            {"step": i, "name": "s", "status": "completed", "summary": "가" * 200} for i in range(10)
        ]}
        result = ex.StepExecutor._build_phase_summary(index)
        assert len(result) <= ex.StepExecutor.PHASE_SUMMARY_MAX

    def test_update_top_index_records_summary(self, executor, top_index):
        executor._top_index_file = top_index
        executor._update_top_index("completed", summary="요약입니다")
        data = json.loads(top_index.read_text(encoding="utf-8"))
        mvp = next(p for p in data["phases"] if p["dir"] == "0-mvp")
        assert mvp["summary"] == "요약입니다"

    def test_phase_context_lists_other_completed_phases(self, executor, tmp_project):
        top = {"phases": [
            {"dir": "0-foundation", "status": "completed", "summary": "docs와 검증기 완성"},
            {"dir": "1-web", "status": "pending"},
            {"dir": "0-mvp", "status": "pending"},
        ]}
        p = tmp_project / "phases" / "index.json"
        p.write_text(json.dumps(top, ensure_ascii=False), encoding="utf-8")
        executor._top_index_file = p
        result = executor._build_phase_context()
        assert result.startswith("## 이전 Phase 요약")
        assert "0-foundation: docs와 검증기 완성" in result
        assert "1-web" not in result

    def test_phase_context_empty_without_top_index(self, executor, tmp_path):
        executor._top_index_file = tmp_path / "none.json"
        assert executor._build_phase_context() == ""


# ---------------------------------------------------------------------------
# allowed_paths — step의 수정 허용 경로 검사
# ---------------------------------------------------------------------------

class TestAllowedPaths:
    def test_parse_porcelain_handles_untracked_and_rename(self):
        out = " M docs/PRD.md\n?? content/course.yaml\nR  old.md -> docs/new.md\n"
        assert ex.StepExecutor._parse_porcelain(out) == [
            "docs/PRD.md", "content/course.yaml", "docs/new.md",
        ]

    def test_no_allowed_paths_means_no_check(self, executor):
        assert executor._find_path_violations({"step": 2}, ["anything/at/all.txt"]) == []

    def test_violations_detected(self, executor):
        step = {"step": 2, "allowed_paths": ["docs/**", "content/course.yaml"]}
        changed = ["docs/PRD.md", "content/course.yaml", "src/pages/index.astro"]
        assert executor._find_path_violations(step, changed) == ["src/pages/index.astro"]

    def test_own_phase_dir_always_allowed(self, executor):
        step = {"step": 2, "allowed_paths": ["docs/**"]}
        changed = ["phases/0-mvp/index.json", "phases/0-mvp/step2-output.json"]
        assert executor._find_path_violations(step, changed) == []

    def test_changed_files_uses_untracked_all_and_no_quotepath(self, executor):
        calls = []

        def fake_git(*args):
            calls.append(args)
            return MagicMock(returncode=0, stdout="?? docs/한글.md\n", stderr="")
        executor._run_git = fake_git
        assert executor._changed_files() == ["docs/한글.md"]
        flat = " ".join(calls[0])
        assert "core.quotepath=false" in flat
        assert "--untracked-files=all" in flat

    def test_completed_step_with_violation_is_retried(self, executor):
        """허용 경로 밖 변경이 있으면 completed로 인정하지 않고 에러로 재시도한다."""
        idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
        idx["steps"][2]["allowed_paths"] = ["docs/**"]
        executor._index_file.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")

        def fake_invoke(step, preamble):
            data = json.loads(executor._index_file.read_text(encoding="utf-8"))
            data["steps"][2]["status"] = "completed"
            data["steps"][2]["summary"] = "done"
            executor._index_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return {}

        executor._invoke_claude = fake_invoke
        executor._changed_files = lambda: ["src/evil.ts"]
        executor._commit_step = MagicMock()
        executor._update_top_index = MagicMock()
        executor._top_index_file = executor._phases_dir / "none.json"

        with pytest.raises(SystemExit) as exc_info:
            executor._execute_single_step(idx["steps"][2], "")
        assert exc_info.value.code == 1
        final = json.loads(executor._index_file.read_text(encoding="utf-8"))
        assert final["steps"][2]["status"] == "error"
        assert "src/evil.ts" in final["steps"][2]["error_message"]
