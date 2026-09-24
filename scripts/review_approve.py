#!/usr/bin/env python3
"""
사람 승인 명령 (ADR-005, ADR-011, ARCHITECTURE 10절).

사람이 검토를 마친 교시·카드의 콘텐츠 파일 해시를 course.yaml의 reviewed_hash에 기록하고
status를 reviewed로 바꾼다. 콘텐츠 파일은 수정하지 않는다.
course.yaml은 통째로 다시 쓰지 않고 해당 항목의 줄만 텍스트로 고친다(주석·키 순서·인라인 형식 보존).

Usage:
    npm run review:approve <id>
    python scripts/review_approve.py <id> [--root .]
"""

import argparse
import copy
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_hash import content_hash, target_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = {"lessons": "lesson", "cards": "card"}


class ApproveError(Exception):
    pass


def _split_eol(line: str):
    body = line.rstrip("\r\n")
    return body, line[len(body):]


def _section_range(lines, section):
    head = re.compile(rf"^{re.escape(section)}:\s*(#.*)?$")
    start = next((i for i, ln in enumerate(lines) if head.match(_split_eol(ln)[0])), None)
    if start is None:
        raise ApproveError(f"course.yaml에서 '{section}:' 구역을 찾지 못했다")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        body = _split_eol(lines[j])[0]
        if body and not body[0].isspace() and not body.startswith("#"):
            end = j
            break
    return start + 1, end


def _edit_inline(body, item_id, digest):
    status_re = re.compile(r"([{,]\s*)status:\s*[^,}]+?(\s*[,}])")
    if not status_re.search(body):
        raise ApproveError(f"{item_id}: status 필드를 찾지 못했다")
    body = status_re.sub(r"\g<1>status: reviewed\g<2>", body, count=1)
    hash_re = re.compile(r"([{,]\s*)reviewed_hash:\s*(\"[^\"]*\"|'[^']*'|[^,}]+?)(\s*[,}])")
    if hash_re.search(body):
        return hash_re.sub(lambda m: f'{m.group(1)}reviewed_hash: "{digest}"{m.group(3)}', body, count=1)
    close = body.rfind("}")
    if close < 0:
        raise ApproveError(f"{item_id}: 인라인 항목의 닫는 괄호를 찾지 못했다")
    return body[:close].rstrip() + f', reviewed_hash: "{digest}"' + body[close:]


def _edit_block(lines, idx, end, field_indent, item_id, digest):
    pad = " " * field_indent
    item_indent = field_indent - 2
    block_end = end
    for j in range(idx + 1, end):
        body = _split_eol(lines[j])[0]
        stripped = body.lstrip()
        if stripped and not stripped.startswith("#") and len(body) - len(stripped) <= item_indent:
            block_end = j
            break
    status_re = re.compile(rf"^{pad}status:(\s*)[^\s#]+(.*)$")
    hash_re = re.compile(rf"^{pad}reviewed_hash:(\s*)(\"[^\"]*\"|'[^']*'|[^\s#]*)(.*)$")
    status_at = hash_at = None
    for j in range(idx + 1, block_end):
        body = _split_eol(lines[j])[0]
        if status_at is None and status_re.match(body):
            status_at = j
        elif hash_at is None and hash_re.match(body):
            hash_at = j
    if status_at is None:
        raise ApproveError(f"{item_id}: status 줄을 찾지 못했다")
    body, eol = _split_eol(lines[status_at])
    lines[status_at] = status_re.sub(lambda m: f"{pad}status:{m.group(1)}reviewed{m.group(2)}", body) + eol
    if hash_at is not None:
        body, heol = _split_eol(lines[hash_at])
        lines[hash_at] = hash_re.sub(lambda m: f'{pad}reviewed_hash:{m.group(1)}"{digest}"{m.group(3)}', body) + heol
    else:
        lines.insert(status_at + 1, f'{pad}reviewed_hash: "{digest}"' + (eol or "\n"))


def approve_text(text: str, section: str, item_id: str, digest: str) -> str:
    """course.yaml 텍스트에서 section 안의 item_id 항목만 reviewed + digest로 바꾼 텍스트를 돌려준다."""
    lines = text.splitlines(keepends=True)
    start, end = _section_range(lines, section)
    qid = rf"[\"']?{re.escape(item_id)}[\"']?"
    block_re = re.compile(rf"^(\s*-\s+)id:\s*{qid}\s*(#.*)?$")
    inline_re = re.compile(rf"^\s*-\s*\{{\s*id:\s*{qid}\s*[,}}]")
    for i in range(start, end):
        body, eol = _split_eol(lines[i])
        if inline_re.match(body):
            lines[i] = _edit_inline(body, item_id, digest) + eol
            break
        m = block_re.match(body)
        if m:
            _edit_block(lines, i, end, len(m.group(1)), item_id, digest)
            break
    else:
        raise ApproveError(f"course.yaml '{section}'에서 {item_id} 항목 줄을 찾지 못했다")
    new_text = "".join(lines)
    _check_only_target_changed(text, new_text, section, item_id, digest)
    return new_text


def _check_only_target_changed(old_text, new_text, section, item_id, digest):
    """텍스트 수정 결과를 yaml로 다시 읽어, 대상 항목의 두 필드 외에는 바뀌지 않았는지 확인한다."""
    try:
        old, new = yaml.safe_load(old_text), yaml.safe_load(new_text)
    except yaml.YAMLError as e:
        raise ApproveError(f"수정 후 course.yaml을 읽을 수 없다: {e}") from e
    expected = copy.deepcopy(old)
    for it in expected.get(section) or []:
        if it.get("id") == item_id:
            it["status"] = "reviewed"
            it["reviewed_hash"] = digest
    if new != expected:
        raise ApproveError(f"{item_id}: 줄 단위 수정 결과가 예상과 다르다(형식을 확인하라)")


def find_item(course: dict, item_id: str):
    for section, kind in SECTIONS.items():
        for it in course.get(section) or []:
            if it.get("id") == item_id:
                return section, kind, it
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="사람 검토 승인: course.yaml에 status reviewed와 reviewed_hash를 기록")
    parser.add_argument("id", help="교시 ID 또는 카드 ID")
    parser.add_argument("--root", default=str(ROOT), help="저장소 루트(기본: 이 스크립트의 상위 폴더)")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # cp949 콘솔에서 '—'·'→' 출력 때문에 죽지 않게
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")

    root = Path(args.root)
    course_path = root / "content" / "course.yaml"
    try:
        if not course_path.exists():
            raise ApproveError(f"course.yaml이 없다: {course_path}")
        text = course_path.read_bytes().decode("utf-8")
        found = find_item(yaml.safe_load(text) or {}, args.id)
        if found is None:
            raise ApproveError(f"course.yaml의 교시·카드에 없는 ID: {args.id}")
        section, kind, item = found
        path = target_file(root, kind, item)
        if not path.is_file():
            raise ApproveError(f"{args.id}: 콘텐츠 파일이 없다 — {path.relative_to(root).as_posix()}")
        digest = content_hash(path)
        new_text = approve_text(text, section, args.id, digest)
    except (ApproveError, ValueError, UnicodeDecodeError) as e:
        print(f"[review:approve] 오류: {e}", file=sys.stderr)
        return 1
    course_path.write_bytes(new_text.encode("utf-8"))
    print(f"{args.id}: {item.get('status', 'planned')} → reviewed ({digest[:19]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
