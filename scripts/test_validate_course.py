"""
validate_course.py 테스트.
유효한 최소 프로젝트를 만든 뒤, 규칙마다 하나씩 깨뜨려 해당 규칙 ID가 보고되는지 확인한다.
"""

import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
import validate_course as vc

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 최소 유효 프로젝트
# ---------------------------------------------------------------------------

def lesson(lid, day, number, elements, *, type_="practice", cards=None, stuck=None, used_by=None):
    return {
        "id": lid, "day": day, "number": number, "title": f"{lid} 제목", "type": type_,
        "subject": "S1", "track": "core", "status": "planned", "elements": elements,
        "activities": [
            {"kind": "demo", "name": "시연", "minutes": 10},
            {"kind": "practice", "name": "실습", "minutes": 20},
        ],
        "objectives": [{"id": f"{lid}-o1", "text": "목표", "outputs": [f"{lid}-p1"]}],
        "outputs": [{"id": f"{lid}-p1", "text": "산출물", "used_by": used_by or []}],
        "checks": ["결과 확인"],
        "cards": cards or [],
        "stuck_points": stuck if stuck is not None else [
            {"id": f"sp-{lid}", "text": "막힘", "supports": [4, 5]},
        ],
    }


ALL = ["instructions", "context", "tools", "evals", "guardrails", "observability"]

BASE_COURSE = {
    "course": {"title": "T", "edition": "test"},
    "constraints": {
        "total_hours": 4, "days": 2, "lessons_per_day": 2, "lesson_minutes": 50,
        "max_core_minutes": 40, "min_element_coverage": 2, "max_cards_per_lesson": 2,
        "max_core_cards": 14, "freshness_days": 90,
    },
    "elements": {k: k for k in ALL},
    "subjects": {"S1": "과목"},
    "supports": {i: f"지원{i}" for i in range(1, 10)},
    "activity_kinds": ["admin", "explain", "demo", "follow", "practice", "check", "reflect"],
    "completion": {"required_outputs": ["설계서"], "self_check": ["설명할 수 있다"]},
    "cards": [
        {"id": "card-a", "lesson": "l1", "title": "카드", "category": "C", "level": 1, "where": "new-chat", "track": "core"},
    ],
    "lessons": [
        lesson("l1", 1, 1, ALL, cards=["card-a"], stuck=[
            {"id": "sp-l1", "text": "막힘", "supports": [1, 4, 5], "card": "card-a"},
        ], used_by=["l2"]),
        lesson("l2", 1, 2, ALL),
        lesson("l3", 2, 1, ["tools"]),
        lesson("l4", 2, 2, ["evals"]),
    ],
    "modules": [{"id": "optional-codex", "title": "Codex", "track": "optional", "status": "planned"}],
}

QUALITY = """# QUALITY_CHECKLIST
| ID | 층 | 검사 내용 | 구현 |
|---|---|---|---|
{rows}
| H-01 | HUMAN | 법령 해석 정확성 | - |
"""

OPEN_QUESTIONS = """# OPEN_QUESTIONS
| ID | 질문 | 담당 | 막는 시점 | blocking | 상태 | 해결 |
|---|---|---|---|---|---|---|
| OQ-01 | 열린 질문 | 사용자 | Phase 1 | 예 | open | |
| OQ-02 | 닫힌 질문 | 사용자 | Phase 1 | 아니오 | closed | ADR-001 |
"""


def write_project(root: Path, course=None, product=None, sources=None, links=None):
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    for name in vc.REQUIRED_DOCS:
        (docs / name).write_text(f"# {name}\n", encoding="utf-8")
    rows = "\n".join(f"| {rid} | AUTO-오류 | 검사 | 구현 |" for rid in vc.implemented_rule_ids())
    (docs / "QUALITY_CHECKLIST.md").write_text(QUALITY.format(rows=rows), encoding="utf-8")
    (docs / "OPEN_QUESTIONS.md").write_text(OPEN_QUESTIONS, encoding="utf-8")
    (root / "CLAUDE.md").write_text("# 규칙\n", encoding="utf-8")
    content = root / "content"
    content.mkdir(exist_ok=True)
    dump = lambda name, data: (content / name).write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    dump("course.yaml", course if course is not None else copy.deepcopy(BASE_COURSE))
    dump("product-features.yaml", product if product is not None else {"features": [{
        "id": "chatgpt-projects", "product": "ChatGPT", "plan": "Plus", "name": "Projects",
        "status": "available", "verified_at": "2026-09-24", "verified_by": "web",
        "source": "https://help.openai.com/", "fallback": "일반 대화창에 지침 붙여넣기",
    }]})
    dump("sources.yaml", sources if sources is not None else {"sources": [{
        "id": "law-resident", "type": "law", "title": "주민등록법", "url": "https://www.law.go.kr/",
        "effective_date": "2026-01-01", "accessed_at": "2026-09-24", "articles": ["제16조"],
        "license": "공공저작물",
    }]})
    dump("external-links.yaml", links if links is not None else {"links": [{
        "id": "sheet-x", "title": "시트", "kind": "sheet-template", "owner": "강사",
        "url": None, "verified_at": None, "fallback": "xlsx", "status": "planned",
    }]})
    dump("glossary.yaml", {"terms": [{"id": "harness", "term": "하네스", "en": "Harness", "definition": "정의"}]})
    dump("banned-terms.yaml", {"terms": [{"pattern": "무료 계정", "scope": "content", "reason": "r", "replace": "x"}]})
    return root


def run(root, **kw):
    kw.setdefault("today", "2026-09-24")
    kw.setdefault("check_git", False)
    return vc.validate(root, **kw)


def ids(findings, level=None):
    return {f.rule for f in findings if level is None or f.level == level}


def course_with(mutate):
    c = copy.deepcopy(BASE_COURSE)
    mutate(c)
    return c


# ---------------------------------------------------------------------------
# 기본
# ---------------------------------------------------------------------------

class TestBaseline:
    def test_valid_project_has_no_errors(self, tmp_path):
        write_project(tmp_path)
        findings = run(tmp_path)
        assert ids(findings, "error") == set(), [str(f) for f in findings if f.level == "error"]

    def test_real_repository_passes(self):
        findings = vc.validate(ROOT, check_git=True)
        errors = [str(f) for f in findings if f.level == "error"]
        assert errors == []

    def test_every_rule_documented_in_registry(self):
        for rid in vc.implemented_rule_ids():
            assert rid in vc.RULES


class TestDocs:
    def test_missing_required_doc(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").unlink()
        assert "V-DOC-001" in ids(run(tmp_path), "error")

    def test_broken_relative_link(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "ADR.md").write_text("[없음](./NOPE.md) [웹](https://x.y) [앵커](#a)", encoding="utf-8")
        found = [f for f in run(tmp_path) if f.rule == "V-DOC-002"]
        assert len(found) == 1 and "NOPE.md" in found[0].message


class TestCourseStructure:
    def test_missing_course_yaml(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "content" / "course.yaml").unlink()
        assert "V-CRS-001" in ids(run(tmp_path), "error")

    def test_invalid_enum(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0].update(type="lecture")))
        assert "V-CRS-001" in ids(run(tmp_path), "error")

    def test_lesson_count_mismatch(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"].pop()))
        assert "V-CRS-002" in ids(run(tmp_path), "error")

    def test_total_hours_mismatch(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["constraints"].update(total_hours=5)))
        assert "V-CRS-002" in ids(run(tmp_path), "error")

    def test_duplicate_lesson_number(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][1].update(number=1)))
        assert "V-CRS-002" in ids(run(tmp_path), "error")

    def test_minutes_over_budget(self, tmp_path):
        def m(c):
            c["lessons"][0]["activities"].append({"kind": "practice", "name": "추가", "minutes": 15})
        write_project(tmp_path, course=course_with(m))
        assert "V-CRS-003" in ids(run(tmp_path), "error")

    def test_lesson_without_practice(self, tmp_path):
        def m(c):
            c["lessons"][0]["activities"] = [{"kind": "explain", "name": "설명", "minutes": 30}]
        write_project(tmp_path, course=course_with(m))
        assert "V-CRS-004" in ids(run(tmp_path), "error")

    def test_lesson_without_checks(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0].update(checks=[])))
        assert "V-CRS-004" in ids(run(tmp_path), "error")

    def test_objective_points_to_unknown_output(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["objectives"][0].update(outputs=["nope"])))
        assert "V-CRS-005" in ids(run(tmp_path), "error")

    def test_output_not_linked_to_objective(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["outputs"].append({"id": "l1-p9", "text": "고아", "used_by": []})))
        assert "V-CRS-005" in ids(run(tmp_path), "error")

    def test_used_by_unknown_lesson(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["outputs"][0].update(used_by=["ghost"])))
        assert "V-CRS-005" in ids(run(tmp_path), "error")

    def test_element_coverage(self, tmp_path):
        def m(c):
            for les in c["lessons"]:
                les["elements"] = [e for e in les["elements"] if e != "context"]
            c["lessons"][0]["elements"].append("context")
        write_project(tmp_path, course=course_with(m))
        found = [f for f in run(tmp_path) if f.rule == "V-CRS-006"]
        assert found and "context" in found[0].message

    def test_duplicate_ids(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][1].update(id="l1")))
        assert "V-CRS-007" in ids(run(tmp_path), "error")


class TestCards:
    def test_lesson_references_unknown_card(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][1].update(cards=["card-x"])))
        assert "V-CRS-008" in ids(run(tmp_path), "error")

    def test_card_not_backed_by_stuck_point(self, tmp_path):
        def m(c):
            c["cards"].append({"id": "card-b", "lesson": "l2", "title": "b", "category": "C",
                               "level": 1, "where": "new-chat", "track": "core"})
            c["lessons"][1]["cards"] = ["card-b"]
        write_project(tmp_path, course=course_with(m))
        found = [f for f in run(tmp_path) if f.rule == "V-CRS-008"]
        assert found and "card-b" in found[0].message

    def test_card_lesson_mismatch(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(lesson="l2")))
        assert "V-CRS-008" in ids(run(tmp_path), "error")

    def test_invalid_card_where(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(where="anywhere")))
        assert "V-CRS-008" in ids(run(tmp_path), "error")

    def test_invalid_card_status(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(status="done")))
        assert "V-CRS-008" in ids(run(tmp_path), "error")

    def test_core_lesson_uses_optional_card(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(track="optional")))
        assert "V-CRS-009" in ids(run(tmp_path), "error")

    def test_core_lesson_mentions_codex_in_objective(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["objectives"][0].update(text="Codex로 자동화한다")))
        assert "V-CRS-009" in ids(run(tmp_path), "error")

    def test_practice_lesson_needs_expected_and_wrong_examples(self, tmp_path):
        def m(c):
            c["lessons"][1]["stuck_points"] = [{"id": "sp-l2", "text": "막힘", "supports": [7]}]
        write_project(tmp_path, course=course_with(m))
        assert "V-CRS-010" in ids(run(tmp_path), "error")

    def test_too_many_cards_warns(self, tmp_path):
        def m(c):
            for i in range(3):
                cid = f"card-extra-{i}"
                c["cards"].append({"id": cid, "lesson": "l2", "title": "x", "category": "C",
                                   "level": 1, "where": "new-chat", "track": "core"})
                c["lessons"][1]["cards"].append(cid)
                c["lessons"][1]["stuck_points"].append({"id": f"sp-x{i}", "text": "t", "supports": [1], "card": cid})
        write_project(tmp_path, course=course_with(m))
        assert "V-CRS-011" in ids(run(tmp_path), "warn")

    def test_invalid_support_number(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["stuck_points"][0].update(supports=[10])))
        assert "V-CRS-001" in ids(run(tmp_path), "error")


class TestRegistries:
    def test_feature_missing_fallback(self, tmp_path):
        write_project(tmp_path, product={"features": [{
            "id": "f", "product": "ChatGPT", "plan": "Plus", "name": "n", "status": "available",
            "verified_at": "2026-09-24", "verified_by": "web", "source": "https://x",
        }]})
        assert "V-REG-001" in ids(run(tmp_path), "error")

    def test_feature_invalid_status(self, tmp_path):
        write_project(tmp_path, product={"features": [{
            "id": "f", "product": "ChatGPT", "plan": "Plus", "name": "n", "status": "maybe",
            "verified_at": "2026-09-24", "verified_by": "web", "source": "https://x", "fallback": "f",
        }]})
        assert "V-REG-001" in ids(run(tmp_path), "error")

    def test_unverified_feature_needs_tbd(self, tmp_path):
        write_project(tmp_path, product={"features": [{
            "id": "f", "product": "ChatGPT", "plan": "Plus", "name": "n", "status": "unverified",
            "verified_at": None, "verified_by": "hands-on", "source": None, "fallback": "f",
        }]})
        assert "V-REG-001" in ids(run(tmp_path), "error")

    def test_unverified_feature_with_oq_ok(self, tmp_path):
        write_project(tmp_path, product={"features": [{
            "id": "f", "product": "ChatGPT", "plan": "Plus", "name": "n", "status": "unverified",
            "verified_at": None, "verified_by": "hands-on", "source": None, "fallback": "f",
            "tbd": "[TBD: OQ-01]",
        }]})
        assert "V-REG-001" not in ids(run(tmp_path), "error")

    def test_law_needs_effective_date(self, tmp_path):
        write_project(tmp_path, sources={"sources": [{
            "id": "law-x", "type": "law", "title": "법", "url": "https://x", "accessed_at": "2026-09-24",
            "articles": ["제1조"], "license": "공공",
        }]})
        assert "V-REG-002" in ids(run(tmp_path), "error")

    def test_stale_source_warns(self, tmp_path):
        write_project(tmp_path, sources={"sources": [{
            "id": "doc", "type": "official-doc", "title": "d", "url": "https://x",
            "accessed_at": "2026-01-01", "license": "l",
        }]})
        assert "V-REG-003" in ids(run(tmp_path), "warn")

    def test_external_link_invalid_kind(self, tmp_path):
        write_project(tmp_path, links={"links": [{
            "id": "x", "title": "t", "kind": "video", "owner": "o", "url": None,
            "verified_at": None, "fallback": "f", "status": "planned",
        }]})
        assert "V-REG-004" in ids(run(tmp_path), "error")

    def test_active_external_link_needs_url(self, tmp_path):
        write_project(tmp_path, links={"links": [{
            "id": "x", "title": "t", "kind": "sheet-template", "owner": "o", "url": None,
            "verified_at": "2026-09-24", "fallback": "f", "status": "active",
        }]})
        assert "V-REG-004" in ids(run(tmp_path), "error")


class TestTagsAndText:
    def test_bare_tbd_is_error(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("요금은 [TBD] 이다", encoding="utf-8")
        assert "V-TAG-001" in ids(run(tmp_path), "error")

    def test_unknown_oq_is_error(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("요금은 [TBD: OQ-99] 이다", encoding="utf-8")
        assert "V-TAG-001" in ids(run(tmp_path), "error")

    def test_closed_oq_warns(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("요금은 [TBD: OQ-02] 이다", encoding="utf-8")
        assert "V-TAG-002" in ids(run(tmp_path), "warn")

    def test_tag_summary_counts(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("[PROVISIONAL] a [TBD: OQ-01] b [AS-OF: chatgpt-projects]", encoding="utf-8")
        info = [f for f in run(tmp_path) if f.rule == "V-TAG-003"]
        assert info and "PROVISIONAL 1" in info[0].message and "TBD 1" in info[0].message

    def test_tags_in_code_are_examples(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text(
            "형식은 `[TBD: OQ-xx]`와 `[AS-OF: feature-id]`\n```\n[TBD]\n```\n", encoding="utf-8")
        assert "V-TAG-001" not in ids(run(tmp_path))

    def test_tags_in_yaml_comments_are_examples(self, tmp_path):
        write_project(tmp_path)
        p = tmp_path / "content" / "glossary.yaml"
        p.write_text("# 본문은 [AS-OF: id] 태그로 참조\n" + p.read_text(encoding="utf-8"), encoding="utf-8")
        assert "V-TAG-001" not in ids(run(tmp_path))

    def test_real_tag_in_yaml_value_is_checked(self, tmp_path):
        write_project(tmp_path)
        p = tmp_path / "content" / "glossary.yaml"
        p.write_text(p.read_text(encoding="utf-8") + "note: \"[TBD: OQ-77]\"\n", encoding="utf-8")
        assert "V-TAG-001" in ids(run(tmp_path), "error")

    def test_as_of_unknown_feature(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("[AS-OF: no-such-feature]", encoding="utf-8")
        assert "V-TAG-001" in ids(run(tmp_path), "error")

    def test_real_phone_number_is_error(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("연락처 010-1234-5678", encoding="utf-8")
        assert "V-PII-001" in ids(run(tmp_path), "error")

    def test_fictional_phone_number_allowed(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("연락처 010-0000-1234", encoding="utf-8")
        assert "V-PII-001" not in ids(run(tmp_path))

    def test_resident_number_is_error(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "PRD.md").write_text("900101-1234567", encoding="utf-8")
        assert "V-PII-001" in ids(run(tmp_path), "error")

    def test_banned_term_in_content(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "content" / "day1").mkdir()
        (tmp_path / "content" / "day1" / "x.mdx").write_text("ChatGPT 무료 계정으로 시작", encoding="utf-8")
        assert "V-TXT-001" in ids(run(tmp_path), "error")

    def test_banned_term_in_docs_is_ignored(self, tmp_path):
        write_project(tmp_path)
        (tmp_path / "docs" / "CONTENT_GUIDE.md").write_text("'무료 계정' 표현 금지", encoding="utf-8")
        assert "V-TXT-001" not in ids(run(tmp_path))


class TestQualityLink:
    def test_implemented_rule_marked_as_planned(self, tmp_path):
        write_project(tmp_path)
        q = tmp_path / "docs" / "QUALITY_CHECKLIST.md"
        q.write_text(q.read_text(encoding="utf-8").replace(
            "| V-CRS-003 | AUTO-오류 | 검사 | 구현 |", "| V-CRS-003 | AUTO-오류 | 검사 | 예정(P1) |"), encoding="utf-8")
        assert "V-QUA-001" in ids(run(tmp_path), "error")

    def test_unknown_status_value(self, tmp_path):
        write_project(tmp_path)
        q = tmp_path / "docs" / "QUALITY_CHECKLIST.md"
        q.write_text(q.read_text(encoding="utf-8") + "| V-ODD-001 | AUTO-오류 | 이상한 값 | P0 |\n", encoding="utf-8")
        assert "V-QUA-001" in ids(run(tmp_path), "error")

    def test_implemented_rule_missing_from_checklist(self, tmp_path):
        write_project(tmp_path)
        q = tmp_path / "docs" / "QUALITY_CHECKLIST.md"
        q.write_text(q.read_text(encoding="utf-8").replace("| V-CRS-003 |", "| V-XXX-999 |"), encoding="utf-8")
        found = ids(run(tmp_path), "error")
        assert "V-QUA-001" in found

    def test_checklist_marked_implemented_but_missing(self, tmp_path):
        write_project(tmp_path)
        q = tmp_path / "docs" / "QUALITY_CHECKLIST.md"
        q.write_text(q.read_text(encoding="utf-8") + "| V-NEW-001 | AUTO-오류 | 미구현 | 구현 |\n", encoding="utf-8")
        assert "V-QUA-001" in ids(run(tmp_path), "error")

    def test_checklist_future_rule_is_fine(self, tmp_path):
        write_project(tmp_path)
        q = tmp_path / "docs" / "QUALITY_CHECKLIST.md"
        q.write_text(q.read_text(encoding="utf-8") + "| V-WEB-001 | AUTO-오류 | 링크 | 예정(P1) |\n", encoding="utf-8")
        assert "V-QUA-001" not in ids(run(tmp_path))


class TestModes:
    def test_require_reviewed_fails_on_planned(self, tmp_path):
        write_project(tmp_path)
        assert "V-REV-001" in ids(run(tmp_path, require_reviewed=True), "error")

    def test_require_reviewed_scope_lesson(self, tmp_path):
        def m(c):
            c["lessons"][0]["status"] = "reviewed"
        write_project(tmp_path, course=course_with(m))
        assert "V-REV-001" not in ids(run(tmp_path, require_reviewed=True, scope="lesson:l1"))
        assert "V-REV-001" in ids(run(tmp_path, require_reviewed=True, scope="lesson:l2"))

    def test_require_reviewed_does_not_need_hash_rule(self, tmp_path):
        # V-REV-001은 status만 본다(기존 동작 유지). 해시 검사는 V-REV-002가 따로 한다.
        def m(c):
            c["lessons"][0]["status"] = "reviewed"
        write_project(tmp_path, course=course_with(m))
        found = run(tmp_path, require_reviewed=True, scope="lesson:l1")
        assert "V-REV-001" not in ids(found)
        assert "V-REV-002" in ids(found, "error")

    def test_unknown_scope_is_error(self, tmp_path):
        write_project(tmp_path)
        assert "V-CLI-001" in ids(run(tmp_path, scope="lesson:ghost"), "error")

    def test_cli_exit_codes(self, tmp_path, monkeypatch):
        write_project(tmp_path)
        monkeypatch.setattr(vc, "ROOT", tmp_path)
        assert vc.main(["--docs-only", "--no-git", "--today", "2026-09-24"]) == 0
        (tmp_path / "docs" / "PRD.md").unlink()
        assert vc.main(["--docs-only", "--no-git", "--today", "2026-09-24"]) == 1

    def test_json_output(self, tmp_path, monkeypatch, capsys):
        write_project(tmp_path)
        monkeypatch.setattr(vc, "ROOT", tmp_path)
        vc.main(["--no-git", "--json", "--today", "2026-09-24"])
        data = json.loads(capsys.readouterr().out)
        assert "findings" in data and "summary" in data


class TestReviewHash:
    """V-REV-002: reviewed 항목의 콘텐츠 파일 해시가 reviewed_hash와 일치한다."""

    def _approved(self, tmp_path, text="본문\n"):
        mdx = tmp_path / "content" / "day1" / "01.mdx"
        md = tmp_path / "content" / "prompts" / "card-a.md"

        def m(c):
            c["lessons"][0].update(status="reviewed", reviewed_hash="sha256:placeholder")
            c["cards"][0].update(status="reviewed", reviewed_hash="sha256:placeholder")
        write_project(tmp_path, course=course_with(m))
        for p in (mdx, md):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(text.encode("utf-8"))
        course_path = tmp_path / "content" / "course.yaml"
        data = yaml.safe_load(course_path.read_text(encoding="utf-8"))
        data["lessons"][0]["reviewed_hash"] = vc.content_hash(mdx)
        data["cards"][0]["reviewed_hash"] = vc.content_hash(md)
        course_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return mdx, md

    def test_matching_hash_passes(self, tmp_path):
        self._approved(tmp_path)
        assert "V-REV-002" not in ids(run(tmp_path))

    def test_crlf_working_copy_matches_lf_hash(self, tmp_path):
        mdx, _ = self._approved(tmp_path, "첫 줄\n둘째 줄\n")
        mdx.write_bytes("첫 줄\r\n둘째 줄\r\n".encode("utf-8"))
        assert "V-REV-002" not in ids(run(tmp_path))

    def test_modified_lesson_after_approval_is_error(self, tmp_path):
        mdx, _ = self._approved(tmp_path)
        mdx.write_text("본문 수정\n", encoding="utf-8")
        found = [f for f in run(tmp_path) if f.rule == "V-REV-002"]
        assert len(found) == 1 and found[0].level == "error"
        assert "승인 후 수정됨" in found[0].message and "l1" in found[0].message

    def test_modified_card_after_approval_is_error(self, tmp_path):
        _, md = self._approved(tmp_path)
        md.write_text("카드 수정\n", encoding="utf-8")
        found = [f for f in run(tmp_path) if f.rule == "V-REV-002"]
        assert len(found) == 1 and "card-a" in found[0].message

    def test_missing_file_is_error(self, tmp_path):
        mdx, _ = self._approved(tmp_path)
        mdx.unlink()
        assert "V-REV-002" in ids(run(tmp_path), "error")

    def test_missing_hash_is_error(self, tmp_path):
        def m(c):
            c["cards"][0]["status"] = "reviewed"
        write_project(tmp_path, course=course_with(m))
        md = tmp_path / "content" / "prompts" / "card-a.md"
        md.parent.mkdir(parents=True)
        md.write_text("카드\n", encoding="utf-8")
        assert "V-REV-002" in ids(run(tmp_path), "error")

    def test_draft_items_are_not_checked(self, tmp_path):
        def m(c):
            c["lessons"][0].update(status="draft", reviewed_hash="sha256:stale")
        write_project(tmp_path, course=course_with(m))
        assert "V-REV-002" not in ids(run(tmp_path))

    def test_scope_limits_hash_check(self, tmp_path):
        mdx, _ = self._approved(tmp_path)
        mdx.write_text("본문 수정\n", encoding="utf-8")
        assert "V-REV-002" in ids(run(tmp_path, scope="lesson:l1"))
        assert "V-REV-002" not in ids(run(tmp_path, scope="lesson:l2"))
