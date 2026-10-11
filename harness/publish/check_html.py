"""G-E 산출물 게이트 중 html 파일만 보고 셀 수 있는 항목 (docs/gates.md G-E).

    python harness/publish/check_html.py runs/<slug>/s5_report.html

- 허용 밖 색 0 (CSS, SVG 속성. rules.yaml visual.colors_allowed)
- 외부 리소스 로드 0 (<link>, <script src>, http(s) src, url(http), @import)
- 그림자·애니메이션 0
- 모서리: html은 radius_allowed, 다이어그램(SVG rx)은 radius_diagram_max 이하
- 간격(margin·padding·gap): spacing_html, 글자 크기: type_sizes_html/display, SVG 글자: type_sizes_diagram
- 단계별 다이어그램 1개 이상 (MARKET, COMPETITORS, SOLUTION GAP), 추가 다이어그램 extra_max 이하
모바일 가로 스크롤은 브라우저에서 확인한다 (이 스크립트 범위 밖).
종료 코드: 0 통과 / 1 실패 / 2 오류
"""
import re
from html import unescape as html_unescape
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "judge"))
from common import exit_code, load_rules, utf8_stdout  # noqa: E402

BASIC_FIGURES = 5          # docs/outputs.md 기본 5종
STAGE_SECTIONS = ["market", "competitors", "solution-gap"]


def px_values(value):
    return [float(v) for v in re.findall(r"(-?\d+(?:\.\d+)?)px", value)]


def check(page, rules):
    v = rules["visual"]
    allowed_colors = {c.lower() for c in v["colors_allowed"]}
    fails = []
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", page, re.S))
    styles = re.sub(r"url\(data:[^)]*\)", "url(data:)", styles)
    css = re.sub(r"/\*.*?\*/", "", styles, flags=re.S)
    svgs = re.findall(r"<svg\b.*?</svg>", page, re.S)

    # 색
    found = set(re.findall(r"#[0-9a-fA-F]{3,8}\b", css))
    for svg in svgs:
        found |= set(re.findall(r'(?:fill|stroke|stop-color|color)="(#[0-9a-fA-F]{3,8})"', svg))
    found |= set(re.findall(r'style="[^"]*?(#[0-9a-fA-F]{3,8})', page))
    for c in sorted(found):
        if c.lower() not in allowed_colors:
            fails.append(f"허용 밖 색 {c}")
    if re.search(r"\b(rgb|rgba|hsl|hsla)\(", css):
        fails.append("rgb()/hsl() 색 사용")

    # 외부 리소스
    for pat, what in [(r"<link\b", "<link>"), (r"<script[^>]+src=", "<script src>"),
                      (r'\ssrc="https?:', "외부 src"), (r"url\(\s*['\"]?https?:", "외부 url()"), (r"@import", "@import")]:
        if re.search(pat, page, re.I):
            fails.append(f"외부 리소스 로드: {what}")

    # 그림자·애니메이션
    if re.search(r"(box-shadow|text-shadow)\s*:\s*(?!none)", css) or "drop-shadow" in css:
        fails.append("그림자 사용")
    if re.search(r"\b(animation|transition)\s*:", css) or "@keyframes" in css:
        fails.append("애니메이션 사용")

    # 모서리
    for val in re.findall(r"border-radius\s*:\s*([^;}]+)", css):
        for n in px_values(val):
            if n != 0 and n not in v["radius_allowed"]:
                fails.append(f"허용 밖 모서리 {n:g}px")
    for svg in svgs:
        for n in re.findall(r'\brx="(\d+(?:\.\d+)?)"', svg):
            n = float(n)
            if n not in v["radius_allowed"] or n > v["radius_diagram_max"]:
                fails.append(f"다이어그램 허용 밖 모서리 rx={n:g}")

    # 간격
    # scroll-padding(고정 내비 아래로 앵커를 맞추는 값)은 여백이 아니라서 제외
    for prop, val in re.findall(r"(?<![\w-])((?:margin|padding)(?:-[a-z]+)?|gap|row-gap|column-gap)\s*:\s*([^;}]+)", css):
        for n in px_values(val):
            if n != 0 and n not in v["spacing_html"]:
                fails.append(f"허용 밖 간격 {prop} {n:g}px")

    # 글자 크기
    sizes = set(v["type_sizes_html"]) | set(v["type_sizes_display"])
    for val in re.findall(r"font-size\s*:\s*([^;}]+)", css):
        for n in px_values(val):
            if n not in sizes:
                fails.append(f"허용 밖 글자 크기 {n:g}px")
    for svg in svgs:
        for n in re.findall(r'font-size="(\d+(?:\.\d+)?)"', svg):
            if float(n) not in v["type_sizes_diagram"]:
                fails.append(f"다이어그램 허용 밖 글자 크기 {n}")
    if v["letter_spacing_html"] not in css:
        fails.append(f"자간 {v['letter_spacing_html']} 없음")

    # 화면에 보이는 글자의 금지 문장부호 (rules.yaml korean, docs/korean-writing.md)
    visible = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", page, flags=re.S)
    visible = html_unescape(re.sub(r"<[^>]+>", " ", visible))
    for ch in rules.get("korean", {}).get("forbidden_chars", []):
        hits = [m.start() for m in re.finditer(re.escape(ch), visible)]
        if ch == "–":
            hits = [i for i in hits if not (re.match(r"[0-9A-Za-z]", visible[i - 1:i] or " ")
                                            and re.match(r"[0-9A-Za-z]", visible[i + 1:i + 2] or " "))]
        if hits:
            sample = visible[max(0, hits[0] - 12):hits[0] + 12].replace("\n", " ")
            fails.append(f"금지 문장부호 U+{ord(ch):04X} {len(hits)}개 (예: …{sample}…)")

    # 다이어그램 수
    for key in STAGE_SECTIONS:
        m = re.search(rf'<section class="sec" id="{key}">(.*?)</section>', page, re.S)
        if m and v_count(m.group(1)) < rules["figures"]["per_stage_min"]:
            fails.append(f"{key} 섹션 다이어그램 {rules['figures']['per_stage_min']}개 미만")
    total = v_count(page)
    if total - BASIC_FIGURES > rules["figures"]["extra_max"]:
        fails.append(f"추가 다이어그램 {total - BASIC_FIGURES}개 > 상한 {rules['figures']['extra_max']}")
    return sorted(set(fails)), total


def v_count(h):
    return len(re.findall(r'<figure class="fig">', h))


def main():
    utf8_stdout()
    rules = load_rules()
    if len(sys.argv) != 2 or not Path(sys.argv[1]).exists():
        print("사용법: python harness/publish/check_html.py <html>", file=sys.stderr)
        return exit_code("error", rules)
    page = Path(sys.argv[1]).read_text(encoding="utf-8")
    fails, figs = check(page, rules)
    for f in fails:
        print("실패:", f)
    print(f"다이어그램 {figs}개 / G-E html 검사: {'실패 ' + str(len(fails)) + '건' if fails else '통과'}")
    return exit_code("fail" if fails else "pass", rules)


if __name__ == "__main__":
    sys.exit(main())
