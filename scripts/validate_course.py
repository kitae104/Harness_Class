#!/usr/bin/env python3
"""
교육자료 Harness 검증기.

course.yaml(과정 구조의 단일 원천), 등록부 yaml, docs를 검사해
구조·추적성·출처·정보 상태·개인정보 규칙 위반을 찾는다.
규칙 ID와 설명은 docs/QUALITY_CHECKLIST.md와 1:1로 대응한다.

Usage:
    python scripts/validate_course.py                  # 전체 검사 (현재 단계에서 가능한 규칙)
    python scripts/validate_course.py --docs-only      # docs·yaml 수준 검사 (Phase 1 이전 AC)
    python scripts/validate_course.py --scope lesson:d1-context --require-reviewed
    python scripts/validate_course.py --json           # 기계 판독용 출력
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML이 필요합니다: pip install -r requirements-dev.txt")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DOCS = (
    "PRD.md", "ARCHITECTURE.md", "ADR.md", "UI_GUIDE.md", "COURSE_MAP.md",
    "LEARNING_OBJECTIVES.md", "HARNESS_ELEMENTS.md", "PRACTICE_CASES.md", "PRACTICE_DESIGN.md",
    "CONTENT_GUIDE.md", "PROMPT_GUIDE.md", "TOOL_GUIDE.md", "CODEX_GUIDE.md",
    "PRODUCT_FEATURES.md", "SOURCE_REGISTER.md", "QUALITY_CHECKLIST.md", "DEPLOYMENT.md",
    "OPEN_QUESTIONS.md",
)

ELEMENTS = ("instructions", "context", "tools", "evals", "guardrails", "observability")
LESSON_TYPES = ("concept", "practice", "project")
TRACKS = ("core", "optional")
STATUSES = ("planned", "draft", "reviewed")
CARD_WHERE = ("instructions", "project-chat", "new-chat", "temporary-chat")
CARD_CATEGORIES = tuple("ABCDEFGHI")
FEATURE_STATUS = ("available", "limited", "unavailable", "unverified")
FEATURE_VERIFIED_BY = ("web", "hands-on")
SOURCE_TYPES = ("law", "official-doc", "proposal", "user-decision", "fictional", "guideline")
LINK_KINDS = ("sheet-template", "form-template", "shared-form", "doc")
LINK_STATUS = ("planned", "active", "retired")
PRACTICE_KINDS = ("practice", "follow")
OPTIONAL_WORDS = re.compile(r"codex", re.I)

TAG_RE = re.compile(r"\[(PROVISIONAL|TBD|AS-OF)(?::\s*([^\]]*))?\]")
OQ_ROW_RE = re.compile(r"^\|\s*(OQ-\d+)\s*\|(.*)$")
QUALITY_ROW_RE = re.compile(r"^\|\s*(V-[A-Z]{3}-\d{3})\s*\|\s*([^|]+)\|\s*([^|]*)\|\s*([^|]*)\|")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PHONE_RE = re.compile(r"(?<!\d)01[016789]-?(\d{3,4})-?\d{4}(?!\d)")
RRN_RE = re.compile(r"(?<!\d)\d{6}-[1-4]\d{6}(?!\d)")


@dataclass
class Finding:
    rule: str
    level: str  # error | warn | info
    message: str
    where: str = ""

    def __str__(self):
        loc = f" ({self.where})" if self.where else ""
        return f"[{self.level.upper()}] {self.rule}: {self.message}{loc}"


# 규칙 등록부 — 여기 있는 ID는 모두 구현되어 있어야 하며 QUALITY_CHECKLIST.md에 P0로 적혀 있어야 한다.
RULES = {
    "V-DOC-001": "필수 docs 존재",
    "V-DOC-002": "docs와 CLAUDE.md의 상대 링크가 실제 파일을 가리킨다",
    "V-CRS-001": "course.yaml 스키마와 허용값",
    "V-CRS-002": "Day·교시 수와 총 시간이 constraints와 일치, 교시 번호 중복 없음",
    "V-CRS-003": "교시 핵심 활동 합계가 max_core_minutes 이하",
    "V-CRS-004": "모든 교시에 학습목표·산출물·결과 확인·실습 활동 존재",
    "V-CRS-005": "학습목표→산출물→다음 교시 추적성",
    "V-CRS-006": "6요소별 최소 교시 수(min_element_coverage)",
    "V-CRS-007": "교시·목표·산출물·막힘 지점·카드 ID 중복 없음",
    "V-CRS-008": "카드 무결성(존재·교시 일치·막힘 지점 근거·허용값)",
    "V-CRS-009": "core 교시가 optional(Codex) 카드나 내용에 의존하지 않음",
    "V-CRS-010": "실습형 교시에 예상 결과(4)와 잘못된 결과 예시(5) 지원이 있음",
    "V-CRS-011": "교시당 카드 수와 core 카드 총량 상한 (경고)",
    "V-REG-001": "제품 정보 등록부 필드·허용값·fallback·미확인 시 OQ",
    "V-REG-002": "출처 등록부 필드, 법령은 시행일·조문 필수",
    "V-REG-003": "제품 정보·출처 확인일 경과 (경고)",
    "V-REG-004": "외부 링크 등록부 필드·허용값, active는 URL·확인일 필수",
    "V-TAG-001": "정보 상태 태그 형식: TBD는 존재하는 OQ, AS-OF는 존재하는 기능 ID",
    "V-TAG-002": "닫힌 OQ를 가리키는 TBD (경고)",
    "V-TAG-003": "정보 상태 태그 집계 (정보)",
    "V-PII-001": "실제 형식의 전화번호·주민등록번호 금지(가상 번호 010-0000-XXXX 제외)",
    "V-TXT-001": "수강생 콘텐츠의 금지 표현",
    "V-SEC-001": "비공개 원본(references/)이 git에 추적되지 않음",
    "V-QUA-001": "QUALITY_CHECKLIST의 P0 규칙과 구현된 규칙이 일치",
    "V-REV-001": "--require-reviewed: 범위 안 항목이 모두 reviewed",
    "V-CLI-001": "--scope 대상이 존재",
}


def implemented_rule_ids():
    return sorted(RULES)


# ---------------------------------------------------------------------------
# 입출력 도우미
# ---------------------------------------------------------------------------

def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_date(value) -> Optional[dt.date]:
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def _text_files(root: Path):
    """태그·개인정보 검사 대상: CLAUDE.md, docs, content, deliverables의 텍스트 파일."""
    files = []
    if (root / "CLAUDE.md").exists():
        files.append(root / "CLAUDE.md")
    for sub in ("docs", "content", "deliverables"):
        base = root / sub
        if base.is_dir():
            files += [p for p in sorted(base.rglob("*")) if p.suffix in (".md", ".mdx", ".yaml", ".yml")]
    return files


def _rel(root: Path, p: Path) -> str:
    try:
        return p.relative_to(root).as_posix()
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# 규칙: docs
# ---------------------------------------------------------------------------

def check_docs(root, out):
    docs = root / "docs"
    for name in REQUIRED_DOCS:
        if not (docs / name).exists():
            out.append(Finding("V-DOC-001", "error", f"필수 문서가 없다: docs/{name}"))
    md_files = [root / "CLAUDE.md"] + (sorted(docs.glob("*.md")) if docs.is_dir() else [])
    for md in md_files:
        if not md.exists():
            continue
        for target in MD_LINK_RE.findall(md.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            resolved = (root / path.lstrip("/")) if path.startswith("/") else (md.parent / path)
            if not resolved.exists():
                out.append(Finding("V-DOC-002", "error", f"깨진 링크: {target}", _rel(root, md)))


# ---------------------------------------------------------------------------
# 규칙: course.yaml
# ---------------------------------------------------------------------------

def _require(obj, keys, where, out):
    ok = True
    for k in keys:
        if k not in obj or obj[k] in (None, ""):
            out.append(Finding("V-CRS-001", "error", f"필수 필드 누락: {k}", where))
            ok = False
    return ok


def _enum(value, allowed, field, where, out):
    if value not in allowed:
        out.append(Finding("V-CRS-001", "error", f"{field} 값 '{value}'은 허용값 {list(allowed)}이 아니다", where))


def check_course(root, out, scope_lessons=None):
    path = root / "content" / "course.yaml"
    if not path.exists():
        out.append(Finding("V-CRS-001", "error", "content/course.yaml이 없다"))
        return None
    course = _load_yaml(path)
    if not _require(course, ("course", "constraints", "subjects", "supports", "cards", "lessons", "completion"),
                    "course.yaml", out):
        return course

    cons = course["constraints"]
    _require(cons, ("total_hours", "days", "lessons_per_day", "lesson_minutes", "max_core_minutes",
                    "min_element_coverage", "max_cards_per_lesson", "max_core_cards", "freshness_days"),
             "constraints", out)
    subjects = set(course["subjects"])
    supports = {int(k) for k in course["supports"]}
    kinds = set(course.get("activity_kinds") or [])
    lessons = course["lessons"] or []
    cards = course["cards"] or []
    lesson_ids = [les.get("id") for les in lessons]
    lesson_set = set(lesson_ids)

    # V-CRS-001 스키마
    for les in lessons:
        w = f"lesson {les.get('id')}"
        if not _require(les, ("id", "day", "number", "title", "type", "subject", "track", "status",
                              "activities", "objectives", "outputs", "checks", "stuck_points"), w, out):
            continue
        _enum(les["type"], LESSON_TYPES, "type", w, out)
        _enum(les["track"], TRACKS, "track", w, out)
        _enum(les["status"], STATUSES, "status", w, out)
        _enum(les["subject"], subjects, "subject", w, out)
        for e in les.get("elements") or []:
            _enum(e, ELEMENTS, "elements", w, out)
        for a in les["activities"]:
            _enum(a.get("kind"), kinds, "activities.kind", w, out)
            if not isinstance(a.get("minutes"), int) or a["minutes"] <= 0:
                out.append(Finding("V-CRS-001", "error", f"활동 '{a.get('name')}'의 minutes가 양의 정수가 아니다", w))
        for sp in les["stuck_points"]:
            for s in sp.get("supports") or []:
                if s not in supports:
                    out.append(Finding("V-CRS-001", "error", f"막힘 지점 {sp.get('id')}의 지원 방식 {s}은 1~9가 아니다", w))
    for c in cards:
        w = f"card {c.get('id')}"
        if _require(c, ("id", "lesson", "title", "category", "level", "where", "track"), w, out):
            pass

    # V-CRS-002 교시 수·시간·번호
    expected = cons.get("days", 0) * cons.get("lessons_per_day", 0)
    core_lessons = [les for les in lessons if les.get("track") == "core"]
    if len(core_lessons) != expected:
        out.append(Finding("V-CRS-002", "error", f"core 교시 수 {len(core_lessons)} ≠ days×lessons_per_day {expected}"))
    if cons.get("total_hours") != expected:
        out.append(Finding("V-CRS-002", "error", f"total_hours {cons.get('total_hours')} ≠ 교시 수 {expected}(교시당 1시간)"))
    for day in range(1, cons.get("days", 0) + 1):
        nums = sorted(les.get("number") for les in core_lessons if les.get("day") == day)
        want = list(range(1, cons.get("lessons_per_day", 0) + 1))
        if nums != want:
            out.append(Finding("V-CRS-002", "error", f"Day {day} 교시 번호 {nums} ≠ {want}"))

    # V-CRS-007 ID 중복
    seen = {}
    def _id(kind, value, where):
        if value in seen:
            out.append(Finding("V-CRS-007", "error", f"ID 중복: {value} ({seen[value]}, {kind})", where))
        else:
            seen[value] = kind
    for les in lessons:
        _id("lesson", les.get("id"), "")
        for o in les.get("objectives") or []:
            _id("objective", o.get("id"), les.get("id"))
        for o in les.get("outputs") or []:
            _id("output", o.get("id"), les.get("id"))
        for sp in les.get("stuck_points") or []:
            _id("stuck_point", sp.get("id"), les.get("id"))
    for c in cards:
        _id("card", c.get("id"), "cards")
    for m in course.get("modules") or []:
        _id("module", m.get("id"), "modules")

    card_by_id = {c.get("id"): c for c in cards}
    card_backing = {}  # card id -> stuck point ids
    for les in lessons:
        for sp in les.get("stuck_points") or []:
            if sp.get("card"):
                card_backing.setdefault(sp["card"], []).append(sp.get("id"))

    for les in lessons:
        lid = les.get("id")
        if scope_lessons is not None and lid not in scope_lessons:
            continue
        w = f"lesson {lid}"
        acts = les.get("activities") or []
        total = sum(a.get("minutes") or 0 for a in acts)
        # V-CRS-003
        if total > cons.get("max_core_minutes", 0):
            out.append(Finding("V-CRS-003", "error",
                               f"핵심 활동 {total}분 > 상한 {cons.get('max_core_minutes')}분", w))
        # V-CRS-004
        if not les.get("objectives"):
            out.append(Finding("V-CRS-004", "error", "학습목표가 없다", w))
        if not les.get("outputs"):
            out.append(Finding("V-CRS-004", "error", "산출물이 없다", w))
        if not les.get("checks"):
            out.append(Finding("V-CRS-004", "error", "결과 확인 항목이 없다", w))
        if not any(a.get("kind") in PRACTICE_KINDS for a in acts):
            out.append(Finding("V-CRS-004", "error", "실습(practice/follow) 활동이 없다", w))
        # V-CRS-005 추적성
        output_ids = {o.get("id") for o in les.get("outputs") or []}
        linked = set()
        for o in les.get("objectives") or []:
            refs = o.get("outputs") or []
            if not refs:
                out.append(Finding("V-CRS-005", "error", f"학습목표 {o.get('id')}가 산출물을 가리키지 않는다", w))
            for r in refs:
                if r not in output_ids:
                    out.append(Finding("V-CRS-005", "error", f"학습목표 {o.get('id')}가 없는 산출물 {r}을 가리킨다", w))
                linked.add(r)
        for oid in output_ids - linked:
            out.append(Finding("V-CRS-005", "error", f"산출물 {oid}가 어떤 학습목표와도 연결되지 않는다", w))
        for o in les.get("outputs") or []:
            for u in o.get("used_by") or []:
                if u not in lesson_set:
                    out.append(Finding("V-CRS-005", "error", f"산출물 {o.get('id')}의 used_by '{u}'는 없는 교시다", w))
        # V-CRS-008 카드 (교시 쪽)
        for cid in les.get("cards") or []:
            c = card_by_id.get(cid)
            if c is None:
                out.append(Finding("V-CRS-008", "error", f"없는 카드 {cid}를 참조한다", w))
            elif c.get("lesson") != lid:
                out.append(Finding("V-CRS-008", "error", f"카드 {cid}의 lesson은 '{c.get('lesson')}'인데 {lid}에 배치됐다", w))
        for sp in les.get("stuck_points") or []:
            if sp.get("card") and sp["card"] not in card_by_id:
                out.append(Finding("V-CRS-008", "error", f"막힘 지점 {sp.get('id')}가 없는 카드 {sp['card']}를 가리킨다", w))
        # V-CRS-009 core → optional 의존
        if les.get("track") == "core":
            for cid in les.get("cards") or []:
                if card_by_id.get(cid, {}).get("track") == "optional":
                    out.append(Finding("V-CRS-009", "error", f"core 교시가 optional 카드 {cid}를 사용한다", w))
            texts = [o.get("text", "") for o in les.get("objectives") or []]
            texts += [o.get("text", "") for o in les.get("outputs") or []]
            texts += [a.get("name", "") for a in acts]
            if any(OPTIONAL_WORDS.search(t) for t in texts):
                out.append(Finding("V-CRS-009", "error", "core 교시의 목표·산출물·활동에 Codex가 등장한다", w))
        # V-CRS-010 실습형 ④⑤
        if les.get("type") == "practice":
            used = {s for sp in les.get("stuck_points") or [] for s in sp.get("supports") or []}
            for need, label in ((4, "예상 결과"), (5, "잘못된 결과 예시")):
                if need not in used:
                    out.append(Finding("V-CRS-010", "error", f"실습형 교시에 {label}({need}) 지원이 없다", w))
        # V-CRS-011 카드 수
        if len(les.get("cards") or []) > cons.get("max_cards_per_lesson", 99):
            out.append(Finding("V-CRS-011", "warn",
                               f"교시 카드 {len(les['cards'])}장 > 권장 {cons.get('max_cards_per_lesson')}장", w))

    # V-CRS-008 카드 (카드 쪽)
    for c in cards:
        cid = c.get("id")
        w = f"card {cid}"
        if c.get("lesson") != "common" and c.get("lesson") not in lesson_set:
            out.append(Finding("V-CRS-008", "error", f"카드 lesson '{c.get('lesson')}'은 없는 교시다", w))
        if c.get("where") not in CARD_WHERE:
            out.append(Finding("V-CRS-008", "error", f"where '{c.get('where')}'은 허용값 {list(CARD_WHERE)}이 아니다", w))
        if c.get("category") not in CARD_CATEGORIES:
            out.append(Finding("V-CRS-008", "error", f"category '{c.get('category')}'은 A~I가 아니다", w))
        if c.get("level") not in (1, 2, 3):
            out.append(Finding("V-CRS-008", "error", f"level '{c.get('level')}'은 1~3이 아니다", w))
        if c.get("track") not in TRACKS:
            out.append(Finding("V-CRS-008", "error", f"track '{c.get('track')}'이 허용값이 아니다", w))
        if cid not in card_backing:
            out.append(Finding("V-CRS-008", "error", f"카드 {cid}를 근거로 삼는 막힘 지점(stuck_points.card)이 없다", w))
    core_cards = [c for c in cards if c.get("track") == "core"]
    if len(core_cards) > cons.get("max_core_cards", 999):
        out.append(Finding("V-CRS-011", "warn", f"core 카드 {len(core_cards)}장 > 상한 {cons.get('max_core_cards')}장"))

    # V-CRS-006 6요소 커버리지 (core 교시 기준)
    need = cons.get("min_element_coverage", 0)
    for e in ELEMENTS:
        n = sum(1 for les in core_lessons if e in (les.get("elements") or []))
        if n < need:
            out.append(Finding("V-CRS-006", "error", f"요소 {e}를 다루는 교시가 {n}개 < {need}개"))
    return course


# ---------------------------------------------------------------------------
# 규칙: 등록부
# ---------------------------------------------------------------------------

def _stale(value, today, days):
    d = _parse_date(value)
    return d is not None and (today - d).days > days


def check_registries(root, out, today, freshness, feature_ids):
    content = root / "content"
    pf = content / "product-features.yaml"
    if pf.exists():
        for f in _load_yaml(pf).get("features") or []:
            w = f"feature {f.get('id')}"
            for k in ("id", "product", "plan", "name", "status", "verified_by", "fallback"):
                if not f.get(k):
                    out.append(Finding("V-REG-001", "error", f"필수 필드 누락: {k}", w))
            if f.get("status") not in FEATURE_STATUS:
                out.append(Finding("V-REG-001", "error", f"status '{f.get('status')}'은 허용값 {list(FEATURE_STATUS)}이 아니다", w))
            if f.get("verified_by") not in FEATURE_VERIFIED_BY:
                out.append(Finding("V-REG-001", "error", f"verified_by '{f.get('verified_by')}'이 허용값이 아니다", w))
            if f.get("status") == "unverified":
                if not re.search(r"\[TBD: OQ-\d+\]", str(f.get("tbd", ""))):
                    out.append(Finding("V-REG-001", "error", "미확인(unverified) 기능은 tbd 필드에 [TBD: OQ-xx]가 필요하다", w))
            else:
                if not _parse_date(f.get("verified_at")) or not f.get("source"):
                    out.append(Finding("V-REG-001", "error", "확인된 기능은 verified_at(날짜)과 source가 필요하다", w))
                elif _stale(f.get("verified_at"), today, freshness):
                    out.append(Finding("V-REG-003", "warn", f"확인일 {f.get('verified_at')}이 {freshness}일을 넘었다", w))
    src = content / "sources.yaml"
    if src.exists():
        for s in _load_yaml(src).get("sources") or []:
            w = f"source {s.get('id')}"
            for k in ("id", "type", "title", "accessed_at", "license"):
                if not s.get(k):
                    out.append(Finding("V-REG-002", "error", f"필수 필드 누락: {k}", w))
            if s.get("type") not in SOURCE_TYPES:
                out.append(Finding("V-REG-002", "error", f"type '{s.get('type')}'은 허용값 {list(SOURCE_TYPES)}이 아니다", w))
            if s.get("type") == "law":
                if not _parse_date(s.get("effective_date")):
                    out.append(Finding("V-REG-002", "error", "법령은 effective_date(시행일)가 필요하다", w))
                if not s.get("articles"):
                    out.append(Finding("V-REG-002", "error", "법령은 인용 조문 목록(articles)이 필요하다", w))
            if s.get("type") not in ("proposal", "user-decision", "fictional") and not s.get("url"):
                out.append(Finding("V-REG-002", "error", "공개 출처는 url이 필요하다", w))
            if _stale(s.get("accessed_at"), today, freshness):
                out.append(Finding("V-REG-003", "warn", f"접근일 {s.get('accessed_at')}이 {freshness}일을 넘었다", w))
    links = content / "external-links.yaml"
    if links.exists():
        for ln in _load_yaml(links).get("links") or []:
            w = f"link {ln.get('id')}"
            for k in ("id", "title", "kind", "owner", "fallback", "status"):
                if not ln.get(k):
                    out.append(Finding("V-REG-004", "error", f"필수 필드 누락: {k}", w))
            if ln.get("kind") not in LINK_KINDS:
                out.append(Finding("V-REG-004", "error", f"kind '{ln.get('kind')}'은 허용값 {list(LINK_KINDS)}이 아니다", w))
            if ln.get("status") not in LINK_STATUS:
                out.append(Finding("V-REG-004", "error", f"status '{ln.get('status')}'이 허용값이 아니다", w))
            if ln.get("status") == "active" and (not ln.get("url") or not _parse_date(ln.get("verified_at"))):
                out.append(Finding("V-REG-004", "error", "active 링크는 url과 verified_at이 필요하다", w))
            elif ln.get("status") == "active" and _stale(ln.get("verified_at"), today, freshness):
                out.append(Finding("V-REG-003", "warn", f"링크 확인일 {ln.get('verified_at')}이 오래되었다", w))


def feature_ids(root):
    pf = root / "content" / "product-features.yaml"
    return {f.get("id") for f in (_load_yaml(pf).get("features") or [])} if pf.exists() else set()


# ---------------------------------------------------------------------------
# 규칙: 태그·개인정보·금지 표현
# ---------------------------------------------------------------------------

def open_questions(root):
    path = root / "docs" / "OPEN_QUESTIONS.md"
    result = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        m = OQ_ROW_RE.match(line)
        if m:
            cols = [c.strip() for c in m.group(2).split("|")]
            status = cols[4].lower() if len(cols) > 4 else ""
            result[m.group(1)] = "closed" if ("closed" in status or "해결" in status) else "open"
    return result


FENCE_RE = re.compile(r"^```.*?^```", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
YAML_COMMENT_RE = re.compile(r"^\s*#.*$", re.M)


def _strip_examples(text: str, suffix: str) -> str:
    """태그 형식을 설명하는 예시(코드 블록, 인라인 코드, yaml 주석)는 검사에서 뺀다."""
    if suffix in (".yaml", ".yml"):
        return YAML_COMMENT_RE.sub("", text)
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def check_tags_and_text(root, out, features):
    oqs = open_questions(root)
    counts = {"PROVISIONAL": 0, "TBD": 0, "AS-OF": 0}
    for p in _text_files(root):
        text = p.read_text(encoding="utf-8")
        where = _rel(root, p)
        for m in TAG_RE.finditer(_strip_examples(text, p.suffix)):
            kind, arg = m.group(1), (m.group(2) or "").strip()
            counts[kind] += 1
            if kind == "TBD":
                ref = re.fullmatch(r"OQ-\d+", arg)
                if not ref:
                    out.append(Finding("V-TAG-001", "error", f"TBD 태그는 [TBD: OQ-xx] 형식이어야 한다: {m.group(0)}", where))
                elif arg not in oqs:
                    out.append(Finding("V-TAG-001", "error", f"{arg}가 OPEN_QUESTIONS에 없다", where))
                elif oqs[arg] == "closed":
                    out.append(Finding("V-TAG-002", "warn", f"닫힌 {arg}를 가리키는 TBD가 남아 있다", where))
            elif kind == "AS-OF":
                if not arg or arg not in features:
                    out.append(Finding("V-TAG-001", "error", f"AS-OF 태그의 기능 ID '{arg}'가 product-features에 없다", where))
        for m in PHONE_RE.finditer(text):
            if m.group(1) != "0000":
                out.append(Finding("V-PII-001", "error", f"실제 형식의 전화번호: {m.group(0)} (가상 번호는 010-0000-XXXX)", where))
        for m in RRN_RE.finditer(text):
            out.append(Finding("V-PII-001", "error", f"주민등록번호 형식: {m.group(0)[:7]}*******", where))
    out.append(Finding("V-TAG-003", "info",
                       f"정보 상태 태그: PROVISIONAL {counts['PROVISIONAL']}, TBD {counts['TBD']}, AS-OF {counts['AS-OF']}"))

    banned_path = root / "content" / "banned-terms.yaml"
    if banned_path.exists():
        banned = _load_yaml(banned_path).get("terms") or []
        targets = []
        for sub in ("content", "deliverables"):
            base = root / sub
            if base.is_dir():
                targets += [p for p in base.rglob("*") if p.suffix in (".md", ".mdx")]
        for p in targets:
            text = p.read_text(encoding="utf-8")
            for t in banned:
                if re.search(t["pattern"], text):
                    out.append(Finding("V-TXT-001", "error",
                                       f"금지 표현 '{t['pattern']}': {t.get('reason')} → {t.get('replace')}", _rel(root, p)))


def check_git_tracking(root, out):
    r = subprocess.run(["git", "ls-files", "references"], cwd=root, capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0 and r.stdout.strip():
        out.append(Finding("V-SEC-001", "error", "비공개 원본이 git에 추적되고 있다: " + r.stdout.strip().replace("\n", ", ")))


def check_quality_link(root, out):
    path = root / "docs" / "QUALITY_CHECKLIST.md"
    if not path.exists():
        return
    listed = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = QUALITY_ROW_RE.match(line)
        if m:
            listed[m.group(1)] = m.group(4).strip()
    for rid in RULES:
        if rid not in listed:
            out.append(Finding("V-QUA-001", "error", f"구현된 규칙 {rid}가 QUALITY_CHECKLIST에 없다"))
        elif listed[rid] != "P0":
            out.append(Finding("V-QUA-001", "error", f"구현된 규칙 {rid}의 구현 시점이 P0가 아니다({listed[rid]})"))
    for rid, when in listed.items():
        if when == "P0" and rid not in RULES:
            out.append(Finding("V-QUA-001", "error", f"QUALITY_CHECKLIST의 P0 규칙 {rid}가 구현되지 않았다"))


def check_reviewed(course, out, scope_lessons):
    if course is None:
        return
    items = [("lesson", les) for les in course.get("lessons") or []]
    if scope_lessons is None:
        items += [("card", c) for c in course.get("cards") or []]
    for kind, it in items:
        if scope_lessons is not None and it.get("id") not in scope_lessons:
            continue
        if kind == "lesson" and it.get("track") != "core" and scope_lessons is None:
            continue
        if it.get("status", "planned") != "reviewed":
            out.append(Finding("V-REV-001", "error", f"{kind} {it.get('id')}의 status가 reviewed가 아니다({it.get('status', 'planned')})"))


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------

def _resolve_scope(root, scope):
    """scope 문자열 → 교시 ID 집합(None = 전체). 오류 시 (None, 메시지)."""
    if not scope or scope == "all":
        return None, None
    kind, _, target = scope.partition(":")
    course_path = root / "content" / "course.yaml"
    lessons = _load_yaml(course_path).get("lessons") or [] if course_path.exists() else []
    if kind == "lesson":
        if target not in {les.get("id") for les in lessons}:
            return set(), f"없는 교시: {target}"
        return {target}, None
    if kind == "day":
        found = {les.get("id") for les in lessons if str(les.get("day")) == target}
        return (found, None) if found else (set(), f"없는 Day: {target}")
    if kind == "phase":
        return None, None  # phase 범위는 콘텐츠 phase가 생기면 phases/<id>/index.json으로 확장한다
    return set(), f"알 수 없는 scope 형식: {scope} (lesson:<id> | day:<n> | phase:<id> | all)"


def validate(root: Path, *, docs_only=False, scope=None, require_reviewed=False,
             today=None, check_git=True):
    out = []
    today = _parse_date(today) or dt.date.today()
    scope_lessons, scope_err = _resolve_scope(root, scope)
    if scope_err:
        out.append(Finding("V-CLI-001", "error", scope_err))
        return out
    check_docs(root, out)
    course = check_course(root, out, scope_lessons)
    freshness = ((course or {}).get("constraints") or {}).get("freshness_days", 90)
    features = feature_ids(root)
    check_registries(root, out, today, freshness, features)
    check_tags_and_text(root, out, features)
    check_quality_link(root, out)
    if check_git:
        check_git_tracking(root, out)
    if require_reviewed:
        check_reviewed(course, out, scope_lessons)
    # docs_only: 현재 모든 규칙이 docs·yaml 수준이다. 웹 빌드 검사(V-WEB-*)는 Phase 1에서 추가하며 docs_only일 때 건너뛴다.
    return out



def main(argv=None):
    parser = argparse.ArgumentParser(description="교육자료 Harness 검증기")
    parser.add_argument("--docs-only", action="store_true", help="docs·yaml 수준 규칙만 검사 (Phase 1 이전 AC)")
    parser.add_argument("--scope", default=None, help="lesson:<id> | day:<n> | phase:<id> | all")
    parser.add_argument("--require-reviewed", action="store_true", help="범위 안 항목이 모두 reviewed인지 검사")
    parser.add_argument("--production", action="store_true", help="Production 관문: --require-reviewed 포함")
    parser.add_argument("--pre-launch", action="store_true", help="개설 전 점검: 확인일 경과 경고를 오류로 격상")
    parser.add_argument("--no-git", action="store_true", help="git 추적 검사 생략")
    parser.add_argument("--today", default=None, help="기준일(YYYY-MM-DD), 테스트용")
    parser.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = parser.parse_args(argv)

    findings = validate(
        ROOT, docs_only=args.docs_only, scope=args.scope,
        require_reviewed=args.require_reviewed or args.production,
        today=args.today, check_git=not args.no_git,
    )
    if args.pre_launch:
        for f in findings:
            if f.rule == "V-REG-003":
                f.level = "error"

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]
    infos = [f for f in findings if f.level == "info"]
    if args.json:
        print(json.dumps({
            "summary": {"errors": len(errors), "warnings": len(warns), "rules": len(RULES)},
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        for f in errors + warns + infos:
            print(str(f))
        print(f"\n검사 규칙 {len(RULES)}개 · 오류 {len(errors)} · 경고 {len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
