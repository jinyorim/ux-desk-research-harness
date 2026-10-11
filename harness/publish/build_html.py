"""s5_report.md → s5_report.html (html 페이지 구성은 docs/outputs.md).

    python harness/publish/build_html.py runs/<slug>/s5_report.md [--out 파일]

- md 앞부분(front matter): title, topic, run_date, scope, sources_used, counts, key_findings,
  tags, sections.<key>.headline/lead (헤드라인의 **굵게**는 강조색)
- 본문: "## MARKET …" 같은 제목으로 섹션을 나눈다. "### 유사 서비스 UI"는 별도 영역(4-1)
- `![캡션](figures/x.svg)` → SVG를 파일 안에 넣은 그림, `> 인용` → INSIGHT 박스
- `<!-- detail -->` … `<!-- /detail -->` → 접힌 상세 (docx에서는 빠짐)
- `[n]` → 출처 목록으로 가는 링크, `[A]`/`[B]`/`[C]` → 등급 표시
- Pretendard는 사용한 글자만 추려 woff2로 내장 (외부 로드 없음)
"""
import argparse
import base64
import html
import io
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "judge"))
from common import HARNESS, load_rules, utf8_stdout  # noqa: E402

TEMPLATE = HARNESS / "publish" / "template.html"

# docs/outputs.md 순서. (key, 제목 판별 접두어, 영문 라벨, 한글 이름)
SECTIONS = [
    ("market", "MARKET", "MARKET", "시장"),
    ("competitors", "COMPETITORS", "COMPETITORS", "경쟁 지형"),
    ("similar-ui", "유사 서비스 UI", "SIMILAR UI", "유사 서비스 UI"),
    ("solution-gap", "SOLUTION GAP", "SOLUTION GAP", "미충족 필요"),
    ("crosscheck", "교차검증", "CROSS-CHECK", "교차검증 결과"),
    ("why-ai", "WHY AI", "WHY AI", "왜 AI인가"),
    ("hypothesis", "HYPOTHESIS", "HYPOTHESIS", "가설"),
    ("sources", "출처", "SOURCES", "출처"),
]
FONT_WEIGHTS = {400: "Pretendard-Regular.otf", 600: "Pretendard-SemiBold.otf", 700: "Pretendard-Bold.otf"}


def esc(s):
    return html.escape(str(s), quote=True)


def inline_md(s):
    """front matter 문구: **굵게** → 강조색."""
    return re.sub(r"\*\*(.+?)\*\*", r'<em class="hl">\1</em>', esc(s))


def split_front(md):
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    return (yaml.safe_load(m.group(1)) or {}, md[m.end():]) if m else ({}, md)


def split_sections(body):
    """'## 제목' 단위로 나누고 key를 붙인다. '### 유사 서비스 UI'는 따로 뗀다."""
    parts = {}
    chunks = re.split(r"^## +(.+)$", body, flags=re.M)
    for title, text in zip(chunks[1::2], chunks[2::2]):
        key = next((k for k, pre, *_ in SECTIONS if title.strip().startswith(pre)), None)
        if not key:
            raise SystemExit(f"알 수 없는 섹션 제목: {title}")
        parts[key] = (title.strip(), text.strip())
    if "competitors" in parts:
        title, text = parts["competitors"]
        m = re.search(r"^### +유사 서비스 UI.*$", text, flags=re.M)
        if m:
            parts["competitors"] = (title, text[:m.start()].strip())
            parts["similar-ui"] = ("유사 서비스 UI", text[m.end():].strip())
    return parts


def find_pandoc():
    """실제 pandoc 실행 파일을 먼저 찾는다. Chocolatey 바로가기(shim)는 Windows 앱 제어 정책에 막힐 수 있다."""
    import shutil
    cands = [os.environ.get("PANDOC"),
             str(Path(os.environ.get("LOCALAPPDATA", "")) / "Pandoc" / "pandoc.exe"),
             str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Pandoc" / "pandoc.exe"),
             shutil.which("pandoc")]
    for c in cands:
        if c and Path(c).exists():
            return c
    raise SystemExit("pandoc을 찾지 못함 (환경변수 PANDOC으로 경로 지정 가능)")


def pandoc(md):
    r = subprocess.run([find_pandoc(), "-f", "gfm", "-t", "html5", "--wrap=none"],
                       input=md.encode("utf-8"), capture_output=True, check=True)
    return r.stdout.decode("utf-8")


def outside_tags(h, fn):
    """태그 밖 텍스트에만 fn을 적용한다."""
    return "".join(p if p.startswith("<") else fn(p) for p in re.split(r"(<[^>]+>)", h))


def link_cites(h, refs):
    """태그 밖 텍스트의 [n]은 출처 링크로, [A]·[B]·[C]는 등급 배지로."""
    def cites(t):
        t = re.sub(r"\[(\d+)\]", lambda m: f'<a class="cite" href="#ref-{m.group(1)}">[{m.group(1)}]</a>'
                   if m.group(1) in refs else m.group(0), t)
        return re.sub(r"\[([ABC](?:/[ABC])?)\]", r'<span class="grade">\1</span>', t)
    return outside_tags(h, cites)


def render_findings(items, refs):
    """KEY FINDINGS 카드 (ux-insight 형식: 주장·왜·그래서·근거·확신도·HMW·참고 아이디어).
    문자열 목록이면 주장만 표시한다."""
    out = []
    for i, f in enumerate(items, 1):
        if isinstance(f, str):
            f = {"claim": f}
        rows = "".join(f"<dt>{k}</dt><dd>{link_cites(inline_md(f[key]), refs)}</dd>"
                       for k, key in (("왜", "why"), ("그래서", "so_what")) if f.get(key))
        ev = "".join(f"<li>{link_cites(inline_md(e), refs)}</li>" for e in f.get("evidence") or [])
        conf = (f'<p class="conf">확신도 <b>{esc(f["confidence"])}</b><span>{esc(f.get("confidence_reason", ""))}</span></p>'
                if f.get("confidence") else "")
        hmw = f.get("hmw") or {}
        if isinstance(hmw, str):
            hmw = {"question": hmw}
        ideas = hmw.get("ideas") or {}
        idea_html = ""
        if ideas:
            pairs = [("기능", ideas.get("feature")), ("전략", ideas.get("strategy"))]
            idea_html = ('<details class="ideas"><summary>참고 아이디어 (검증 전)</summary><dl>'
                         + "".join(f"<dt>{k}</dt><dd>{esc(v)}</dd>" for k, v in pairs if v) + "</dl></details>")
        hmw_html = (f'<div class="hmw"><span class="hmw-label">How Might We</span>'
                    f'<p class="hmw-q">{esc(hmw["question"])}</p>{idea_html}</div>' if hmw.get("question") else "")
        rows_html = f'<dl class="finding-rows">{rows}</dl>' if rows else ""
        ev_html = f'<ul class="evidence">{ev}</ul>' if ev else ""
        out.append(f'<li class="finding"><p class="point-num">POINT {i:02d}</p><div>'
                   f'<p class="finding-claim">{inline_md(f["claim"])}</p>{rows_html}{ev_html}{conf}{hmw_html}</div></li>')
    return f'<ol class="findings">{"".join(out)}</ol>'


def render_limits(limits, method):
    """교차검증 섹션 끝: 조사 한계(무엇·왜·읽는 법·다음 단계)와 방법 박스."""
    h = ""
    if limits:
        names = (("무엇", "what"), ("왜", "why"), ("읽는 법", "read_as"), ("다음 단계", "next"))
        items = "".join("<li><dl>" + "".join(f"<dt>{k}</dt><dd>{esc(l[key])}</dd>" for k, key in names if l.get(key))
                        + "</dl></li>" for l in limits)
        h += f'<h3>조사 한계</h3><ul class="limits">{items}</ul>'
    if method:
        rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in method.items())
        h += f'<h3>방법</h3><div class="table-wrap"><table><tbody>{rows}</tbody></table></div>'
    return h


def render_body(md, base, refs):
    h = pandoc(md)
    # 그림: SVG를 파일 안에 넣는다
    def figure(m):
        src, alt = m.group(1), html.unescape(m.group(2))
        path = base / src
        if not path.exists():
            raise SystemExit(f"그림 파일 없음: {path}")
        svg = re.sub(r"<\?xml[^>]*>\s*", "", path.read_text(encoding="utf-8")).strip()
        return f'<figure class="fig">{svg}<figcaption>{esc(alt)}</figcaption></figure>'
    h = re.sub(r'<p><img src="([^"]+\.svg)" alt="([^"]*)" ?/?></p>', figure, h)
    h = re.sub(r'<figure>\s*<img src="([^"]+\.svg)" alt="([^"]*)" ?/?>\s*(?:<figcaption>.*?</figcaption>)?\s*</figure>', figure, h, flags=re.S)
    # 인용 → INSIGHT
    h = h.replace("<blockquote>", '<aside class="insight"><span class="insight-label">INSIGHT</span>').replace("</blockquote>", "</aside>")
    # 표 감싸기 (좁은 화면에서 표 안에서만 가로 스크롤)
    h = h.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    # 상세 펼치기: 첫 소제목을 요약 줄로
    def detail(m):
        inner = m.group(1).strip()
        hm = re.match(r'<h3[^>]*>(.*?)</h3>\s*', inner, re.S)
        label, inner = (hm.group(1), inner[hm.end():]) if hm else ("세부 근거", inner)
        return (f'<details class="detail"><summary><span class="chip">상세</span>{label}</summary>'
                f'<div class="detail-body">{inner}</div></details>')
    h = re.sub(r"<!-- detail -->(.*?)<!-- /detail -->", detail, h, flags=re.S)
    return link_cites(h, refs)


def parse_refs(text):
    refs = {}
    for line in text.splitlines():
        m = re.match(r"^\s*(\d+)\.\s*(.*)$", line)
        if m:
            entry = m.group(2).strip()
            u = re.search(r"(https?://\S+)\s*$", entry)
            title = entry[:u.start()].rstrip(", ").strip() if u else entry
            refs[m.group(1)] = (re.sub(r"\*\*(.+?)\*\*", r"\1", title), u.group(1) if u else "")
    return refs


def render_refs(refs):
    items = []
    for n, (title, url) in refs.items():
        link = f'<a class="ref-url" href="{esc(url)}" rel="noopener">{esc(url)}</a>' if url else ""
        items.append(f'<li id="ref-{n}"><span class="ref-num">{n}</span><span><span class="ref-title">{esc(title)}</span>{link}</span></li>')
    return f'<ol class="refs">{"".join(items)}</ol>'


def font_faces(text):
    """Pretendard에서 쓴 글자만 추려 woff2 base64로 넣는다. 서체가 없으면 시스템 대체."""
    try:
        from fontTools import subset
    except ImportError:
        print("경고: fontTools 없음 → 서체 내장 생략", file=sys.stderr)
        return ""
    dirs = [Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts", Path("C:/Windows/Fonts"),
            Path.home() / "Library/Fonts", Path("/usr/share/fonts")]
    chars = set(text) | set(chr(c) for c in range(0x20, 0x7f)) | set("·—–…“”‘’→×○●")
    out = []
    for weight, name in FONT_WEIGHTS.items():
        path = next((d / name for d in dirs if (d / name).exists()), None)
        if not path:
            print(f"경고: {name} 없음 → 이 굵기는 시스템 대체", file=sys.stderr)
            continue
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        font = subset.load_font(str(path), opts)
        s = subset.Subsetter(opts)
        s.populate(text="".join(chars))
        s.subset(font)
        buf = io.BytesIO()
        subset.save_font(font, buf, opts)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        out.append(f'@font-face {{ font-family: "Pretendard"; font-weight: {weight}; font-style: normal; '
                   f'font-display: swap; src: url(data:font/woff2;base64,{b64}) format("woff2"); }}')
    return "\n".join(out)


def build(md_path, out_path):
    md = md_path.read_text(encoding="utf-8")
    front, body = split_front(md)
    parts = split_sections(body)
    refs = parse_refs(parts.get("sources", ("", ""))[1])
    heads = front.get("sections") or {}
    counts = front.get("counts") or {}

    nav, index, secs = [], [], []
    # 핵심 발견 (확장)
    if front.get("key_findings"):
        secs.append('<section class="sec" id="findings"><header class="sec-head"><p class="eyebrow">KEY FINDINGS</p>'
                    f'<h2>핵심 발견</h2></header>{render_findings(front["key_findings"], refs)}</section>')
    num = 0
    for key, _, label, ko in SECTIONS:
        if key not in parts:
            continue
        num += 1
        title, text = parts[key]
        # 섹션 제목 구분: '## MARKET: 시장과 사용자 행동' (콜론). 옛 형식 '—'도 읽는다
        parts_t = re.split(r"\s*[:—]\s*", title, maxsplit=1)
        sub = parts_t[1].strip() if len(parts_t) == 2 and parts_t[1].strip() else ko
        h = heads.get(key) or {}
        headline = inline_md(h["headline"]) if h.get("headline") else esc(sub)
        lead = f'<p class="lead">{inline_md(h["lead"])}</p>' if h.get("lead") else ""
        extra = render_limits(front.get("limits"), front.get("method")) if key == "crosscheck" else ""
        content = (render_refs(refs) if key == "sources"
                   else f'<div class="prose">{render_body(text, md_path.parent, refs)}{extra}</div>')
        secs.append(f'<section class="sec" id="{key}"><header class="sec-head">'
                    f'<p class="eyebrow"><span>{num:02d}</span><span>{label}</span><span class="eyebrow-ko">{esc(sub)}</span></p>'
                    f'<h2>{headline}</h2>{lead}</header>{content}</section>')
        nav.append(f'<li><a href="#{key}">{label}</a></li>')
        index.append(f'<li><a href="#{key}"><span class="index-num">{num:02d}</span>'
                     f'<span class="index-name">{label}</span><span class="index-ko">{esc(sub)}</span></a></li>')

    detail = [("실행일", front.get("run_date")), ("조사 범위", front.get("scope")),
              ("소스", ", ".join(front.get("sources_used") or []))]
    stat_names = [("confirmed", "확정"), ("held", "보류"), ("discarded", "폐기"), ("hypotheses", "가설")]
    stats = "".join(f'<div class="{"is-key" if k == "confirmed" else ""}"><dt>{n}</dt><dd>{esc(counts[k])}</dd></div>'
                    for k, n in stat_names if k in counts)
    cover = front.get("cover") or {}
    title = cover.get("question") or front.get("title") or "데스크 리서치"
    subtitle = cover.get("subtitle") or front.get("topic", "")
    answer = f'<p class="cover-answer">{inline_md(cover["answer"])}</p>' if cover.get("answer") else ""
    fill = {
        "title": esc(title),
        "answer": answer,
        "short_title": esc(front.get("short_title") or title),
        "topic": esc(subtitle),
        "detail": "".join(f"<dt>{k}</dt><dd>{esc(v)}</dd>" for k, v in detail if v),
        "tags": "".join(f"<li>{esc(t)}</li>" for t in front.get("tags") or []),
        "stats": stats,
        "nav": "".join(nav),
        "index": "".join(index),
        "sections": "\n".join(secs),
        "footer": esc(f"{title}. {front.get('run_date', '')} 딥리서치 하네스로 생성. "
                      "본문 수치는 교차검증에서 확정 판정된 사실만 사용했습니다."),
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    for k, v in fill.items():
        page = page.replace("{{" + k + "}}", str(v))
    text_only = html.unescape(re.sub(r"<[^>]+>", " ", page))
    page = page.replace("{{font_faces}}", font_faces(text_only))
    out_path.write_text(page, encoding="utf-8")
    return out_path


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--out")
    a = ap.parse_args()
    md = Path(a.md)
    out = Path(a.out) if a.out else md.with_suffix(".html")
    build(md, out)
    print(f"생성: {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    load_rules()
    sys.exit(main())
