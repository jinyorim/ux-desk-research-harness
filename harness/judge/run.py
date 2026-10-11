"""S3 판정 진입점.

    python harness/judge/run.py <slug> --stage script   # 1단계: 스크립트 판정
    python harness/judge/run.py <slug> --stage jev      # 2단계: judge가 쓴 s3_claims.json을 Jev로

입력 (docs/outputs.md):
    runs/<slug>/s2_raw/<engine>/<section>.md
    runs/<slug>/s2_sources/sources.json   {"<engine>/<section>": {"n": {url, file, status, published}}}
    runs/<slug>/s3_claims.json            {"<engine>/<section>": [{unit, text, source}]}  (jev 단계)
출력: s3_script.json, s3_verdicts.json, s3_failures.json
종료 코드: 0 통과(보류 포함) / 1 실패 / 2 오류 (docs/orchestrator.md)
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks  # noqa: E402
import jev  # noqa: E402
from common import ROOT, HarnessError, exit_code, load_rules, read_json, utf8_stdout, write_json  # noqa: E402


def script_stage(report_md, sources, as_of, rules, mode="engine"):
    """리포트 하나의 스크립트 판정. mode="report"는 S5 보고서 검사 (checks.check_unit 참고)."""
    units, refs, headings = checks.parse_report(report_md, rules)
    for u in units:
        u["script"] = checks.check_unit(u, refs, sources, rules, as_of, mode)
    return {"units": units, "heading_fails": checks.check_headings(headings, rules)}


def jev_stage(script_result, claims, sources, rules):
    """스크립트를 통과한 문장의 주장만 Jev로. 문장별 최종 판정을 붙인다."""
    units = script_result["units"]
    by_unit = {}
    for c in claims:
        by_unit.setdefault(int(c["unit"]), []).append(c)
    for u in units:
        if u["script"]:
            u["verdict"] = "fail"
            continue
        if u.get("skip") or u.get("warn"):
            u["verdict"] = "skip" if u.get("skip") else "warn"
            continue
        cs = by_unit.get(u["index"])
        if not cs:
            raise HarnessError(f"문장 {u['index']}에 주장이 없음 (judge가 s3_claims.json을 채워야 함)")
        u["claims"] = []
        for c in cs:
            pre = checks.check_claim(c, u)
            if pre:
                u["claims"].append({**c, "verdict": "fail", "script": pre})
                continue
            src = sources[str(c["source"])]
            if c.get("absence"):
                u["claims"].append({**c, **absence_check(c, src["text"], rules)})
                continue
            res = jev.judge_claim(c["text"], src["text"], rules, src.get("url"), src.get("title"))
            u["claims"].append({**c, **res})
        vs = {c["verdict"] for c in u["claims"]}
        u["verdict"] = "fail" if "fail" in vs else "hold" if "hold" in vs else "pass"
    if script_result["heading_fails"]:
        script_result["verdict"] = "fail"
    else:
        vs = {u["verdict"] for u in units} - {"skip", "warn"}
        script_result["verdict"] = "fail" if "fail" in vs else "hold" if "hold" in vs else "pass"
    return script_result


def absence_check(claim, source_text, rules):
    """'없다' 주장: Jev 대신 원문에 해당 낱말이 있는지 문자열로 본다 (rules.yaml absence)."""
    terms = claim.get("absent_terms") or []
    if not terms:
        return {"verdict": "fail", "script": [{"reason": "absence_terms_missing"}]}
    flat = checks.squash(source_text).lower()
    found = [t for t in terms if checks.squash(t).lower() in flat]
    a = rules["absence"]
    if found:
        return {"verdict": a["verdict_if_found"], "absence_found": found}
    return {"verdict": a["verdict_if_absent"], "absence_found": []}


def load_sources(base, table):
    out = {}
    for n, s in (table or {}).items():
        s = dict(s)
        f = s.get("file")
        if f and (base / f).exists():
            s["text"] = (base / f).read_text(encoding="utf-8")
        out[str(n)] = s
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--stage", choices=["script", "jev"], required=True)
    ap.add_argument("--target", choices=["s2", "s5"], default="s2",
                    help="s2: 엔진 결과(S3 판정), s5: 최종 보고서 사실 검사(judge의 S5 교차 검사)")
    args = ap.parse_args()
    rules = load_rules()
    run = ROOT / "runs" / args.slug
    if args.target == "s5":
        return main_s5(run, args.stage, rules)
    try:
        reports = sorted((run / "s2_raw").glob("*/*.md"))
        if not reports:
            raise HarnessError("s2_raw에 리포트가 없음")
        src_base = run / "s2_sources"
        table = read_json(src_base / "sources.json")
        today = date.today()
        script = {}
        for p in reports:
            key = f"{p.parent.name}/{p.stem}"
            script[key] = script_stage(p.read_text(encoding="utf-8"),
                                       load_sources(src_base, table.get(key)), today, rules)
        if args.stage == "script":
            write_json(run / "s3_script.json", script)
            failed = any(r["heading_fails"] or any(u["script"] for u in r["units"]) for r in script.values())
            print(f"스크립트 판정: {'실패 있음' if failed else '전부 통과'} → s3_script.json")
            # 실패 문장은 재조사 대상. 통과 문장은 judge가 주장으로 쪼갠 뒤 jev 단계로 간다.
            return exit_code("fail" if failed else "pass", rules)

        claims = read_json(run / "s3_claims.json")
        verdicts, failures = {}, {}
        for key, res in script.items():
            verdicts[key] = jev_stage(res, claims.get(key, []), load_sources(src_base, table.get(key)), rules)
            bad = [u["index"] for u in res["units"] if u["verdict"] == "fail"]
            if bad or res["heading_fails"]:
                failures[key] = {"units": bad, "headings": res["heading_fails"]}
        write_json(run / "s3_verdicts.json", verdicts)
        write_json(run / "s3_failures.json", failures)
        print(f"판정: {'실패 ' + str(len(failures)) + '개 리포트' if failures else '통과(보류 포함)'}")
        return exit_code("fail" if failures else "pass", rules)
    except HarnessError as e:
        print(f"오류: {e}", file=sys.stderr)
        return exit_code("error", rules)


def s5_sources(run, report_md):
    """S5 보고서의 출처 번호를 S2 원문 저장본에 잇는다 (URL 또는 observation: 경로로 찾음)."""
    src_base = run / "s2_sources"
    table = read_json(src_base / "sources.json")
    by_key = {}
    for entries in table.values():
        for e in entries.values():
            if e.get("url"):
                by_key[e["url"].rstrip("/")] = e
            if e.get("file"):
                by_key["observation:" + e["file"]] = e
    _, refs, _ = checks.parse_report(report_md, load_rules())
    out = {}
    for n, entry in refs.items():
        u = checks.URL.search(entry)
        o = checks.OBSERVATION.search(entry)
        key = u.group(0).rstrip("/") if u else (re.sub(r"\s+", "", o.group(0)) if o else None)
        out[n] = dict(by_key.get(key, {})) if key else {}
    return load_sources(src_base, out)


def main_s5(run, stage, rules):
    """judge가 publisher의 S5 보고서를 검사한다. 결과는 reviews/s5/에 (docs/review.md)."""
    try:
        md = (run / "s5_report.md").read_text(encoding="utf-8")
        md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
        sources = s5_sources(run, md)
        res = script_stage(md, sources, date.today(), rules, mode="report")
        out = run / "reviews" / "s5"
        if stage == "script":
            write_json(out / "script.json", res)
            bad = [u for u in res["units"] if u["script"]]
            warn = [u for u in res["units"] if u.get("warn")]
            print(f"S5 스크립트 검사: 실패 {len(bad)}문장, 출처 없는 문장(경고) {len(warn)} → reviews/s5/script.json")
            return exit_code("fail" if bad or res["heading_fails"] else "pass", rules)
        claims = read_json(out / "claims.json")
        res = jev_stage(res, claims, sources, rules)
        write_json(out / "verdicts.json", res)
        print(f"S5 판정: {res['verdict']} → reviews/s5/verdicts.json")
        return exit_code("fail" if res["verdict"] == "fail" else "pass", rules)
    except HarnessError as e:
        print(f"오류: {e}", file=sys.stderr)
        return exit_code("error", rules)


if __name__ == "__main__":
    sys.exit(main())
