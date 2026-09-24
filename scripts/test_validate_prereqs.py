"""
Day 1 제작 전 보강 규칙 테스트.
- V-INS-001: draft·reviewed 교시의 강사 안내 존재
- step 단위 review_targets(--scope phase:<dir>:step<N>)와 kit:<id> 범위
- V-KIT-001: course.yaml kits 목록과 content/kits/<id>/kit.yaml 구조
- 키트 승인 상태(V-REV-001)와 해시(V-REV-002)
"""

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import content_hash as ch
import validate_course as vc
from test_validate_course import (  # noqa: F401 (도우미)
    course_with, lesson_mdx, rule, run, write_lesson, write_project,
)


# ---------------------------------------------------------------------------
# V-INS-001 강사 안내
# ---------------------------------------------------------------------------

class TestInstructorNotes:
    def test_draft_lesson_without_instructor_note_is_error(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0].update(status="draft")))
        write_lesson(tmp_path, instructor=False)
        found = rule(run(tmp_path), "V-INS-001", "error")
        assert found and "instructor/day1/01.md" in found[0].message

    def test_draft_lesson_with_instructor_note_passes(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0].update(status="draft")))
        write_lesson(tmp_path)
        assert not rule(run(tmp_path), "V-INS-001")

    def test_planned_lesson_needs_no_instructor_note(self, tmp_path):
        write_project(tmp_path)
        assert not rule(run(tmp_path), "V-INS-001")

    def test_scope_limits_instructor_check(self, tmp_path):
        write_project(tmp_path, course=course_with(lambda c: c["lessons"][0].update(status="draft")))
        write_lesson(tmp_path, instructor=False)
        assert not rule(run(tmp_path, scope="lesson:l2"), "V-INS-001")


# ---------------------------------------------------------------------------
# 키트 도우미
# ---------------------------------------------------------------------------

def kit_yaml(kid="day1-x", **over):
    data = {
        "id": kid, "title": "키트", "track": "core", "sources": ["law-resident"],
        "privacy_notes": "가상 자료만 쓴다", "fictional_label": "이 자료는 교육용 가상 자료입니다",
        "files": [{"path": "faq.md", "role": "context", "download": True}],
    }
    data.update(over)
    return data


def write_kit(root, kid="day1-x", files=None, data=None):
    d = root / "content" / "kits" / kid
    d.mkdir(parents=True, exist_ok=True)
    for rel, text in (files if files is not None else {"faq.md": "교육용 FAQ\r\n"}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (d / "kit.yaml").write_text(
        yaml.safe_dump(data if data is not None else kit_yaml(kid), allow_unicode=True, sort_keys=False),
        encoding="utf-8")
    return d


def with_kits(*entries):
    return course_with(lambda c: c.update(kits=list(entries)))


KIT_ENTRY = {"id": "day1-x", "title": "키트", "status": "planned"}


# ---------------------------------------------------------------------------
# V-KIT-001
# ---------------------------------------------------------------------------

class TestKits:
    def test_no_kits_is_fine(self, tmp_path):
        write_project(tmp_path)
        assert not rule(run(tmp_path), "V-KIT-001")

    def test_valid_kit_passes(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path)
        assert not rule(run(tmp_path), "V-KIT-001", "error")

    def test_course_kit_without_folder(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        found = rule(run(tmp_path), "V-KIT-001", "error")
        assert found and "kit.yaml" in found[0].message

    def test_kit_folder_without_course_entry(self, tmp_path):
        write_project(tmp_path)
        write_kit(tmp_path)
        found = rule(run(tmp_path), "V-KIT-001", "error")
        assert found and "day1-x" in found[0].message

    def test_kit_id_mismatch(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, data=kit_yaml("other"))
        assert rule(run(tmp_path), "V-KIT-001", "error")

    def test_missing_required_field(self, tmp_path):
        data = kit_yaml()
        del data["fictional_label"]
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, data=data)
        found = rule(run(tmp_path), "V-KIT-001", "error")
        assert found and "fictional_label" in found[0].message

    def test_unknown_source_id(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, data=kit_yaml(sources=["law-ghost"]))
        found = rule(run(tmp_path), "V-KIT-001", "error")
        assert found and "law-ghost" in found[0].message

    def test_listed_file_missing(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, files={}, data=kit_yaml())
        found = rule(run(tmp_path), "V-KIT-001", "error")
        assert found and "faq.md" in found[0].message

    def test_unlisted_file_in_kit(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, files={"faq.md": "a", "stray.md": "b"})
        found = rule(run(tmp_path), "V-KIT-001", "error")
        assert found and "stray.md" in found[0].message

    def test_invalid_role(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, data=kit_yaml(files=[{"path": "faq.md", "role": "misc"}]))
        assert rule(run(tmp_path), "V-KIT-001", "error")

    def test_path_escaping_kit_folder(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path, data=kit_yaml(files=[{"path": "../x.md", "role": "context"}]))
        assert rule(run(tmp_path), "V-KIT-001", "error")

    def test_invalid_kit_status(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY, status="done")))
        write_kit(tmp_path)
        assert rule(run(tmp_path), "V-KIT-001", "error")

    def test_duplicate_kit_id(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY), dict(KIT_ENTRY)))
        write_kit(tmp_path)
        assert rule(run(tmp_path), "V-KIT-001", "error")


# ---------------------------------------------------------------------------
# 키트 승인 상태와 해시
# ---------------------------------------------------------------------------

class TestKitReview:
    def test_kit_scope_requires_reviewed(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path)
        found = rule(run(tmp_path, scope="kit:day1-x", require_reviewed=True), "V-REV-001", "error")
        assert found and "day1-x" in found[0].message

    def test_unknown_kit_scope(self, tmp_path):
        write_project(tmp_path)
        assert rule(run(tmp_path, scope="kit:ghost"), "V-CLI-001", "error")

    def test_reviewed_kit_hash_matches(self, tmp_path):
        write_project(tmp_path)
        d = write_kit(tmp_path)
        digest = ch.content_hash(d)
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY, status="reviewed", reviewed_hash=digest)))
        found = run(tmp_path, scope="kit:day1-x", require_reviewed=True)
        assert not rule(found, "V-REV-001") and not rule(found, "V-REV-002")

    def test_reviewed_kit_modified_after_approval(self, tmp_path):
        write_project(tmp_path)
        d = write_kit(tmp_path)
        digest = ch.content_hash(d)
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY, status="reviewed", reviewed_hash=digest)))
        (d / "faq.md").write_text("바뀐 내용", encoding="utf-8")
        found = rule(run(tmp_path), "V-REV-002", "error")
        assert found and "day1-x" in found[0].message


# ---------------------------------------------------------------------------
# step 단위 review_targets
# ---------------------------------------------------------------------------

def write_phase_steps(root, name="2-test", steps=None, phase_targets=None):
    d = root / "phases" / name
    d.mkdir(parents=True, exist_ok=True)
    data = {"phase": "test", "steps": steps or []}
    if phase_targets is not None:
        data["review_targets"] = phase_targets
    (d / "index.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestStepScope:
    STEPS = [
        {"step": 0, "name": "kit", "status": "pending"},
        {"step": 1, "name": "human-review-a", "status": "pending", "review_targets": ["lesson:l1", "kit:day1-x"]},
        {"step": 2, "name": "human-review-b", "status": "pending", "review_targets": ["lesson:l2"]},
    ]

    def test_step_scope_checks_only_that_steps_targets(self, tmp_path):
        write_project(tmp_path, course=with_kits(dict(KIT_ENTRY)))
        write_kit(tmp_path)
        write_phase_steps(tmp_path, steps=self.STEPS)
        found = rule(run(tmp_path, scope="phase:2-test:step1", require_reviewed=True), "V-REV-001", "error")
        msgs = " ".join(f.message for f in found)
        assert "l1" in msgs and "day1-x" in msgs and "l2" not in msgs

    def test_later_step_targets_not_required_earlier(self, tmp_path):
        def m(c):
            c["lessons"][0]["status"] = "reviewed"
        course = course_with(m)
        write_project(tmp_path, course=course)
        write_lesson(tmp_path)
        l1 = course["lessons"][0]
        l1["reviewed_hash"] = ch.content_hash(tmp_path / "content" / "day1" / "01.mdx")
        write_project(tmp_path, course=course)
        write_phase_steps(tmp_path, steps=[dict(self.STEPS[0]), {"step": 1, "name": "hr", "status": "pending",
                                                                 "review_targets": ["lesson:l1"]}, dict(self.STEPS[2])])
        assert not rule(run(tmp_path, scope="phase:2-test:step1", require_reviewed=True), "V-REV-001")

    def test_step_without_review_targets(self, tmp_path):
        write_project(tmp_path)
        write_phase_steps(tmp_path, steps=self.STEPS)
        assert rule(run(tmp_path, scope="phase:2-test:step0"), "V-CLI-001", "error")

    def test_unknown_step(self, tmp_path):
        write_project(tmp_path)
        write_phase_steps(tmp_path, steps=self.STEPS)
        assert rule(run(tmp_path, scope="phase:2-test:step9"), "V-CLI-001", "error")

    def test_malformed_step_token(self, tmp_path):
        write_project(tmp_path)
        write_phase_steps(tmp_path, steps=self.STEPS)
        assert rule(run(tmp_path, scope="phase:2-test:first"), "V-CLI-001", "error")

    def test_unknown_kit_target(self, tmp_path):
        write_project(tmp_path)
        write_phase_steps(tmp_path, steps=[{"step": 0, "name": "hr", "status": "pending",
                                            "review_targets": ["kit:ghost"]}])
        assert rule(run(tmp_path, scope="phase:2-test:step0"), "V-CLI-001", "error")

    def test_phase_level_targets_still_work(self, tmp_path):
        write_project(tmp_path)
        write_phase_steps(tmp_path, steps=self.STEPS, phase_targets=["lesson:l2"])
        found = rule(run(tmp_path, scope="phase:2-test", require_reviewed=True), "V-REV-001", "error")
        assert found and all("l2" in f.message for f in found)
