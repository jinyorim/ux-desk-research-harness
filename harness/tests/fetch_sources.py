"""fixtures 원문을 Exa /contents로 한 번 받아 고정한다 (docs/verification.md).

    python harness/tests/fetch_sources.py            # file이 없는 출처만 받기
    python harness/tests/fetch_sources.py --refresh  # 전부 다시 받기

case.json의 sources[n]에 url이 있고 file이 없으면 받아서 source_<n>.md로 저장하고
status·published·fetched를 채운다. 실패한 URL은 status에 실패 사유를 남긴다
(판정에서는 source_unreachable). 키는 환경변수로만 읽는다.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "judge"))

from common import HARNESS, ROOT, read_json, utf8_stdout, write_json  # noqa: E402

FIXTURES = HARNESS / "tests" / "fixtures"


def fetch(urls):
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    key = os.environ.get("EXA_API_KEY")
    if not key:
        raise SystemExit("EXA_API_KEY 환경변수 없음")
    body = json.dumps({"urls": urls, "text": True, "livecrawlTimeout": 15000}).encode()
    req = urllib.request.Request("https://api.exa.ai/contents", data=body, headers={
        "x-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    todo = {}
    for d in sorted(FIXTURES.iterdir()):
        if not (d / "case.json").exists():
            continue
        case = read_json(d / "case.json")
        for n, s in case["sources"].items():
            if s.get("url") and (args.refresh or not s.get("file")):
                todo.setdefault(s["url"], []).append((d, n))
    if not todo:
        print("받을 원문 없음")
        return 0

    data = fetch(list(todo))
    results = {r["url"]: r for r in data.get("results", [])}
    statuses = {s["id"]: s for s in data.get("statuses", [])}
    cost = (data.get("costDollars") or {}).get("total")
    today = date.today().isoformat()

    for url, targets in todo.items():
        st = statuses.get(url, {})
        res = results.get(url) or next((r for r in results.values() if r.get("id") == url), None)
        ok = st.get("status") == "success" and res and res.get("text")
        for d, n in targets:
            path = d / "case.json"
            case = read_json(path)
            s = case["sources"][n]
            s["fetched"] = today
            if ok:
                (d / f"source_{n}.md").write_text(res["text"], encoding="utf-8")
                s["file"] = f"source_{n}.md"
                s["status"] = 200
                s["published"] = (res.get("publishedDate") or "")[:10] or None
                s["title"] = res.get("title")
            else:
                err = st.get("error") or {}
                s["file"] = None
                s["status"] = err.get("httpStatusCode") or err.get("tag") or "error"
            write_json(path, case)
        print(f"{'성공' if ok else '실패'}  {url[:90]}" + ("" if ok else f"  ({statuses.get(url, {}).get('error')})"))
    print(f"\n{len(todo)}개 URL, 비용 ${cost}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
