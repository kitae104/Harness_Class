"""content_hash.py 테스트 — 해시는 줄바꿈을 LF로 정규화한 뒤 계산한다(ADR-005)."""

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import content_hash as ch


def write_bytes(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


class TestNormalizedBytes:
    def test_crlf_becomes_lf(self, tmp_path):
        p = write_bytes(tmp_path / "a.mdx", "첫 줄\r\n둘째 줄\r\n".encode("utf-8"))
        assert ch.normalized_bytes(p) == "첫 줄\n둘째 줄\n".encode("utf-8")

    def test_lone_cr_becomes_lf(self, tmp_path):
        p = write_bytes(tmp_path / "a.mdx", b"a\rb\r\nc\n")
        assert ch.normalized_bytes(p) == b"a\nb\nc\n"

    def test_non_utf8_is_error(self, tmp_path):
        p = write_bytes(tmp_path / "a.mdx", "한글".encode("cp949"))
        with pytest.raises(UnicodeDecodeError):
            ch.normalized_bytes(p)


class TestContentHash:
    def test_crlf_and_lf_files_have_same_hash(self, tmp_path):
        text = "---\nlesson_id: d1-x\n---\n\n## 이번 시간에 할 일\n본문\n"
        lf = write_bytes(tmp_path / "lf.mdx", text.encode("utf-8"))
        crlf = write_bytes(tmp_path / "crlf.mdx", text.replace("\n", "\r\n").encode("utf-8"))
        assert ch.content_hash(lf) == ch.content_hash(crlf)

    def test_format_is_sha256_prefix_and_hex(self, tmp_path):
        p = write_bytes(tmp_path / "a.md", b"abc\n")
        assert ch.content_hash(p) == "sha256:" + hashlib.sha256(b"abc\n").hexdigest()

    def test_different_content_has_different_hash(self, tmp_path):
        a = write_bytes(tmp_path / "a.md", b"abc\n")
        b = write_bytes(tmp_path / "b.md", b"abd\n")
        assert ch.content_hash(a) != ch.content_hash(b)


class TestTargetFile:
    def test_lesson_path_uses_day_and_two_digit_number(self, tmp_path):
        item = {"id": "d1-x", "day": 1, "number": 3}
        assert ch.target_file(tmp_path, "lesson", item) == tmp_path / "content" / "day1" / "03.mdx"

    def test_lesson_number_ten_or_more(self, tmp_path):
        item = {"id": "d2-x", "day": 2, "number": 12}
        assert ch.target_file(tmp_path, "lesson", item) == tmp_path / "content" / "day2" / "12.mdx"

    def test_card_path_uses_id(self, tmp_path):
        assert ch.target_file(tmp_path, "card", {"id": "card-a"}) == tmp_path / "content" / "prompts" / "card-a.md"

    def test_unknown_kind_is_error(self, tmp_path):
        with pytest.raises(ValueError):
            ch.target_file(tmp_path, "module", {"id": "m"})


class TestDirectoryHash:
    def _kit(self, root, newline="\n", order=("a.md", "b/c.md")):
        texts = {"a.md": "첫 파일\n둘째 줄\n", "b/c.md": "하위 폴더\n"}
        for rel in order:
            write_bytes(root / rel, texts[rel].replace("\n", newline).encode("utf-8"))
        return root

    def test_crlf_and_lf_folders_have_same_hash(self, tmp_path):
        lf = self._kit(tmp_path / "lf")
        crlf = self._kit(tmp_path / "crlf", newline="\r\n")
        assert ch.content_hash(lf) == ch.content_hash(crlf)

    def test_creation_order_does_not_matter(self, tmp_path):
        a = self._kit(tmp_path / "a", order=("a.md", "b/c.md"))
        b = self._kit(tmp_path / "b", order=("b/c.md", "a.md"))
        assert ch.content_hash(a) == ch.content_hash(b)

    def test_rename_changes_hash(self, tmp_path):
        a = self._kit(tmp_path / "a")
        before = ch.content_hash(a)
        (a / "a.md").rename(a / "z.md")
        assert ch.content_hash(a) != before

    def test_binary_file_is_hashed_as_is(self, tmp_path):
        d = tmp_path / "k"
        write_bytes(d / "sheet.xlsx", b"PK\x03\x04\xff\xfe")
        assert ch.content_hash(d).startswith("sha256:")

    def test_kit_target_is_folder(self, tmp_path):
        assert ch.target_file(tmp_path, "kit", {"id": "day1-x"}) == tmp_path / "content" / "kits" / "day1-x"
