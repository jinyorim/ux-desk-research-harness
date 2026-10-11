"""한국어 문장 검사 (docs/korean-writing.md).

    python harness/judge/check_korean.py runs/<slug>/s4_insights.md
    python harness/judge/check_korean.py runs/<slug>/s5_report.md

검사 대상: front matter의 문구(cover, key_findings, sections, limits, method)와 본문 문장.
출처 목록, 표 구분선, 코드, URL은 제외한다.
- 실패: 금지 문장부호(가운뎃점, em dash, en dash), 거친 표현, S1 번역투, S2 패턴이 문서에서 s2_max회 초과
- 경고: 한 문장의 보조사 은/는 과다, 명사 앞 긴 관형절, 흐린 말, 칸별 길이 초과, 연결어미 뒤 쉼표 과다
기준 수치는 harness/rules.yaml korean. Kiwi(kiwipiepy) 형태소 분석을 쓴다.
종료 코드: 0 통과(경고 허용) / 1 실패 / 2 오류
"""
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import exit_code, load_rules, utf8_stdout  # noqa: E402

URL = re.compile(r"https?://\S+")
MARK = re.compile(r"\[(\d+|[ABC](?:/[ABC])?)\]|\*\*|`")
PRED_TAGS = {"VV", "VA", "XSV", "XSA", "VCP", "VX"}
# 조건·이유·대조 어미 뒤에서는 관형절 세기를 새로 시작한다 ("바꾸지 않으면 많이 팔린 클래스")
CLAUSE_ENDINGS = {"면", "으면", "지만", "는데", "은데", "니까", "으니까", "어서", "아서", "므로", "으므로", "도록"}
EN_DASH_RANGE = re.compile(r"[0-9A-Za-z]–[0-9A-Za-z]")   # 영문·숫자 범위는 허용


def clean(text):
    return MARK.sub("", URL.sub("", text)).strip()


def front_items(front):
    """(위치, 칸 종류, 문장) 목록."""
    items = []
    cover = front.get("cover") or {}
    for k, kind in (("question", "title"), ("answer", "answer"), ("subtitle", "sentence")):
        if cover.get(k):
            items.append((f"cover.{k}", kind, cover[k]))
    for i, f in enumerate(front.get("key_findings") or [], 1):
        if isinstance(f, str):
            f = {"claim": f}
        for k in ("claim", "why", "so_what", "confidence_reason"):
            if f.get(k):
                items.append((f"K{i}.{k}", "claim" if k == "claim" else "sentence", f[k]))
        for j, e in enumerate(f.get("evidence") or [], 1):
            items.append((f"K{i}.evidence{j}", "sentence", e))
        h = f.get("hmw") or {}
        if isinstance(h, dict):
            if h.get("question"):
                items.append((f"K{i}.hmw", "sentence", h["question"]))
            for k, v in (h.get("ideas") or {}).items():
                items.append((f"K{i}.ideas.{k}", "sentence", v))
    for key, h in (front.get("sections") or {}).items():
        for k in ("headline", "lead"):
            if h.get(k):
                items.append((f"sections.{key}.{k}", "headline" if k == "headline" else "sentence", h[k]))
    for i, l in enumerate(front.get("limits") or [], 1):
        for k, v in l.items():
            items.append((f"limits{i}.{k}", "sentence", v))
    for k, v in (front.get("method") or {}).items():
        items.append((f"method.{k}", "sentence", str(v)))
    return items


def body_items(body):
    """(위치, 칸 종류, 문장, 섹션) 목록. 표는 칸 단위로 나눈다."""
    items, in_refs, in_code, section = [], False, False, ""
    for n, line in enumerate(body.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s or s.startswith("<!--"):
            continue
        if re.match(r"^#{1,6}\s*(출처|참고\s*자료)\s*$", s):
            in_refs = True
            continue
        if s.startswith("#"):
            in_refs = False
            if s.startswith("## "):
                section = re.split(r"[:\s]", s[3:].strip(), maxsplit=1)[0]
            items.append((f"본문 {n}행(제목)", "heading", s.lstrip("# "), section))
            continue
        if in_refs or re.fullmatch(r"\|[\s:|-]+\|?", s) or s.startswith("!["):
            continue
        if s.startswith("|"):
            for c, cell in enumerate(s.strip("|").split("|"), 1):
                if cell.strip():
                    items.append((f"본문 {n}행 {c}칸", "cell", cell.strip(), section))
            continue
        s = re.sub(r"^(>\s*|[-*+]\s+|\d+\.\s+)", "", s)
        for part in re.split(r"(?<=[.!?])\s+", s):
            if part.strip():
                items.append((f"본문 {n}행", "sentence", part, section))
    return items


def split_front(md):
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if not m:
        return {}, md
    return yaml.safe_load(m.group(1)) or {}, md[m.end():]


def modifier_chain(tokens):
    """명사 앞 관형절 안 서술어 수의 최댓값 (예: '후보를 고르고 비교하는 기능' = 2)."""
    best, preds = 0, 0
    for i, t in enumerate(tokens):
        if t.tag in PRED_TAGS:
            preds += 1
        elif t.tag == "ETM":
            # 일반·고유 명사 앞일 때만 관형절로 센다 ('할 수', '한 것' 같은 의존명사 앞은 제외)
            if i + 1 < len(tokens) and tokens[i + 1].tag in ("NNG", "NNP"):
                best = max(best, preds)
            preds = 0
        elif t.tag in ("JKS", "JX", "SF") or (t.tag == "SP" and t.form == ",")                 or (t.tag == "EC" and t.form in CLAUSE_ENDINGS):
            preds = 0
    return best


def check(md, rules, kiwi):
    k = rules["korean"]
    front, body = split_front(md)
    items = [(*it, "front") for it in front_items(front)] + body_items(body)
    exempt = k.get("s2_exempt", {})
    fails, warns = [], []
    s2_hits = {}
    comma_endings = total_endings = 0
    for loc, kind, raw, section in items:
        text = clean(str(raw))
        if not text:
            continue
        for ch in k["forbidden_chars"]:
            if ch in text:
                if ch == "–" and EN_DASH_RANGE.search(text) and text.count(ch) == len(EN_DASH_RANGE.findall(text)):
                    continue
                fails.append(f"{loc}: 금지 문장부호 U+{ord(ch):04X} '{ch}' → {text[:40]}")
        for w in k["rough_words"]:
            if w in text:
                fails.append(f"{loc}: 거친 표현 '{w}' → {text[:40]}")
        for pat in k["s1_patterns"]:
            m = re.search(pat, text)
            if m:
                fails.append(f"{loc}: 번역투(S1) '{m.group(0)}' → {text[:40]}")
        for pat in k["s2_patterns"]:
            if section in exempt.get(pat, []):
                continue
            for m in re.finditer(pat, text, re.M):
                s2_hits.setdefault(pat, []).append(f"{loc}: '{m.group(0)}'")
        for w in k["vague_words"]:
            if w in text:
                warns.append(f"{loc}: 흐린 말 '{w}' → {text[:40]}")
        limit = k["max_chars"].get(kind)
        if limit and len(text) > limit:
            warns.append(f"{loc}: 길이 {len(text)}자 > {limit}자 → {text[:30]}")
        if kind == "heading":
            continue
        toks = kiwi.tokenize(text)
        topics = [t for t in toks if t.tag == "JX" and t.form in ("은", "는")]
        if len(topics) > k["topic_marker_max"]:
            warns.append(f"{loc}: 보조사 은/는 {len(topics)}개 → {text[:40]}")
        chain = modifier_chain(toks)
        if chain > k["modifier_pred_max"]:
            warns.append(f"{loc}: 명사 앞 관형절 서술어 {chain}개 → {text[:40]}")
        for i, t in enumerate(toks):
            if t.tag == "EC":
                total_endings += 1
                if i + 1 < len(toks) and toks[i + 1].form == ",":
                    comma_endings += 1
    for pat, hits in s2_hits.items():
        if len(hits) > k["s2_max"]:
            fails.append(f"S2 '{pat}' {len(hits)}회 > {k['s2_max']}회: " + "; ".join(hits[:4]))
    if total_endings and comma_endings / total_endings > k["comma_after_ending_ratio"]:
        warns.append(f"연결어미 뒤 쉼표 {comma_endings}/{total_endings} = {comma_endings / total_endings:.0%} "
                     f"> {k['comma_after_ending_ratio']:.0%}")
    return fails, warns, len(items)


def main():
    utf8_stdout()
    rules = load_rules()
    if len(sys.argv) != 2 or not Path(sys.argv[1]).exists():
        print("사용법: python harness/judge/check_korean.py <md>", file=sys.stderr)
        return exit_code("error", rules)
    try:
        from kiwipiepy import Kiwi
    except ImportError:
        print("오류: kiwipiepy 없음 (pip install kiwipiepy)", file=sys.stderr)
        return exit_code("error", rules)
    fails, warns, n = check(Path(sys.argv[1]).read_text(encoding="utf-8"), rules, Kiwi())
    for f in fails:
        print("실패:", f)
    for w in warns:
        print("경고:", w)
    print(f"문장 {n}개 / 실패 {len(fails)}건 / 경고 {len(warns)}건")
    return exit_code("fail" if fails else "pass", rules)


if __name__ == "__main__":
    sys.exit(main())
