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


def content_hash(path: Path) -> str:
    """'sha256:<hex>' 형식의 해시."""
    return "sha256:" + hashlib.sha256(normalized_bytes(path)).hexdigest()


def target_file(root: Path, kind: str, item: dict) -> Path:
    """course.yaml 항목의 콘텐츠 파일 경로. kind는 'lesson' 또는 'card'."""
    root = Path(root)
    if kind == "lesson":
        return root / "content" / f"day{int(item['day'])}" / f"{int(item['number']):02d}.mdx"
    if kind == "card":
        return root / "content" / "prompts" / f"{item['id']}.md"
    raise ValueError(f"알 수 없는 종류: {kind} (lesson | card)")
