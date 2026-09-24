"""review_approve.py 테스트 — 임시 폴더에서만 실행한다(실제 course.yaml에 쓰지 않는다)."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
import content_hash as ch
import review_approve as ra

COURSE = """\
# 머리 주석 — 보존되어야 한다
course:
  title: T   # 줄 끝 주석

cards:
  - {id: card-a, lesson: l1, title: 카드, category: C, level: 1, where: new-chat, track: core, status: draft}
  - {id: card-b, lesson: l2, title: 카드 B, category: C, level: 1, where: new-chat, track: core, status: planned, reviewed_hash: "sha256:old"}

lessons:
  # Day 1 묶음 주석
  - id: l1
    day: 1
    number: 1
    title: 첫 교시
    status: draft
    elements: [instructions, context]
    objectives:
      - {id: l1-o1, text: 목표, outputs: [l1-p1]}
  - id: l2
    day: 1
    number: 2
    status: planned   # 아직 안 씀
    reviewed_hash: "sha256:old"
    objectives: []
  - id: l3
    day: 2
    number: 1
    objectives: []
"""


def make_root(tmp_path, course=COURSE, newline="\n"):
    (tmp_path / "content").mkdir()
    (tmp_path / "content" / "course.yaml").write_bytes(course.replace("\n", newline).encode("utf-8"))
    return tmp_path


def add_file(root, rel, text="본문\n"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))
    return p


def course_text(root):
    return (root / "content" / "course.yaml").read_bytes().decode("utf-8")


def item(root, section, iid):
    data = yaml.safe_load(course_text(root))
    return next(x for x in data[section] if x["id"] == iid)


class TestApproveLesson:
    def test_sets_status_and_hash(self, tmp_path):
        root = make_root(tmp_path)
        mdx = add_file(root, "content/day1/01.mdx")
        assert ra.main(["l1", "--root", str(root)]) == 0
        les = item(root, "lessons", "l1")
        assert les["status"] == "reviewed"
        assert les["reviewed_hash"] == ch.content_hash(mdx)

    def test_only_target_lines_change(self, tmp_path):
        root = make_root(tmp_path)
        add_file(root, "content/day1/01.mdx")
        before = course_text(root).splitlines()
        ra.main(["l1", "--root", str(root)])
        after = course_text(root).splitlines()
        # status 줄이 바뀌고 reviewed_hash 줄 하나가 그 바로 뒤에 추가된다
        assert len(after) == len(before) + 1
        idx = before.index("    status: draft")
        assert after[idx] == "    status: reviewed"
        assert after[idx + 1].startswith('    reviewed_hash: "sha256:')
        assert after[:idx] == before[:idx]
        assert after[idx + 2:] == before[idx + 1:]

    def test_comments_and_inline_style_preserved(self, tmp_path):
        root = make_root(tmp_path)
        add_file(root, "content/day1/01.mdx")
        ra.main(["l1", "--root", str(root)])
        text = course_text(root)
        assert "# 머리 주석 — 보존되어야 한다" in text
        assert "title: T   # 줄 끝 주석" in text
        assert "  # Day 1 묶음 주석" in text
        assert "      - {id: l1-o1, text: 목표, outputs: [l1-p1]}" in text
        assert "    elements: [instructions, context]" in text

    def test_replaces_existing_hash_and_keeps_trailing_comment(self, tmp_path):
        root = make_root(tmp_path)
        mdx = add_file(root, "content/day1/02.mdx")
        before = course_text(root).splitlines()
        ra.main(["l2", "--root", str(root)])
        after = course_text(root).splitlines()
        assert len(after) == len(before)
        assert "    status: reviewed   # 아직 안 씀" in after
        assert f'    reviewed_hash: "{ch.content_hash(mdx)}"' in after
        assert item(root, "lessons", "l2")["reviewed_hash"] == ch.content_hash(mdx)

    def test_missing_status_line_is_error(self, tmp_path):
        root = make_root(tmp_path)
        add_file(root, "content/day2/01.mdx")
        before = course_text(root)
        assert ra.main(["l3", "--root", str(root)]) != 0
        assert course_text(root) == before

    def test_crlf_course_file_keeps_crlf(self, tmp_path):
        root = make_root(tmp_path, newline="\r\n")
        add_file(root, "content/day1/01.mdx")
        assert ra.main(["l1", "--root", str(root)]) == 0
        raw = (root / "content" / "course.yaml").read_bytes()
        assert b"\r\n" in raw and raw.count(b"\n") == raw.count(b"\r\n")
        assert item(root, "lessons", "l1")["status"] == "reviewed"


class TestApproveCard:
    def test_inline_card_gets_status_and_hash(self, tmp_path):
        root = make_root(tmp_path)
        md = add_file(root, "content/prompts/card-a.md")
        before = course_text(root).splitlines()
        assert ra.main(["card-a", "--root", str(root)]) == 0
        after = course_text(root).splitlines()
        assert len(after) == len(before)
        card = item(root, "cards", "card-a")
        assert card["status"] == "reviewed"
        assert card["reviewed_hash"] == ch.content_hash(md)
        line = next(x for x in after if "id: card-a," in x)
        assert line.startswith("  - {id: card-a, lesson: l1,") and line.endswith("}")

    def test_inline_card_existing_hash_replaced(self, tmp_path):
        root = make_root(tmp_path)
        md = add_file(root, "content/prompts/card-b.md")
        ra.main(["card-b", "--root", str(root)])
        card = item(root, "cards", "card-b")
        assert card["status"] == "reviewed" and card["reviewed_hash"] == ch.content_hash(md)
        assert course_text(root).count("reviewed_hash") == 2  # card-b 1개 + l2 1개


class TestErrors:
    def test_missing_content_file_is_error(self, tmp_path):
        root = make_root(tmp_path)
        before = course_text(root)
        assert ra.main(["l1", "--root", str(root)]) != 0
        assert course_text(root) == before

    def test_unknown_id_is_error(self, tmp_path):
        root = make_root(tmp_path)
        assert ra.main(["ghost", "--root", str(root)]) != 0

    def test_content_file_is_not_modified(self, tmp_path):
        root = make_root(tmp_path)
        mdx = add_file(root, "content/day1/01.mdx", "본문\r\n")
        raw = mdx.read_bytes()
        ra.main(["l1", "--root", str(root)])
        assert mdx.read_bytes() == raw


class TestOutput:
    def test_prints_one_line_transition(self, tmp_path, capsys):
        root = make_root(tmp_path)
        add_file(root, "content/day1/01.mdx")
        ra.main(["l1", "--root", str(root)])
        out = capsys.readouterr().out.strip().splitlines()
        assert len(out) == 1
        assert out[0].startswith("l1: draft → reviewed (sha256:")


class TestApproveText:
    """approve_text는 순수 함수: 텍스트를 받아 바뀐 텍스트를 돌려준다."""

    def test_raises_when_item_not_found(self):
        with pytest.raises(ra.ApproveError):
            ra.approve_text(COURSE, "lessons", "ghost", "sha256:x")

    def test_id_prefix_does_not_match_other_item(self):
        # l1을 찾을 때 l1-o1(목표) 줄을 건드리면 안 된다
        out = ra.approve_text(COURSE, "lessons", "l1", "sha256:x")
        assert "      - {id: l1-o1, text: 목표, outputs: [l1-p1]}" in out


KIT_COURSE = COURSE.replace("\nlessons:\n", """
kits:
  - id: day1-x
    title: 키트
    status: draft

lessons:
""")


class TestApproveKit:
    def test_approve_kit_records_folder_hash(self, tmp_path):
        root = make_root(tmp_path, KIT_COURSE)
        add_file(root, "content/kits/day1-x/kit.yaml", "id: day1-x\n")
        add_file(root, "content/kits/day1-x/faq.md", "교육용 FAQ\n")
        assert ra.main(["day1-x", "--root", str(root)]) == 0
        data = yaml.safe_load(course_text(root))
        kit = data["kits"][0]
        assert kit["status"] == "reviewed"
        assert kit["reviewed_hash"] == ch.content_hash(root / "content" / "kits" / "day1-x")
        assert "# 머리 주석 — 보존되어야 한다" in course_text(root)

    def test_approve_kit_without_folder_fails(self, tmp_path):
        root = make_root(tmp_path, KIT_COURSE)
        assert ra.main(["day1-x", "--root", str(root)]) == 1
