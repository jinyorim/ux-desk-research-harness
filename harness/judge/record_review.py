"""교차 검사 기록을 검사하고 장부에 올린다 (docs/review.md 3번, 4번).

    python harness/judge/record_review.py <slug> runs/<slug>/reviews/<단계>/round<N>.json

- 형식: stage, reviewer, model, round, verdict, findings[] (id, severity C/I/M, check script/model, location, evidence, passed)
- 통과 항목에도 evidence가 있어야 한다.
- 작업자와 검사자가 같으면 실패 (자기 채점 금지).
- round가 rules.yaml review.max_rounds를 넘으면 종료 코드 2.
종료 코드: 0 approved / 1 needs_fixes, needs_human / 2 형식 오류, 횟수 초과
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, exit_code, load_rules, read_json, utf8_stdout  # noqa: E402

WORKER = {"s1": "interviewer", "s2": "researcher", "s3": "judge", "s4": "analyst", "s5": "publisher"}
VERDICTS = {"approved", "needs_fixes", "needs_human"}


def validate(rec):
    errs = []
    for k in ("stage", "reviewer", "model", "round", "verdict", "findings"):
        if k not in rec:
            errs.append(f"{k} 없음")
    if errs:
        return errs
    if rec["stage"] not in WORKER:
        errs.append(f"알 수 없는 단계 {rec['stage']}")
    elif rec["reviewer"] == WORKER[rec["stage"]]:
        errs.append(f"자기 채점: {rec['stage']} 작업자 {rec['reviewer']}가 검사자")
    if rec["verdict"] not in VERDICTS:
        errs.append(f"verdict는 {sorted(VERDICTS)} 중 하나")
    for f in rec["findings"]:
        fid = f.get("id", "?")
        if f.get("severity") not in ("C", "I", "M"):
            errs.append(f"{fid}: severity는 C/I/M")
        if f.get("check") not in ("script", "model"):
            errs.append(f"{fid}: check는 script/model")
        if not f.get("location") or not f.get("evidence"):
            errs.append(f"{fid}: location과 evidence 필수 (통과 항목도)")
        if "passed" not in f:
            errs.append(f"{fid}: passed 없음")
    if rec["verdict"] == "approved" and any(not f.get("passed", True) for f in rec["findings"]):
        errs.append("통과하지 못한 지적이 있는데 approved")
    return errs


def main():
    utf8_stdout()
    rules = load_rules()
    if len(sys.argv) != 3:
        print("사용법: python harness/judge/record_review.py <slug> <기록 파일>", file=sys.stderr)
        return exit_code("error", rules)
    run = ROOT / "runs" / sys.argv[1]
    path = Path(sys.argv[2]).resolve()
    run = run.resolve()
    rec = read_json(path)
    errs = validate(rec)
    if errs:
        for e in errs:
            print("형식 오류:", e)
        return exit_code("error", rules)
    over = rec["round"] > rules["review"]["max_rounds"]
    with open(run / "reviews" / "ledger.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({k: rec[k] for k in ("stage", "reviewer", "model", "round", "verdict")}
                           | {"created": rec.get("created"), "file": str(path.relative_to(run)).replace("\\", "/"),
                              "open_findings": sum(not x["passed"] for x in rec["findings"])},
                           ensure_ascii=False) + "\n")
    print(f"{rec['stage']} {rec['round']}회차 {rec['reviewer']}: {rec['verdict']} → 장부 기록")
    if over:
        print(f"되돌리기 {rules['review']['max_rounds']}회 초과: 멈추고 사람에게 넘김")
        return exit_code("error", rules)
    return exit_code("pass" if rec["verdict"] == "approved" else "fail", rules)


if __name__ == "__main__":
    sys.exit(main())
