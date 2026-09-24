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
    python scripts/validate_course.py --scope phase:1-web-foundation --require-reviewed  # review_targets만
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_hash import content_hash, target_file  # noqa: E402

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


# 규칙 등록부 — 여기 있는 ID는 모두 구현되어 있어야 하며 QUALITY_CHECKLIST.md의 구현 열이 '구현'이어야 한다.
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
    "V-QUA-001": "QUALITY_CHECKLIST의 구현 열(구현/예정)과 실제 구현된 규칙이 일치",
    "V-REV-001": "--require-reviewed: 범위 안 항목이 모두 reviewed",
    "V-REV-002": "reviewed 항목의 콘텐츠 파일 해시(LF 정규화)가 course.yaml의 reviewed_hash와 일치",
    "V-CLI-001": "--scope 대상이 존재",
    "V-LSN-001": "교시 MDX의 lesson_id가 같은 위치의 course.yaml 교시와 일치, draft·reviewed 교시는 파일 존재",
    "V-LSN-002": "교시 MDX에 공통 필수 섹션과 유형별 필수 섹션(실습형: 예상 결과·잘못된 결과 예시) 존재",
    "V-LSN-003": "학습목표 동사(이해한다·안다·알아본다)와 본문 문장 길이 (경고)",
    "V-LSN-004": "교시 본문에 제품 정보(메뉴 경로·파일 개수·용량)를 직접 쓴 흔적 (경고)",
    "V-PRM-001": "카드 파일이 course.yaml 카드와 1:1, 교차 필드 일치, 대괄호↔replace 일치, draft·reviewed 카드는 파일 존재",
    "V-PRM-002": "직접 쓰기(level 3) 카드에 바꿔 쓰기(l2_template) 대안 존재",
    "V-PRM-003": "카드 tested_at 없음 또는 경과 (경고)",
    "V-WEB-001": "dist/ HTML의 내부 링크·이미지 경로가 실제 파일을 가리킴",
    "V-WEB-002": "빌드 산출물에 외부 script·stylesheet·웹폰트와 모듈 스크립트가 없고, 오프라인 번들 링크는 상대경로",
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
        if c.get("status", "planned") not in STATUSES:
            out.append(Finding("V-CRS-008", "error", f"status '{c.get('status')}'은 허용값 {list(STATUSES)}이 아니다", w))
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
    for rid, state in listed.items():
        if state != "구현" and not re.fullmatch(r"예정\(P\d+[a-z]?\)", state):
            out.append(Finding("V-QUA-001", "error", f"규칙 {rid}의 구현 열 '{state}'은 '구현' 또는 '예정(Pn)'이 아니다"))
    for rid in RULES:
        if rid not in listed:
            out.append(Finding("V-QUA-001", "error", f"구현된 규칙 {rid}가 QUALITY_CHECKLIST에 없다"))
        elif listed[rid] != "구현":
            out.append(Finding("V-QUA-001", "error", f"구현된 규칙 {rid}가 '{listed[rid]}'로 표시되어 있다('구현'이어야 함)"))
    for rid, state in listed.items():
        if state == "구현" and rid not in RULES:
            out.append(Finding("V-QUA-001", "error", f"QUALITY_CHECKLIST에서 '구현'인 규칙 {rid}가 구현되지 않았다"))


def check_reviewed(course, out, scope_lessons, scope_cards=None):
    if course is None:
        return
    items = [("lesson", les) for les in course.get("lessons") or []]
    items += [("card", c) for c in course.get("cards") or []
              if scope_lessons is None or c.get("id") in (scope_cards or ())]
    for kind, it in items:
        if kind == "lesson" and scope_lessons is not None and it.get("id") not in scope_lessons:
            continue
        if kind == "lesson" and it.get("track") != "core" and scope_lessons is None:
            continue
        if it.get("status", "planned") != "reviewed":
            out.append(Finding("V-REV-001", "error", f"{kind} {it.get('id')}의 status가 reviewed가 아니다({it.get('status', 'planned')})"))


def _card_in_scope(card, scope_lessons, scope_cards):
    """범위 안 카드: 전체 범위, 범위 교시에 속한 카드, card:<id>로 지정한 카드."""
    return (scope_lessons is None or card.get("lesson") in scope_lessons
            or card.get("id") in (scope_cards or ()))


def check_review_hashes(root, course, out, scope_lessons, scope_cards=None):
    """V-REV-002: reviewed 교시·카드의 콘텐츠 파일이 승인 이후 바뀌지 않았는지 해시로 대조한다."""
    if course is None:
        return
    items = [("lesson", les) for les in course.get("lessons") or []
             if scope_lessons is None or les.get("id") in scope_lessons]
    items += [("card", c) for c in course.get("cards") or []
              if _card_in_scope(c, scope_lessons, scope_cards)]
    for kind, it in items:
        if it.get("status") != "reviewed":
            continue
        iid = it.get("id")
        try:
            path = target_file(root, kind, it)
        except (KeyError, TypeError, ValueError):
            continue  # 필드 누락은 V-CRS-001·V-CRS-008이 보고한다
        where = _rel(root, path)
        expected = it.get("reviewed_hash")
        if not expected:
            out.append(Finding("V-REV-002", "error", f"{kind} {iid}는 reviewed인데 reviewed_hash가 없다 — npm run review:approve {iid}", where))
        elif not path.is_file():
            out.append(Finding("V-REV-002", "error", f"{kind} {iid}는 reviewed인데 콘텐츠 파일이 없다", where))
        else:
            try:
                actual = content_hash(path)
            except UnicodeDecodeError:
                actual = None
            if actual != expected:
                out.append(Finding("V-REV-002", "error", f"{kind} {iid}: 승인 후 수정됨 — 다시 검토 필요(npm run review:approve {iid})", where))


# ---------------------------------------------------------------------------
# 규칙: 교시 MDX (V-LSN-*)
# ---------------------------------------------------------------------------

# CONTENT_GUIDE 1절 공통 필수 섹션 중 MDX 본문에 쓰는 것.
# 학습목표·결과 확인은 LessonLayout이 course.yaml에서 자동 표시하므로 본문 섹션으로 요구하지 않는다.
LESSON_COMMON_SECTIONS = ("이번 시간에 할 일", "필수 경로", "실습", "Harness에서 무엇을 바꿨는가", "다음 교시 연결")
LESSON_TYPE_SECTIONS = {"practice": ("예상 결과", "잘못된 결과 예시")}  # V-CRS-010의 ④⑤ 지원이 본문에 있는지
VAGUE_OBJECTIVE_RE = re.compile(r"(이해한다|안다|알아본다)[.\s]*$")
MAX_SENTENCE_CHARS = 120
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.M)
SUMMARY_RE = re.compile(r"<summary[^>]*>(.*?)</summary>", re.S | re.I)
MDX_COMMENT_RE = re.compile(r"\{/\*.*?\*/\}", re.S)
MDX_IMPORT_RE = re.compile(r"^(?:import|export)\s.*$", re.M)
TAG_ELEMENT_RE = re.compile(r"<[A-Za-z/!][^<>]*>")  # 태그 자체(속성 포함). 태그 사이의 본문은 남긴다
QUOTE_MARK_RE = re.compile(r"^\s*(?:>\s*)+")
LIST_MARK_RE = re.compile(r"^\s*(?:#{1,6}\s+|\d+\.\s+|[-*+]\s+)")
TABLE_RULE_RE = re.compile(r"[\s:-]+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.?!])\s+")
# V-LSN-004: 제품 정보는 <Feature>로만 쓴다(CONTENT_GUIDE 5절)
PRODUCT_INFO_PATTERNS = (
    ("메뉴 경로", re.compile(r"\w\)?\s*[>›]\s*\(?\w")),
    ("파일 개수", re.compile(r"파일\s*\d+\s*개")),
    ("용량", re.compile(r"\d+(?:\.\d+)?\s*[MG]B(?![A-Za-z])")),
)


def _split_frontmatter(text):
    """(frontmatter dict 또는 None, 본문). frontmatter가 yaml이 아니면 ValueError."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise ValueError(str(e).splitlines()[0]) from e
    return (data if isinstance(data, dict) else {}), text[m.end():]


def _prose_lines(body):
    """본문에서 코드 블록·인라인 코드·MDX 주석·import·태그를 뺀 서술 줄. 표는 칸별로 나눈다."""
    text = FENCE_RE.sub("", body)
    text = MDX_COMMENT_RE.sub("", text)
    text = MDX_IMPORT_RE.sub("", text)
    text = TAG_ELEMENT_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub("", text)
    for line in text.splitlines():
        line = LIST_MARK_RE.sub("", QUOTE_MARK_RE.sub("", line)).strip()
        if not line:
            continue
        if line.startswith("|"):
            yield from (c.strip() for c in line.strip("|").split("|")
                        if c.strip() and not TABLE_RULE_RE.fullmatch(c))
        else:
            yield line


def _section_titles(body):
    text = FENCE_RE.sub("", body)
    titles = [t.strip() for t in HEADING_RE.findall(text)]
    titles += [re.sub(r"<[^>]+>", "", t).strip() for t in SUMMARY_RE.findall(text)]
    return titles


def _has_section(titles, name):
    """제목이 name 그 자체이거나 'name — 부제'처럼 name으로 시작한다(<details>의 <summary>도 인정)."""
    pat = re.compile(rf"^{re.escape(name)}(?:$|[\s—–(:·-])")
    return any(pat.match(t) for t in titles)


def _lesson_files(root):
    """(day, 파일 경로) — content/day{d}/*.mdx."""
    content = root / "content"
    if not content.is_dir():
        return
    for d in sorted(content.iterdir()):
        m = re.fullmatch(r"day(\d+)", d.name)
        if m and d.is_dir():
            for p in sorted(d.glob("*.mdx")):
                yield int(m.group(1)), p


def check_lesson_files(root, course, out, scope_lessons):
    if course is None:
        return
    lessons = [les for les in course.get("lessons") or [] if isinstance(les, dict)]
    by_pos = {(les.get("day"), les.get("number")): les for les in lessons}

    def in_scope(lid):
        return scope_lessons is None or lid in scope_lessons

    # V-LSN-003 학습목표 동사
    for les in lessons:
        if not in_scope(les.get("id")):
            continue
        for o in les.get("objectives") or []:
            if VAGUE_OBJECTIVE_RE.search(str(o.get("text", ""))):
                out.append(Finding("V-LSN-003", "warn",
                                   f"학습목표 {o.get('id')}가 관찰할 수 없는 동사로 끝난다: '{o.get('text')}' "
                                   "(작성한다·구분한다·설명한다 등)", f"lesson {les.get('id')}"))

    found_ids = set()
    for day, path in _lesson_files(root):
        where = _rel(root, path)
        les = by_pos.get((day, int(path.stem))) if path.stem.isdigit() else None
        if les is None:
            if scope_lessons is None:
                out.append(Finding("V-LSN-001", "error",
                                   f"course.yaml에 Day {day} '{path.stem}' 위치의 교시가 없다(파일명은 교시 번호 NN.mdx)",
                                   where))
            continue
        lid = les.get("id")
        if not in_scope(lid):
            continue
        found_ids.add(lid)
        text = path.read_text(encoding="utf-8")
        try:
            fm, body = _split_frontmatter(text)
        except ValueError as e:
            out.append(Finding("V-LSN-001", "error", f"frontmatter를 읽을 수 없다: {e}", where))
            fm, body = {}, text
        # V-LSN-001 lesson_id
        got = (fm or {}).get("lesson_id")
        if not got:
            out.append(Finding("V-LSN-001", "error", f"frontmatter에 lesson_id가 없다(이 위치의 교시는 {lid})", where))
        elif got != lid:
            out.append(Finding("V-LSN-001", "error",
                               f"lesson_id '{got}'가 이 위치(Day {day} {path.stem})의 교시 {lid}와 다르다", where))
        # V-LSN-002 필수 섹션
        titles = _section_titles(body)
        for name in LESSON_COMMON_SECTIONS + LESSON_TYPE_SECTIONS.get(les.get("type"), ()):
            if not _has_section(titles, name):
                out.append(Finding("V-LSN-002", "error",
                                   f"필수 섹션 '{name}'이 없다({les.get('type')}, CONTENT_GUIDE 1절)", where))
        # V-LSN-003 문장 길이, V-LSN-004 제품 정보 직접 서술
        for line in _prose_lines(body):
            for sentence in SENTENCE_SPLIT_RE.split(line):
                if len(sentence) > MAX_SENTENCE_CHARS:
                    out.append(Finding("V-LSN-003", "warn",
                                       f"문장이 {len(sentence)}자로 {MAX_SENTENCE_CHARS}자를 넘는다: '{sentence[:30]}…'",
                                       where))
            for label, pat in PRODUCT_INFO_PATTERNS:
                m = pat.search(line)
                if m:
                    out.append(Finding("V-LSN-004", "warn",
                                       f"제품 정보({label})를 직접 쓴 것 같다: '{m.group(0)}' → <Feature id>로 참조", where))

    # V-LSN-001 draft·reviewed 교시의 파일 누락
    for les in lessons:
        lid = les.get("id")
        if in_scope(lid) and les.get("status") in ("draft", "reviewed") and lid not in found_ids:
            try:
                where = _rel(root, target_file(root, "lesson", les))
            except (KeyError, TypeError, ValueError):
                where = ""
            out.append(Finding("V-LSN-001", "error",
                               f"교시 {lid}는 status가 {les.get('status')}인데 교시 파일이 없다", where))


# ---------------------------------------------------------------------------
# 규칙: 카드 파일 (V-PRM-*)
# 필드 타입·형식은 zod(src/content.config.ts)가 본다(ADR-004). 여기서는 course.yaml과의 교차 규칙만 본다.
# ---------------------------------------------------------------------------

CARD_CROSS_FIELDS = ("id", "stuck_point", "where", "default_level", "l2_template", "l1_full", "replace")
BRACKET_RE = re.compile(r"\[[^\[\]\n]+\]")  # src/lib/prompt-text.ts의 BRACKET과 같은 정의


def check_prompt_files(root, course, out, today, freshness, scope_lessons, scope_cards):
    if course is None:
        return
    cards = {c.get("id"): c for c in course.get("cards") or [] if isinstance(c, dict)}
    backing = {}
    for les in course.get("lessons") or []:
        for sp in les.get("stuck_points") or []:
            if sp.get("card"):
                backing.setdefault(sp["card"], set()).add(sp.get("id"))
    folder = root / "content" / "prompts"
    files = sorted(folder.glob("*.md")) if folder.is_dir() else []
    seen = set()
    for path in files:
        cid, where = path.stem, _rel(root, path)
        card = cards.get(cid)
        if card is None:
            if scope_lessons is None:
                out.append(Finding("V-PRM-001", "error", f"카드 파일 {cid}가 course.yaml cards에 없다", where))
            continue
        if not _card_in_scope(card, scope_lessons, scope_cards):
            continue
        seen.add(cid)
        try:
            fm, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as e:
            out.append(Finding("V-PRM-001", "error", f"frontmatter를 읽을 수 없다: {e}", where))
            continue
        fm = fm or {}
        missing = [k for k in CARD_CROSS_FIELDS if fm.get(k) is None]
        if missing:
            out.append(Finding("V-PRM-001", "error", f"카드 {cid}에 필수 필드가 없다: {', '.join(missing)}", where))
        if fm.get("id") is not None and fm.get("id") != cid:
            out.append(Finding("V-PRM-001", "error", f"frontmatter id '{fm.get('id')}'가 파일명 {cid}와 다르다", where))
        sp = fm.get("stuck_point")
        if sp is not None and sp not in backing.get(cid, set()):
            out.append(Finding("V-PRM-001", "error",
                               f"stuck_point '{sp}'는 course.yaml에서 카드 {cid}를 가리키는 막힘 지점이 아니다", where))
        if fm.get("where") is not None and fm.get("where") != card.get("where"):
            out.append(Finding("V-PRM-001", "error",
                               f"where '{fm.get('where')}' ≠ course.yaml where '{card.get('where')}'", where))
        if fm.get("default_level") is not None and fm.get("default_level") != card.get("level"):
            out.append(Finding("V-PRM-001", "error",
                               f"default_level {fm.get('default_level')} ≠ course.yaml level {card.get('level')}", where))
        if fm.get("replace") is not None:
            used = set(BRACKET_RE.findall(str(fm.get("l2_template") or "")))
            used |= set(BRACKET_RE.findall(str(fm.get("l1_full") or "")))
            listed = {str(r) for r in fm.get("replace") or []}
            for b in sorted(used - listed):
                out.append(Finding("V-PRM-001", "error", f"대괄호 {b}가 replace 목록에 없다", where))
            for b in sorted(listed - used):
                out.append(Finding("V-PRM-001", "error", f"replace의 {b}가 l2_template·l1_full에 없다", where))
        # V-PRM-002
        if card.get("level") == 3 and not str(fm.get("l2_template") or "").strip():
            out.append(Finding("V-PRM-002", "error",
                               f"직접 쓰기(level 3) 카드 {cid}에 바꿔 쓰기(l2_template) 대안이 없다", where))
        # V-PRM-003
        tested = _parse_date(fm.get("tested_at"))
        if tested is None:
            out.append(Finding("V-PRM-003", "warn", f"카드 {cid}의 tested_at이 없다(실제 계정 테스트 전, H-04)", where))
        elif (today - tested).days > freshness:
            out.append(Finding("V-PRM-003", "warn", f"카드 {cid}의 tested_at {tested}이 {freshness}일을 넘었다", where))

    for cid, card in cards.items():
        if (_card_in_scope(card, scope_lessons, scope_cards) and card.get("status") in ("draft", "reviewed")
                and cid not in seen):
            out.append(Finding("V-PRM-001", "error",
                               f"카드 {cid}는 status가 {card.get('status')}인데 카드 파일이 없다",
                               f"content/prompts/{cid}.md"))


# ---------------------------------------------------------------------------
# 규칙: 빌드 결과 (V-WEB-*) — 네트워크에 접속하지 않는다. 외부 URL은 존재 여부만 본다.
# ---------------------------------------------------------------------------

ATTR_URL_RE = re.compile(r"""\s(?:href|src)\s*=\s*(["'])([^"']*)\1""", re.I)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.I)
LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.I)
EXTERNAL_URL_RE = re.compile(r"^(?:https?:)?//", re.I)
MODULE_SCRIPT_RE = re.compile(r"""\stype\s*=\s*["']?module\b""", re.I)
WEBFONT_RE = re.compile(r"""@font-face\s*\{[^}]*url\(\s*["']?(?:https?:)?//""", re.I)


def _attr(tag, name):
    m = re.search(rf"""\s{name}\s*=\s*(["'])([^"']*)\1""", tag, re.I)
    return m.group(2) if m else None


def _files(base, suffix):
    return sorted(p for p in base.rglob(f"*{suffix}") if p.is_file())


def _root_urls(html_text):
    """사이트 루트 기준 URL(/...). 프로토콜 상대 URL(//...)은 외부로 본다."""
    return sorted({m.group(2) for m in ATTR_URL_RE.finditer(html_text)
                   if m.group(2).startswith("/") and not m.group(2).startswith("//")})


def _resolves(base, url):
    path = re.split(r"[?#]", url, maxsplit=1)[0]
    rel = path.lstrip("/")
    if not rel or path.endswith("/"):
        return (base / rel / "index.html").is_file()
    return any(p.is_file() for p in (base / rel, base / rel / "index.html", base / f"{rel}.html"))


def check_web(root, out):
    dist = root / "dist"
    if not dist.is_dir():
        out.append(Finding("V-WEB-001", "info", "dist/가 없어 빌드 결과 검사를 건너뛴다(npm run build 후 검사)"))
    else:
        # V-WEB-001 내부 링크·이미지 경로
        for html in _files(dist, ".html"):
            text = html.read_text(encoding="utf-8", errors="replace")
            for url in _root_urls(text):
                if not _resolves(dist, url):
                    out.append(Finding("V-WEB-001", "error", f"없는 내부 경로: {url}", _rel(root, html)))
    # V-WEB-002 외부 자원·모듈 스크립트·오프라인 번들 상대경로
    for base in (dist, root / "dist-offline"):
        if not base.is_dir():
            continue
        offline = base.name == "dist-offline"
        for html in _files(base, ".html"):
            text, where = html.read_text(encoding="utf-8", errors="replace"), _rel(root, html)
            for tag in SCRIPT_TAG_RE.findall(text):
                src = _attr(tag, "src")
                if src and EXTERNAL_URL_RE.match(src):
                    out.append(Finding("V-WEB-002", "error", f"외부 스크립트: {src}", where))
                if MODULE_SCRIPT_RE.search(tag):
                    out.append(Finding("V-WEB-002", "error",
                                       "모듈 스크립트(type=module)는 file://에서 차단된다 — is:inline으로 쓴다", where))
            for tag in LINK_TAG_RE.findall(text):
                rel = (_attr(tag, "rel") or "").lower().split()
                href = _attr(tag, "href")
                if "stylesheet" in rel and href and EXTERNAL_URL_RE.match(href):
                    out.append(Finding("V-WEB-002", "error", f"외부 스타일시트: {href}", where))
            if WEBFONT_RE.search(text):
                out.append(Finding("V-WEB-002", "error", "외부 웹폰트(@font-face url)", where))
            if offline:
                for url in _root_urls(text):
                    out.append(Finding("V-WEB-002", "error", f"오프라인 번들의 내부 링크가 상대경로가 아니다: {url}", where))
        for css in _files(base, ".css"):
            if WEBFONT_RE.search(css.read_text(encoding="utf-8", errors="replace")):
                out.append(Finding("V-WEB-002", "error", "외부 웹폰트(@font-face url)", _rel(root, css)))


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------

def _resolve_scope(root, scope):
    """scope 문자열 → (교시 ID 집합, 카드 ID 집합, 오류 메시지). 전체 범위는 (None, None, None)."""
    if not scope or scope == "all":
        return None, None, None
    kind, _, target = scope.partition(":")
    course_path = root / "content" / "course.yaml"
    course = _load_yaml(course_path) if course_path.exists() else {}
    lesson_ids = {les.get("id") for les in course.get("lessons") or []}
    card_ids = {c.get("id") for c in course.get("cards") or []}
    if kind == "lesson":
        if target not in lesson_ids:
            return set(), set(), f"없는 교시: {target}"
        return {target}, set(), None
    if kind == "card":
        if target not in card_ids:
            return set(), set(), f"없는 카드: {target}"
        return set(), {target}, None
    if kind == "day":
        found = {les.get("id") for les in course.get("lessons") or [] if str(les.get("day")) == target}
        return (found, set(), None) if found else (set(), set(), f"없는 Day: {target}")
    if kind == "phase":
        return _phase_scope(root, target, lesson_ids, card_ids)
    return set(), set(), f"알 수 없는 scope 형식: {scope} (lesson:<id> | card:<id> | day:<n> | phase:<dir> | all)"


def _phase_scope(root, name, lesson_ids, card_ids):
    """phases/<name>/index.json의 review_targets(lesson:<id>, card:<id>)만 범위로 삼는다."""
    index = root / "phases" / name / "index.json"
    if not name or not index.is_file():
        return set(), set(), f"없는 phase: {name} (phases/{name}/index.json)"
    try:
        targets = json.loads(index.read_text(encoding="utf-8")).get("review_targets")
    except (ValueError, AttributeError):
        return set(), set(), f"phases/{name}/index.json을 읽을 수 없다"
    if not targets or not isinstance(targets, list):
        return set(), set(), f"phases/{name}/index.json에 review_targets가 없다"
    lessons, cards, errors = set(), set(), []
    for t in targets:
        kind, _, target = str(t).partition(":")
        if kind == "lesson" and target in lesson_ids:
            lessons.add(target)
        elif kind == "card" and target in card_ids:
            cards.add(target)
        else:
            errors.append(str(t))
    if errors:
        return set(), set(), f"phase {name}의 review_targets에 없는 대상: {', '.join(errors)} (lesson:<id> | card:<id>)"
    return lessons, cards, None


def validate(root: Path, *, docs_only=False, scope=None, require_reviewed=False,
             today=None, check_git=True):
    out = []
    today = _parse_date(today) or dt.date.today()
    scope_lessons, scope_cards, scope_err = _resolve_scope(root, scope)
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
    check_review_hashes(root, course, out, scope_lessons, scope_cards)
    check_lesson_files(root, course, out, scope_lessons)
    check_prompt_files(root, course, out, today, freshness, scope_lessons, scope_cards)
    if not docs_only:  # 빌드 결과 검사는 docs_only(Phase 1 이전 AC·Stop 훅)에서 건너뛴다
        check_web(root, out)
    if require_reviewed:
        check_reviewed(course, out, scope_lessons, scope_cards)
    return out



def _safe_console():
    """콘솔 인코딩(예: Windows cp949)에 없는 문자('—' 등)는 바꿔 출력해 검사가 출력 단계에서 죽지 않게 한다."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def main(argv=None):
    parser = argparse.ArgumentParser(description="교육자료 Harness 검증기")
    parser.add_argument("--docs-only", action="store_true", help="docs·yaml 수준 규칙만 검사 (Phase 1 이전 AC)")
    parser.add_argument("--scope", default=None, help="lesson:<id> | card:<id> | day:<n> | phase:<dir> | all")
    parser.add_argument("--require-reviewed", action="store_true", help="범위 안 항목이 모두 reviewed인지 검사")
    parser.add_argument("--production", action="store_true", help="Production 관문: --require-reviewed 포함")
    parser.add_argument("--pre-launch", action="store_true", help="개설 전 점검: 확인일 경과 경고를 오류로 격상")
    parser.add_argument("--no-git", action="store_true", help="git 추적 검사 생략")
    parser.add_argument("--today", default=None, help="기준일(YYYY-MM-DD), 테스트용")
    parser.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = parser.parse_args(argv)
    _safe_console()

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
