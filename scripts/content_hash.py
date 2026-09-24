"""
콘텐츠 파일 해시 (ADR-005, ARCHITECTURE 10절).

파일을 UTF-8로 읽고 줄바꿈(CRLF·CR)을 LF로 바꾼 뒤 SHA-256을 계산한다.
Windows 작업 폴더(CRLF)와 CI(LF)에서 같은 값이 나와야 승인이 깨지지 않는다.
review_approve.py(기록)와 validate_course.py V-REV-002(대조)가 같이 쓴다.
"""

import hashlib
from pathlib import Path


def normalized_bytes(path: Path) -> bytes:
    """UTF-8로 읽고 CRLF·CR을 LF로 바꾼 바이트. UTF-8이 아니면 UnicodeDecodeError."""
    text = Path(path).read_bytes().decode("utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _file_bytes(path: Path) -> bytes:
    """텍스트(UTF-8)는 줄바꿈을 정규화하고, 바이너리(xlsx 등)는 그대로 쓴다."""
    try:
        return normalized_bytes(path)
    except UnicodeDecodeError:
        return Path(path).read_bytes()


def content_hash(path: Path) -> str:
    """'sha256:<hex>' 형식의 해시.

    파일이면 그 파일(UTF-8, 줄바꿈 정규화)의 해시다. 폴더(키트)이면 하위 파일을 상대 경로 순으로 정렬해
    "상대 경로 + 내용"을 이어 해시한다. 파일 생성 순서·OS 줄바꿈과 무관하고, 이름 변경·추가·삭제는 해시를 바꾼다.
    """
    path = Path(path)
    if not path.is_dir():
        return "sha256:" + hashlib.sha256(normalized_bytes(path)).hexdigest()
    digest = hashlib.sha256()
    for f in sorted((q for q in path.rglob("*") if q.is_file()), key=lambda q: q.relative_to(path).as_posix()):
        data = _file_bytes(f)
        digest.update(f.relative_to(path).as_posix().encode("utf-8") + b"\0")
        digest.update(str(len(data)).encode("ascii") + b"\0" + data)
    return "sha256:" + digest.hexdigest()


def target_file(root: Path, kind: str, item: dict) -> Path:
    """course.yaml 항목의 콘텐츠 경로. kind는 'lesson'·'card'(파일) 또는 'kit'(폴더)."""
    root = Path(root)
    if kind == "lesson":
        return root / "content" / f"day{int(item['day'])}" / f"{int(item['number']):02d}.mdx"
    if kind == "card":
        return root / "content" / "prompts" / f"{item['id']}.md"
    if kind == "kit":
        return root / "content" / "kits" / str(item["id"])
    raise ValueError(f"알 수 없는 종류: {kind} (lesson | card | kit)")
