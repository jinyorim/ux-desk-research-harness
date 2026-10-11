"""스크립트 판정 (docs/gates.md G-A 중 스크립트 담당 항목).

리포트 형식: 주장 문장마다 출처 번호 [n]을 붙이고, 끝의 "참고자료" 제목 아래에
`n. 제목, URL` 목록을 둔다. 표 행은 한 행을 한 문장으로 본다.

여기서 실패한 문장은 Jev에 보내지 않는다 (docs/gates.md 판정 순서 1).
"""
import re
from datetime import date

REF_HEADING = re.compile(r"^#{1,6}\s*(참고\s*자료|참고\s*문헌|출처|references|sources)\s*$", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
CITE = re.compile(r"\[(\d+)\]")
GRADE = re.compile(r"\[(?:[ABC](?:/[ABC])?)\]")
ENGINE_TOKEN = re.compile(r"cite[a-z]*turn\w*|turn\d+\w+", re.I)
URL = re.compile(r"https?://[^\s)\]>,]+")
REF_LINE = re.compile(r"^\s*>?\s*(\d+)\.\s*(.*)$")
LOCAL_FILE = re.compile(r"\.(md|docx?|pdf|hwpx?|txt|json)\s*$", re.I)
QUOTE = re.compile(r"[\"“”]([^\"“”]{4,})[\"“”]")

# 이름의 일부인 경우는 단위로 보지 않는다: 6분류, 5원칙, 3주차
UNITS = r"%p|%|배|명|원(?!칙)|개|주(?!차)|시간|분(?!류)|년|월|일|건|곳|회|세|만|천|억"
RANGE = re.compile(rf"(\d+(?:\.\d+)?)\s*~\s*(\d+(?:\.\d+)?)\s*({UNITS})?")
NUMBER = re.compile(rf"(?<![\d.])(\d+(?:\.\d+)?)\s*({UNITS})?")
FRACTION = re.compile(r"(?<!\d)(\d+)\s*/\s*(\d+)(?!\d)")


# ---------- 정규화 ----------

def normalize(text):
    text = text.replace("\\", "")
    text = re.sub(r"(?<=\d)\s*[~～〜–—-]\s*(?=\d)", "~", text)
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    return re.sub(r"\s+", " ", text)


def squash(text):
    """따옴표 대조용: 공백·문장부호를 모두 지운다."""
    return re.sub(r"[\s\W_]+", "", normalize(text))


def strip_markers(text):
    text = CITE.sub(" ", text)
    text = GRADE.sub(" ", text)
    text = URL.sub(" ", text)
    return normalize(text)


# ---------- 리포트 파싱 ----------

TABLE_SEP = re.compile(r"\|[\s:|-]+\|?")


def parse_report(md, rules):
    """본문 문장 단위와 참고자료 목록을 돌려준다.

    표는 한 행을 한 문장으로 보되 머리글 행(바로 아래가 구분선인 행)은 뺀다.
    문장마다 속한 섹션(## 제목의 첫 낱말)과 인용 블록 여부(quote)를 붙인다.
    """
    units, refs, headings = [], {}, []
    in_refs, section = False, ""
    min_chars = rules["claims"]["min_chars"]
    lines = [l.strip() for l in md.splitlines()]
    for i, line in enumerate(lines):
        if not line or line in ("---", "&nbsp;") or line.startswith("<!--") or line.startswith("!["):
            continue
        h = HEADING.match(line)
        if h:
            title = h.group(2).strip().strip("*")
            in_refs = bool(REF_HEADING.match(f"# {title}"))
            if len(h.group(1)) == 2:
                section = re.split(r"[:\s]", title, maxsplit=1)[0]
            headings.append(title)
            continue
        if in_refs:
            m = REF_LINE.match(line)
            if m:
                refs[m.group(1)] = m.group(2).replace("&nbsp;", "").strip()
            continue
        quote = line.startswith(">")
        if line.startswith("|"):
            nxt = next((l for l in lines[i + 1:] if l), "")
            if TABLE_SEP.fullmatch(line) or TABLE_SEP.fullmatch(nxt):
                continue
            pieces = [line]
        else:
            line = re.sub(r"^(>\s*|[*+-]\s+|\d+\.\s+)", "", line)
            pieces = re.split(r"(?<=[.!?])\s+(?=\S)", line)
        for p in pieces:
            if len(strip_markers(p).strip(" |*")) >= min_chars:
                units.append({"index": len(units), "text": p, "section": section, "quote": quote})
    return units, refs, headings


# ---------- 문서 단위 검사 ----------

def check_headings(headings, rules):
    banned = rules["forbidden_headings"]
    return [{"heading": h, "reason": "forbidden_heading"}
            for h in headings if any(b in h for b in banned)]


# ---------- 문장 단위 검사 ----------

def numbers_in(text):
    """주장 문장의 숫자 토큰. 단위 없는 한 자리 숫자는 대조하지 않는다."""
    text = strip_markers(text)
    found, spans = [], []
    for m in RANGE.finditer(text):
        found.append(("range", m.group(1), m.group(2), m.group(3) or ""))
        spans.append(m.span())
    for m in FRACTION.finditer(text):
        if not any(a <= m.start() < b for a, b in spans):
            found.append(("fraction", m.group(1), m.group(2), ""))
            spans.append(m.span())
    for m in NUMBER.finditer(text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        value, unit = m.group(1), m.group(2) or ""
        if not unit and len(value) == 1:
            continue
        found.append(("single", value, None, unit))
    return found


def _has(value, unit, src):
    pat = rf"(?<![\d.]){re.escape(value)}(?![\d])"
    if unit and unit not in ("만", "천", "억"):
        pat += rf"\s*{re.escape(unit)}"
    return re.search(pat, src) is not None


def number_in_source(token, src):
    kind, a, b, unit = token
    if kind == "range":
        if re.search(rf"(?<![\d.]){re.escape(a)}\s*{re.escape(unit)}?\s*~\s*{re.escape(b)}(?![\d])", src):
            return True
        return _has(a, "", src) and _has(b, unit, src)
    if kind == "fraction":
        return re.search(rf"(?<!\d){a}\s*/\s*{b}(?!\d)", src) is not None or \
            re.search(rf"{b}\s*분의\s*{a}", src) is not None
    return _has(a, unit, src)


def quotes_in(text):
    return [q.strip() for q in QUOTE.findall(text)]


OBSERVATION = re.compile(r"observation:\s*\S+")


def classify_ref(entry):
    """참고자료 한 항목: ok / observation / empty / local_file / no_url.

    observation: 사람이 직접 관찰한 1차 출처. s2_sources/observations/의 관찰 기록 파일을 원문으로 쓴다
    (docs/gates.md G-A).
    """
    if not entry or not entry.strip():
        return "empty"
    if URL.search(entry):
        return "ok"
    if OBSERVATION.search(entry):
        return "observation"
    return "local_file" if LOCAL_FILE.search(entry) else "no_url"


def date_parts(sources, ns):
    """출처 게시일의 연, 월, 일. 기사 날짜를 본문이 아니라 메타데이터에만 둔 경우를 인정한다."""
    parts = set()
    for n in ns:
        pub = (sources.get(n) or {}).get("published") or ""
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", pub)
        if m:
            parts |= {("년", str(int(m.group(1)))), ("월", str(int(m.group(2)))), ("일", str(int(m.group(3))))}
    return parts


def years_between(start, end):
    return (end - start).days / 365.25


def check_unit(unit, refs, sources, rules, as_of, mode="engine"):
    """문장 하나의 스크립트 판정. 실패 사유 목록을 돌려준다 (빈 목록 = 통과).

    mode="report" (S5 보고서): 인용 블록(해석)과 HYPOTHESIS 섹션은 검사하지 않는다.
    출처 없는 문장은 숫자가 있으면 실패, 없으면 경고(unit["warn"])로 둔다.
    """
    text = unit["text"]
    fails = []
    cites = sorted(set(CITE.findall(text)), key=int)
    unit["cites"] = cites
    if mode == "report" and (unit.get("quote") or unit.get("section") in rules["report_check"]["skip_sections"]):
        unit["skip"] = True
        return []
    if not cites:
        if mode == "report" and not numbers_in(text) and not ENGINE_TOKEN.search(text):
            unit["warn"] = "no_citation"
            return []
        if mode == "report" and unit.get("section") in rules["report_check"]["internal_sections"]:
            unit["warn"] = "internal_record"   # 하네스 판정 기록의 건수 (s3 파일과 대조)
            return []
        reason = "engine_token_only" if ENGINE_TOKEN.search(text) else (
            "number_without_citation" if mode == "report" else "no_citation")
        return [{"reason": reason}]

    usable = []
    for n in cites:
        kind = classify_ref(refs.get(n))
        if kind == "empty":
            fails.append({"reason": "empty_reference", "ref": n})
        elif kind == "local_file":
            fails.append({"reason": "self_or_local_reference", "ref": n, "entry": refs[n]})
        elif kind == "no_url":
            fails.append({"reason": "reference_without_url", "ref": n})
        elif kind == "observation" and not (sources.get(n) or {}).get("text"):
            fails.append({"reason": "observation_record_missing", "ref": n})
        elif kind == "observation":
            usable.append(n)
        else:
            src = sources.get(n) or {}
            status = src.get("status")
            if not src.get("text"):
                fails.append({"reason": "source_not_saved", "ref": n})
            elif not status or not 200 <= int(status) < 400:
                fails.append({"reason": "source_unreachable", "ref": n, "status": status})
            else:
                usable.append(n)
    if fails:
        return fails

    joined = normalize(" ".join(sources[n]["text"] for n in usable))
    dates = date_parts(sources, usable)
    for tok in numbers_in(text):
        if tok[0] == "single" and (tok[3], tok[1]) in dates:
            continue
        if not number_in_source(tok, joined):
            fails.append({"reason": "number_not_in_source", "number": "~".join(x for x in tok[1:3] if x) + tok[3]})
    squashed = squash(joined)
    for q in quotes_in(text):
        if squash(q) not in squashed:
            fails.append({"reason": "quote_not_in_source", "quote": q})

    fr = rules["freshness"]
    if numbers_in(text) and any(t in text for t in fr["sensitive_terms"]) and fr["stale_label"] not in text:
        for n in usable:
            pub = sources[n].get("published")
            if pub and years_between(date.fromisoformat(pub[:10]), as_of) > fr["max_years"]:
                fails.append({"reason": "stale_without_label", "ref": n, "published": pub[:10]})
    return fails


def check_claim(claim, unit):
    """judge가 쪼갠 주장이 원래 문장을 벗어나지 않았는지 (숫자 기준)."""
    src = normalize(strip_markers(unit["text"]))
    # 단위가 아니라 값으로 대조한다 (표 칸의 "10"과 주장의 "10개"는 같은 값)
    missing = [t for t in numbers_in(claim["text"])
               if not number_in_source(t, src) and not number_in_source((t[0], t[1], t[2], ""), src)]
    if str(claim["source"]) not in unit.get("cites", []):
        return [{"reason": "claim_source_not_cited_in_sentence", "ref": claim["source"]}]
    if missing:
        return [{"reason": "claim_not_in_sentence", "numbers": ["~".join(x for x in t[1:3] if x) + t[3] for t in missing]}]
    return []
