"""판정 회귀 검증 (docs/verification.md).

    python harness/verify.py --fixtures

harness/tests/fixtures/의 F*(실패 예시)는 판정 대상 문장이 전부 실패여야 하고(놓침 0),
P*(통과 예시)는 실패가 하나도 없어야 한다(잘못된 실패 0). Jev는 매번 실제로 호출한다.
종료 코드: 0 둘 다 0개 / 1 하나라도 있음 / 2 오류
"""
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "judge"))

from common import HARNESS, HarnessError, exit_code, load_rules, read_json, utf8_stdout  # noqa: E402
from run import jev_stage, load_sources, script_stage  # noqa: E402

FIXTURES = HARNESS / "tests" / "fixtures"


def reason_of(u):
    if u["script"]:
        return ", ".join(f["reason"] for f in u["script"])
    parts = []
    for c in u.get("claims", []):
        if "score" in c:
            parts.append(f"{c['verdict']} {c['score']:.2f} (뒷받침 {c['supports']:.2f}, 도메인 {c['domain']})")
        else:
            parts.append(f"{c['verdict']} " + ", ".join(f["reason"] for f in c["script"]))
    return " / ".join(parts)


def run_case(d, rules):
    case = read_json(d / "case.json")
    as_of = date.fromisoformat(case["as_of"])
    sources = load_sources(d, case["sources"])
    res = script_stage(case["report"], sources, as_of, rules)
    if not res["units"] and not case.get("heading_only"):
        raise HarnessError(f"{d.name}: 판정할 문장이 없음 (빈 fixture는 통과로 세지 않는다)")
    res = jev_stage(res, case["claims"], sources, rules)
    expect = case["expect"]
    # 실패 예시에서 오류인 문장. 없으면 전 문장. 원문이 뒷받침하는 사실 문장은 실패를 요구하지 않는다.
    error_units = set(case.get("error_units", [u["index"] for u in res["units"]]))
    lines, bad = [], 0
    if res["heading_fails"]:
        lines.append(f"    제목  fail  forbidden_heading: {[h['heading'] for h in res['heading_fails']]}")
    for u in res["units"]:
        if expect == "fail":
            ok = u["verdict"] == "fail" or u["index"] not in error_units or case.get("heading_only")
        else:
            ok = u["verdict"] != "fail"
        bad += not ok
        mark = "  " if ok else "✗ "
        tag = "" if expect != "fail" or u["index"] in error_units else "  (오류 문장 아님)"
        lines.append(f"  {mark}문장{u['index']}  {u['verdict']:<4}  {reason_of(u)}{tag}")
    if expect == "fail" and case.get("heading_only"):
        bad = 0 if res["heading_fails"] else 1
    return case, bad, lines


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", action="store_true", required=True)
    ap.add_argument("--only", help="예: F01,P03")
    args = ap.parse_args()
    rules = load_rules()
    dirs = sorted(p for p in FIXTURES.iterdir() if (p / "case.json").exists())
    if args.only:
        want = set(args.only.split(","))
        dirs = [d for d in dirs if d.name in want]
    if not dirs:
        print("오류: fixtures 없음", file=sys.stderr)
        return exit_code("error", rules)
    missed = wrong = 0
    print(f"Jev 상한 {rules['jev']['upper']} / 하한 {rules['jev']['lower']}\n")
    try:
        for d in dirs:
            case, bad, lines = run_case(d, rules)
            kind = "실패 예시" if case["expect"] == "fail" else "통과 예시"
            print(f"[{d.name}] {kind} — {case['title']}  {'OK' if not bad else f'✗ {bad}건'}")
            print("\n".join(lines))
            if case["expect"] == "fail":
                missed += bad
            else:
                wrong += bad
    except HarnessError as e:
        print(f"\n오류: {e}", file=sys.stderr)
        return exit_code("error", rules)
    print(f"\n놓침 {missed}건 / 잘못된 실패 {wrong}건")
    return exit_code("pass" if missed == 0 and wrong == 0 else "fail", rules)


if __name__ == "__main__":
    sys.exit(main())
