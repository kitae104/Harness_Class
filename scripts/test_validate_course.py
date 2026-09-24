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
        q.write_text(q.read_text(encoding="utf-8") + "| V-KIT-001 | AUTO-오류 | 키트 | 예정(P2) |\n", encoding="utf-8")
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


# ---------------------------------------------------------------------------
# 교시·카드 파일 규칙 (V-LSN-*, V-PRM-*)
# ---------------------------------------------------------------------------

PRACTICE_SECTIONS = ("이번 시간에 할 일", "필수 경로", "실습", "예상 결과", "잘못된 결과 예시",
                     "Harness에서 무엇을 바꿨는가", "다음 교시 연결")


def lesson_mdx(lesson_id="l1", sections=PRACTICE_SECTIONS, body="짧은 문장입니다."):
    parts = [f"---\nlesson_id: {lesson_id}\n---\n", "import Callout from '../../src/components/Callout.astro';\n"]
    for s in sections:
        parts.append(f"## {s}\n\n{body}\n")
    return "\n".join(parts)


def write_lesson(root, rel="day1/01.mdx", text=None):
    p = root / "content" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text if text is not None else lesson_mdx(), encoding="utf-8")
    return p


CARD_FIELDS = {
    "id": "card-a", "stuck_point": "sp-l1", "where": "new-chat", "when": "막힐 때",
    "input": "내 지침", "l3_structure": "[역할] ...", "default_level": 1,
    "l2_template": "너는 [내 업무] 업무를 돕는다.\n모르면 \"확인 필요\"라고 쓴다.\n",
    "l1_full": "너는 민원 업무를 돕는다.\n모르면 \"확인 필요\"라고 쓴다.\n",
    "line_notes": [{"line": "역할", "element": "instructions", "why": "범위"}],
    "replace": ["[내 업무]"], "check": ["확인"], "do_not_trust": ["조문"], "next": "지침으로 옮긴다",
    "tested_at": "2026-09-20", "tested_by": "강사",
}

_DROP = object()


def write_card(root, cid="card-a", **override):
    data = dict(CARD_FIELDS, id=cid)
    for k, v in override.items():
        if v is _DROP:
            data.pop(k, None)
        else:
            data[k] = v
    p = root / "content" / "prompts" / f"{cid}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n", encoding="utf-8")
    return p


def rule(findings, rid, level=None):
    return [f for f in findings if f.rule == rid and (level is None or f.level == level)]


class TestLessonFiles:
    def test_valid_lesson_file_passes(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path)
        found = run(tmp_path)
        assert not rule(found, "V-LSN-001") and not rule(found, "V-LSN-002"), [str(f) for f in found]

    def test_lesson_id_mismatch(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx("l2"))
        found = rule(run(tmp_path), "V-LSN-001", "error")
        assert found and "l2" in found[0].message

    def test_missing_lesson_id(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text="## 이번 시간에 할 일\n")
        assert rule(run(tmp_path), "V-LSN-001", "error")

    def test_file_without_course_lesson(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, rel="day1/05.mdx", text=lesson_mdx("ghost"))
        found = rule(run(tmp_path), "V-LSN-001", "error")
        assert found and "05.mdx" in found[0].where

    def test_draft_lesson_without_file(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][1].update(status="draft")))
        found = rule(run(tmp_path), "V-LSN-001", "error")
        assert found and "l2" in found[0].message

    def test_planned_lesson_without_file_is_fine(self, tmp_path):
        write_project(tmp_path)
        assert not rule(run(tmp_path), "V-LSN-001")

    def test_missing_common_section(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx(sections=[s for s in PRACTICE_SECTIONS if s != "다음 교시 연결"]))
        found = rule(run(tmp_path), "V-LSN-002", "error")
        assert len(found) == 1 and "다음 교시 연결" in found[0].message

    def test_practice_needs_expected_and_wrong_sections(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx(sections=[s for s in PRACTICE_SECTIONS if "결과" not in s]))
        msgs = " ".join(f.message for f in rule(run(tmp_path), "V-LSN-002", "error"))
        assert "예상 결과" in msgs and "잘못된 결과 예시" in msgs

    def test_concept_lesson_does_not_need_result_sections(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0].update(type="concept")))
        write_lesson(tmp_path, text=lesson_mdx(sections=[s for s in PRACTICE_SECTIONS if "결과" not in s]))
        assert not rule(run(tmp_path), "V-LSN-002")

    def test_section_prefix_and_folded_summary_count(self, tmp_path):
        write_project(tmp_path)
        text = lesson_mdx(sections=[s for s in PRACTICE_SECTIONS if s not in ("실습", "잘못된 결과 예시")])
        text += "\n## 실습 — 기준 질문 기록하기\n\n<details>\n<summary>잘못된 결과 예시</summary>\n\n내용\n\n</details>\n"
        write_lesson(tmp_path, text=text)
        assert not rule(run(tmp_path), "V-LSN-002")

    def test_heading_inside_code_block_does_not_count(self, tmp_path):
        write_project(tmp_path)
        text = lesson_mdx(sections=[s for s in PRACTICE_SECTIONS if s != "필수 경로"]) + "\n```\n## 필수 경로\n```\n"
        write_lesson(tmp_path, text=text)
        assert rule(run(tmp_path), "V-LSN-002", "error")

    def test_scope_limits_lesson_rules(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx("l2"))
        assert rule(run(tmp_path, scope="lesson:l1"), "V-LSN-001")
        assert not rule(run(tmp_path, scope="lesson:l3"), "V-LSN-001")


class TestLessonStyle:
    def test_vague_objective_verb_warns(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["objectives"][0].update(text="하네스의 개념을 이해한다")))
        found = rule(run(tmp_path), "V-LSN-003", "warn")
        assert found and "l1-o1" in found[0].message

    @pytest.mark.parametrize("text", ["6요소를 안다", "도구를 알아본다."])
    def test_other_vague_verbs_warn(self, tmp_path, text):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0]["objectives"][0].update(text=text)))
        assert rule(run(tmp_path), "V-LSN-003", "warn")

    def test_observable_verb_is_fine(self, tmp_path):
        write_project(tmp_path, course=course_with(
            lambda c: c["lessons"][0]["objectives"][0].update(text="지침서 5항목을 작성한다")))
        assert not rule(run(tmp_path), "V-LSN-003")

    def test_long_sentence_warns(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx(body="가" * 121 + "입니다."))
        found = rule(run(tmp_path), "V-LSN-003", "warn")
        assert found and found[0].where.endswith("day1/01.mdx")

    def test_short_sentences_on_one_line_are_fine(self, tmp_path):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx(body=("가" * 60 + "입니다. ") * 3))
        assert not rule(run(tmp_path), "V-LSN-003")

    def test_long_text_in_code_and_tags_is_ignored(self, tmp_path):
        write_project(tmp_path)
        long = "가" * 130
        body = f"짧습니다.\n\n```\n{long}\n```\n\n<CopyButton text=\"{long}\" />\n"
        write_lesson(tmp_path, text=lesson_mdx(body=body))
        assert not rule(run(tmp_path), "V-LSN-003")


class TestProductInfoInLesson:
    @pytest.mark.parametrize("text", [
        "설정 > 데이터 제어에서 끕니다.",
        "파일 20개까지 올릴 수 있습니다.",
        "한 파일은 512 MB까지입니다.",
        "저장 공간은 10GB입니다.",
    ])
    def test_product_info_pattern_warns(self, tmp_path, text):
        write_project(tmp_path)
        write_lesson(tmp_path, text=lesson_mdx(body=text))
        found = rule(run(tmp_path), "V-LSN-004", "warn")
        assert found and found[0].where.endswith("day1/01.mdx")

    def test_code_blocks_tags_and_quotes_are_ignored(self, tmp_path):
        write_project(tmp_path)
        body = ("> 교육용 가상 자료입니다.\n\n```\n설정 > 데이터 제어\n파일 20개\n```\n\n"
                "<CopyButton text=\"파일 20개, 10 MB\" />\n<Feature id=\"chatgpt-projects\" />를 엽니다.\n")
        write_lesson(tmp_path, text=lesson_mdx(body=body))
        assert not rule(run(tmp_path), "V-LSN-004")


class TestPromptFiles:
    def test_valid_card_file_passes(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path)
        found = run(tmp_path)
        bad = [str(f) for f in found if f.rule.startswith("V-PRM")]
        assert bad == []

    def test_card_file_not_in_course(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, cid="card-ghost")
        found = rule(run(tmp_path), "V-PRM-001", "error")
        assert found and "card-ghost" in found[0].message

    def test_frontmatter_id_must_match_filename(self, tmp_path):
        write_project(tmp_path)
        p = write_card(tmp_path)
        p.write_text(p.read_text(encoding="utf-8").replace("id: card-a", "id: card-b"), encoding="utf-8")
        assert rule(run(tmp_path), "V-PRM-001", "error")

    def test_missing_required_field(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, replace=_DROP)
        assert rule(run(tmp_path), "V-PRM-001", "error")

    def test_stuck_point_must_back_the_card(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, stuck_point="sp-l2")
        found = rule(run(tmp_path), "V-PRM-001", "error")
        assert found and "sp-l2" in found[0].message

    def test_where_and_level_must_match_course(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, where="instructions", default_level=2)
        msgs = " ".join(f.message for f in rule(run(tmp_path), "V-PRM-001", "error"))
        assert "where" in msgs and "default_level" in msgs

    def test_bracket_missing_from_replace(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, l2_template="[내 업무]와 [내 자료]를 넣는다.")
        found = rule(run(tmp_path), "V-PRM-001", "error")
        assert found and "[내 자료]" in found[0].message

    def test_replace_entry_without_bracket_in_text(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, replace=["[내 업무]", "[안 쓰는 칸]"])
        found = rule(run(tmp_path), "V-PRM-001", "error")
        assert found and "[안 쓰는 칸]" in found[0].message

    def test_brackets_in_l3_structure_are_not_counted(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, l3_structure="[역할] [입력] [규칙] [출력 형식] [모를 때]")
        assert not rule(run(tmp_path), "V-PRM-001")

    def test_draft_card_without_file(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(status="draft")))
        found = rule(run(tmp_path), "V-PRM-001", "error")
        assert found and "card-a" in found[0].message

    def test_planned_card_without_file_is_fine(self, tmp_path):
        write_project(tmp_path)
        assert not rule(run(tmp_path), "V-PRM-001")

    def test_level3_card_needs_l2_template(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(level=3)))
        write_card(tmp_path, default_level=3, l2_template="  ", replace=[])
        assert rule(run(tmp_path), "V-PRM-002", "error")

    def test_level3_card_with_l2_template_is_fine(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["cards"][0].update(level=3)))
        write_card(tmp_path, default_level=3)
        assert not rule(run(tmp_path), "V-PRM-002")

    def test_untested_card_warns(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, tested_at=None)
        assert rule(run(tmp_path), "V-PRM-003", "warn")

    def test_stale_tested_at_warns(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, tested_at="2026-01-01")
        assert rule(run(tmp_path), "V-PRM-003", "warn")

    def test_scope_card(self, tmp_path):
        write_project(tmp_path)
        write_card(tmp_path, stuck_point="sp-l2")
        assert rule(run(tmp_path, scope="card:card-a"), "V-PRM-001")
        assert not rule(run(tmp_path, scope="lesson:l2"), "V-PRM-001")

    def test_unknown_card_scope_is_error(self, tmp_path):
        write_project(tmp_path)
        assert rule(run(tmp_path, scope="card:ghost"), "V-CLI-001", "error")


# ---------------------------------------------------------------------------
# 빌드 결과 규칙 (V-WEB-*)
# ---------------------------------------------------------------------------

def write_dist(root, files, name="dist"):
    base = root / name
    for rel, text in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return base


GOOD_DIST = {
    "index.html": '<a href="/course/">과정</a><a href="/course/day1/01/#top">교시</a>'
                  '<img src="/images/a.svg"><link rel="stylesheet" href="/_astro/a.css"><a href="https://x.y">밖</a>',
    "course/index.html": '<a href="/">홈</a>',
    "course/day1/01/index.html": '<a href="/course">과정</a>',
    "images/a.svg": "<svg/>",
    "_astro/a.css": "body{}",
}


class TestWebBuild:
    def test_missing_dist_is_info(self, tmp_path):
        write_project(tmp_path)
        found = run(tmp_path)
        assert rule(found, "V-WEB-001", "info") and not rule(found, "V-WEB-001", "error")

    def test_good_dist_passes(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, GOOD_DIST)
        found = run(tmp_path)
        assert not [f for f in found if f.rule.startswith("V-WEB") and f.level == "error"], [str(f) for f in found]

    def test_broken_internal_link(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, dict(GOOD_DIST, **{"course/index.html": '<a href="/course/day9/01/">x</a>'}))
        found = rule(run(tmp_path), "V-WEB-001", "error")
        assert found and "/course/day9/01/" in found[0].message

    def test_broken_image(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, dict(GOOD_DIST, **{"course/index.html": '<img src="/images/none.png">'}))
        assert rule(run(tmp_path), "V-WEB-001", "error")

    def test_docs_only_skips_web_rules(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, dict(GOOD_DIST, **{
            "course/index.html": '<script type="module" src="https://cdn.x/a.js"></script><a href="/nope/">x</a>'}))
        found = run(tmp_path, docs_only=True)
        assert not [f for f in found if f.rule.startswith("V-WEB")]

    @pytest.mark.parametrize("html", [
        '<script src="https://cdn.example.com/a.js"></script>',
        '<link rel="stylesheet" href="//fonts.example.com/a.css">',
        '<style>@font-face{font-family:x;src:url(https://fonts.example.com/a.woff2)}</style>',
        '<script type="module">console.log(1)</script>',
    ])
    def test_external_assets_and_module_scripts(self, tmp_path, html):
        write_project(tmp_path)
        write_dist(tmp_path, dict(GOOD_DIST, **{"course/index.html": html}))
        assert rule(run(tmp_path), "V-WEB-002", "error")

    def test_webfont_in_css_file(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, dict(GOOD_DIST, **{"_astro/a.css": "@font-face{src:url('http://f.x/a.woff')}"}))
        assert rule(run(tmp_path), "V-WEB-002", "error")

    def test_offline_bundle_needs_relative_links(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, GOOD_DIST)
        write_dist(tmp_path, {"index.html": '<a href="course/index.html">과정</a><a href="/course/">절대</a>'},
                   name="dist-offline")
        found = rule(run(tmp_path), "V-WEB-002", "error")
        assert found and "dist-offline" in found[0].where

    def test_offline_bundle_relative_links_pass(self, tmp_path):
        write_project(tmp_path)
        write_dist(tmp_path, GOOD_DIST)
        write_dist(tmp_path, {"index.html": '<a href="course/index.html">과정</a><a href="https://x.y">밖</a>'},
                   name="dist-offline")
        assert not rule(run(tmp_path), "V-WEB-002")


# ---------------------------------------------------------------------------
# phase 범위
# ---------------------------------------------------------------------------

def write_phase(root, name="1-test", targets=("lesson:l1", "card:card-a")):
    d = root / "phases" / name
    d.mkdir(parents=True, exist_ok=True)
    data = {"phase": "test", "steps": []}
    if targets is not None:
        data["review_targets"] = list(targets)
    (d / "index.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestPhaseScope:
    def test_phase_scope_requires_reviewed_targets_only(self, tmp_path):
        write_project(tmp_path)
        write_phase(tmp_path)
        found = rule(run(tmp_path, scope="phase:1-test", require_reviewed=True), "V-REV-001", "error")
        msgs = " ".join(f.message for f in found)
        assert "l1" in msgs and "card-a" in msgs and "l2" not in msgs

    def test_phase_scope_passes_when_targets_reviewed(self, tmp_path):
        def m(c):
            c["lessons"][0]["status"] = "reviewed"
            c["cards"][0]["status"] = "reviewed"
        write_project(tmp_path, course=course_with(m))
        write_phase(tmp_path)
        assert not rule(run(tmp_path, scope="phase:1-test", require_reviewed=True), "V-REV-001")

    def test_phase_scope_without_require_reviewed(self, tmp_path):
        write_project(tmp_path)
        write_phase(tmp_path)
        assert ids(run(tmp_path, scope="phase:1-test"), "error") == set()

    def test_phase_scope_limits_lesson_rules(self, tmp_path):
        write_project(tmp_path)
        write_phase(tmp_path, targets=["lesson:l2"])
        write_lesson(tmp_path, text=lesson_mdx("l2"))  # l1 자리의 파일인데 lesson_id 불일치
        assert not rule(run(tmp_path, scope="phase:1-test"), "V-LSN-001")

    def test_missing_phase_dir(self, tmp_path):
        write_project(tmp_path)
        assert rule(run(tmp_path, scope="phase:nope"), "V-CLI-001", "error")

    def test_phase_without_review_targets(self, tmp_path):
        write_project(tmp_path)
        write_phase(tmp_path, targets=None)
        assert rule(run(tmp_path, scope="phase:1-test"), "V-CLI-001", "error")

    def test_phase_with_unknown_target(self, tmp_path):
        write_project(tmp_path)
        write_phase(tmp_path, targets=["lesson:ghost"])
        assert rule(run(tmp_path, scope="phase:1-test"), "V-CLI-001", "error")

    def test_real_phase_scope(self):
        found = vc.validate(ROOT, scope="phase:1-web-foundation", check_git=False)
        assert [str(f) for f in found if f.level == "error"] == []
