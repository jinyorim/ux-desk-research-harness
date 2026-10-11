"""세부 작업 표 형식 검사 (.claude/skills/market-modules, docs/gates.md G-M).

    python harness/judge/check_modules.py runs/<slug>/s2_raw/<engine>/<section>.md

칸 내용이 원문과 맞는지는 S3(run.py, Jev, 감사)가 본다. 이 스크립트는 형식과 계산만 본다.
- M2 PESTEL: 여섯 요인 행, 사실 칸 출처 또는 '확인된 변화 없음', 해석 칸에 숫자 없음
- C2 SWOT: 강점, 약점, 기회, 위협 네 칸 출처, 제언 표현 없음
- C4 포지셔닝: 축1, 축2 정의, 값이 정의한 범위 안, 근거 칸 출처, 경쟁사 4개 이상
- M4 시장 규모: '계산:' 칸을 다시 계산해 값과 비교 (허용 오차 rules.yaml modules.calc_tolerance)
- G2 테마: 큰따옴표 인용 125자 이내
종료 코드: 0 통과 / 1 실패 / 2 오류
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import exit_code, load_rules, utf8_stdout  # noqa: E402

CITE = re.compile(r"\[\d+\]")
SUGGEST = re.compile(r"해야\s?한다|하면\s?좋|필요하다|제안|추천한다|전략은|차별화해야")
PESTEL = ["정치", "경제", "사회", "기술", "환경", "법"]
UNIT = {"만": 1e4, "억": 1e8, "조": 1e12}


def blocks(md):
    """'### <코드> …' 제목별 본문."""
    out, cur, buf = [], None, []
    for line in md.splitlines():
        m = re.match(r"^#{2,4}\s+([MCG]\d)\b(.*)$", line.strip())
        if m:
            if cur:
                out.append((cur[0], cur[1], buf))
            cur, buf = (m.group(1), m.group(2).strip()), []
        elif cur:
            buf.append(line)
    if cur:
        out.append((cur[0], cur[1], buf))
    return out


def table(lines):
    rows = [l.strip() for l in lines if l.strip().startswith("|")]
    rows = [r for r in rows if not re.fullmatch(r"\|[\s:|-]+\|?", r)]
    return [[c.strip() for c in r.strip("|").split("|")] for r in rows]


def num(text):
    """'1,200만', '3.5억', '20%' 같은 값을 수로. 못 읽으면 None."""
    m = re.search(r"(-?\d[\d,]*(?:\.\d+)?)\s*(만|억|조|%)?", text.replace(" ", ""))
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    u = m.group(2)
    return v / 100 if u == "%" else v * UNIT.get(u, 1)


def calc(expr, names):
    toks = re.split(r"\s*([×x*/+\-])\s*", expr.strip())
    vals, ops = [], []
    for t in toks:
        if t in ("×", "x", "*", "/", "+", "-"):
            ops.append("*" if t in ("×", "x") else t)
            continue
        v = names.get(t.strip()) if t.strip() in names else num(t)
        if v is None:
            return None
        vals.append(v)
    s = str(vals[0])
    for o, v in zip(ops, vals[1:]):
        s += o + str(v)
    try:
        return eval(s, {"__builtins__": {}})   # 숫자와 사칙연산만 남은 식
    except Exception:
        return None


def check(md, rules):
    fails = []
    for code, title, lines in blocks(md):
        t = table(lines)
        where = f"{code} {title}".strip()
        if code == "M2" and t:
            head, body = t[0], t[1:]
            names = [r[0] for r in body]
            for p in PESTEL:
                if not any(n.startswith(p) for n in names):
                    fails.append(f"{where}: PESTEL '{p}' 행 없음")
            interp = [i for i, h in enumerate(head) if "(해석)" in h]
            for r in body:
                if len(r) > 1 and not CITE.search(r[1]) and "확인된 변화 없음" not in r[1]:
                    fails.append(f"{where}: '{r[0]}' 사실 칸에 출처 없음")
                for i in interp:
                    if i < len(r) and re.search(r"\d", r[i]):
                        fails.append(f"{where}: '{r[0]}' 해석 칸에 숫자")
        if code == "C2":
            swot = {r[0]: r[1] for r in t if len(r) > 1 and r[0] in ("강점", "약점", "기회", "위협")}
            if t and set(swot) != {"강점", "약점", "기회", "위협"}:
                fails.append(f"{where}: SWOT 네 칸 중 빠진 칸 {sorted({'강점', '약점', '기회', '위협'} - set(swot))}")
            for k, v in swot.items():
                if not CITE.search(v) and "확인 안 됨" not in v:
                    fails.append(f"{where}: SWOT '{k}' 칸에 출처 없음")
                if SUGGEST.search(v):
                    fails.append(f"{where}: SWOT '{k}' 칸에 제언 표현 '{SUGGEST.search(v).group(0)}'")
        if code == "C4":
            axes = {}
            for l in lines:
                m = re.match(r"^\s*(축[12])\s*:\s*(.+?)\s*\(값:\s*(.+?)\)", l)
                if m:
                    axes[m.group(1)] = [v.strip() for v in re.split(r"[,/]", m.group(3)) if v.strip()]
            if set(axes) != {"축1", "축2"}:
                fails.append(f"{where}: 축1, 축2 정의 없음 (예: 축1: 가격 정책 (값: 낮음, 중간, 높음))")
            body = t[1:] if t else []
            if len(body) < rules["modules"]["positioning_min_competitors"]:
                fails.append(f"{where}: 경쟁사 {len(body)}개 < {rules['modules']['positioning_min_competitors']}개")
            for r in body:
                if len(r) < 5:
                    fails.append(f"{where}: '{r[0]}' 행의 칸 수 부족 (경쟁사, 축1 값, 근거, 축2 값, 근거)")
                    continue
                for vi, ci, ax in ((1, 2, "축1"), (3, 4, "축2")):
                    if axes.get(ax) and r[vi] not in axes[ax]:
                        fails.append(f"{where}: '{r[0]}' {ax} 값 '{r[vi]}'가 정의 밖 {axes[ax]}")
                    if not CITE.search(r[ci]):
                        fails.append(f"{where}: '{r[0]}' {ax} 근거에 출처 없음")
        if code == "M4" and t:
            names = {}
            for r in t[1:]:
                if len(r) >= 3:
                    key = re.sub(r"\s*\(.*\)", "", r[0]).strip()
                    v = num(r[1])
                    if v is not None:
                        names.setdefault(key, v)
                    m = re.search(r"계산:\s*(.+)", r[2])
                    if m and v is not None:
                        got = calc(m.group(1), names)
                        if got is None:
                            fails.append(f"{where}: '{r[0]}' 계산식을 읽지 못함: {m.group(1)}")
                        elif abs(got - v) > abs(v) * rules["modules"]["calc_tolerance"]:
                            fails.append(f"{where}: '{r[0]}' 값 {r[1]}와 계산 결과 {got:,.0f}이 다름")
        if code == "G2":
            for q in re.findall(r"[\"“]([^\"”]+)[\"”]", "\n".join(lines)):
                if len(q) > rules["modules"]["quote_max_chars"]:
                    fails.append(f"{where}: 인용 {len(q)}자 > {rules['modules']['quote_max_chars']}자")
    return fails


def main():
    utf8_stdout()
    rules = load_rules()
    if len(sys.argv) != 2 or not Path(sys.argv[1]).exists():
        print("사용법: python harness/judge/check_modules.py <md>", file=sys.stderr)
        return exit_code("error", rules)
    fails = check(Path(sys.argv[1]).read_text(encoding="utf-8"), rules)
    for f in fails:
        print("실패:", f)
    print(f"세부 작업 형식 검사: {'실패 ' + str(len(fails)) + '건' if fails else '통과'}")
    return exit_code("fail" if fails else "pass", rules)


if __name__ == "__main__":
    sys.exit(main())
