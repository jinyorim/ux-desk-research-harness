"""판정 스크립트 공용: 설정 로드와 종료 코드.

수치·목록은 harness/rules.yaml, 엔진 설정은 harness/engines.yaml에서만 읽는다.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "harness"


class HarnessError(Exception):
    """판정을 계속할 수 없는 오류. 종료 코드 2 (docs/orchestrator.md)."""


def load_yaml(name):
    with open(HARNESS / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_rules():
    return load_yaml("rules.yaml")


def load_engines():
    return load_yaml("engines.yaml")


def exit_code(name, rules=None):
    return (rules or load_rules())["exit_codes"][name]


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def utf8_stdout():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
