"""Jev 호출 전용 (docs/roles.md: Jev는 judge만, 이 파일로만 호출).

OpenRouter Decisions API (POST /api/alpha/decisions). 호출 실패는 HarnessError로
올려 종료 코드 2로 멈춘다. 실패를 통과로 바꾸지 않는다 (docs/gates.md).
키는 환경변수로만 읽는다.
"""
import json
import os
import re
import urllib.error
import urllib.request

from common import ROOT, HarnessError, load_engines

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

SUPPORTS = {
    "type": "noul",
    "instructions": "Does the source text support the claim exactly as stated: same entity, "
                    "same number, same time, and same scope?",
    "criteria": {
        "true": "The source states the claim, or states facts that directly establish it.",
        "false": "The source does not state the claim, states something different, "
                 "or only states a related but different fact.",
    },
}

DOMAIN = {
    "type": "choice",
    "instructions": "Compare what the source's evidence is about with what the claim is about. "
                    "Which describes the source?",
    "criteria": {
        "same": "The source is about the same industry, service type, and population as the claim.",
        "broader": "The source is about a broader category (for example all leisure activities "
                   "or all industries) and is not specific to the claim's subject.",
        "other": "The source is about a different industry, service type, channel, or population "
                 "than the claim's subject.",
    },
}


def excerpt(source, claim, budget):
    """원문이 길면 주장 수치·핵심어가 있는 문단 앞뒤만 남긴다 (rules.yaml jev.long_source)."""
    if len(source) <= budget:
        return source
    paras = [p for p in re.split(r"\n\s*\n|\n", source) if p.strip()]
    nums = re.findall(r"\d+(?:\.\d+)?", claim)
    words = [w for w in re.findall(r"[가-힣A-Za-z]{2,}", claim)]
    scores = []
    for i, p in enumerate(paras):
        s = sum(3 for n in nums if n in p) + sum(1 for w in words if w in p)
        scores.append((s, i))
    keep = set()
    for s, i in sorted(scores, reverse=True):
        if s == 0:
            break
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(paras):
                keep.add(j)
        if sum(len(paras[k]) for k in keep) >= budget:
            break
    picked, total = [], 0
    for k in sorted(keep):
        if total + len(paras[k]) > budget:
            break
        picked.append(paras[k])
        total += len(paras[k])
    return "\n".join(picked) if picked else source[:budget]


def decide(state, questions):
    cfg = load_engines()["judge"]["jev"]
    key = os.environ.get(cfg["key_env"])
    if not key:
        raise HarnessError(f"{cfg['key_env']} 환경변수 없음")
    body = json.dumps({"model": cfg["model"], "state": state, "questions": questions}).encode()
    req = urllib.request.Request(cfg["endpoint"], data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise HarnessError(f"Jev 호출 실패 HTTP {e.code}") from None
    except Exception as e:
        raise HarnessError(f"Jev 호출 실패 {type(e).__name__}") from None
    answers = data.get("answers") or {}
    if set(answers) != set(questions):
        raise HarnessError("Jev 응답에 답이 빠짐")
    return answers, data.get("usage", {})


def judge_claim(claim, source_text, rules, url=None, title=None):
    """주장 하나: 뒷받침(Noul)과 도메인(Choice). 점수는 둘 중 낮은 값.

    URL·제목도 함께 보낸다. 상품 페이지는 플랫폼 이름이 도메인에만 있는 경우가 많다.
    """
    jr = rules["jev"]
    state = {"claim": claim, "source_url": url, "source_title": title,
             "source": excerpt(source_text, claim, jr["excerpt_chars"])}
    answers, usage = decide(state, {"supports": SUPPORTS, "domain": DOMAIN})
    supports = float(answers["supports"]["noul"])
    same = float(answers["domain"]["probabilities"].get("same", 0))
    score = min(supports, same)
    if score >= jr["upper"]:
        verdict = "pass"
    elif score < jr["lower"]:
        verdict = "fail"
    else:
        verdict = "hold"
    return {
        "verdict": verdict,
        "score": round(score, 3),
        "supports": supports,
        "domain": answers["domain"]["choice"],
        "domain_probabilities": answers["domain"]["probabilities"],
        "cost": usage.get("cost"),
    }
