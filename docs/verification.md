# 판정 회귀 검사 (verification)

판정 규칙(`harness/rules.yaml`)이나 판정 스크립트(`harness/judge/`)를 바꿀 때마다, 이미 답을 아는 사례로 판정이 그대로 맞는지 확인한다.

## 실행

```bash
python harness/verify.py --fixtures            # 전부
python harness/verify.py --fixtures --only EX-F1,EX-P1
```

- 실패 예시(`F`가 붙은 사례)는 모든 오류 문장이 실패로 판정돼야 한다. 놓침 0건.
- 통과 예시(`P`가 붙은 사례)는 실패가 하나도 없어야 한다. 잘못된 실패 0건.
- 둘 다 0건이면 종료 코드 0. 0이 아니면 그 변경은 쓰지 않는다.
- 통과 예시는 Jev를 실제로 호출하므로 `.env`에 `OPENROUTER_API_KEY`가 있어야 한다. 스크립트 단계에서 실패하는 문장은 Jev에 보내지 않는다.

## 들어 있는 사례

`harness/tests/fixtures/EX-*`는 형식을 보여 주는 가상 사례다. 서비스와 원문은 지어낸 것이고 URL은 예시 도메인이다.

| 사례 | 문장 | 걸리는 게이트 |
| --- | --- | --- |
| EX-F1 | 2022년 수수료를 현재 요율처럼 씀 | G-A 기준일 (`stale_without_label`) |
| EX-F2 | 원문에 없는 호스트 수 | G-A 원문 불일치 수치 (`number_not_in_source`) |
| EX-F3 | "전략적 제언" 섹션 | G-A 금지 섹션 (`forbidden_heading`) |
| EX-P1 | 원문과 일치하는 호스트 수 | 통과 (Jev 뒷받침) |

## 내 사례 추가하기

실제 조사에서 나온 오류를 사례로 남기면 같은 오류가 다시 통과하지 않는다.

1. `harness/tests/fixtures/<ID>/case.json`을 만든다. ID는 실패 예시면 `F`, 통과 예시면 `P`로 시작하게 짓는다.
2. 원문은 직접 넣거나(`file`) URL만 적고 받는다.

```bash
python harness/tests/fetch_sources.py            # file이 없는 출처만 Exa로 받아 source_<n>.md로 저장
python harness/tests/fetch_sources.py --refresh  # 전부 다시 받기
```

`case.json` 형식:

| 키 | 뜻 |
| --- | --- |
| `id`, `title` | 사례 이름 |
| `expect` | `fail` 또는 `pass` |
| `gate` | 걸려야 하는 게이트 (설명용) |
| `as_of` | 기준일. 기준일 판정이 이 날짜로 계산된다 |
| `report` | 판정할 보고서 조각. 본문 문장 끝에 `[n]`, 끝에 `## 참고자료` 목록 |
| `sources` | 번호별 출처. `url`, `file`, `published`(게시일, 모르면 null), `title` |
| `claims` | 문장(`unit`, 0부터)마다 쪼갠 주장과 출처 번호. Jev가 이 주장을 원문과 대조한다 |
| `error_units` | (선택) 실패 예시에서 실패해야 하는 문장 번호. 없으면 전 문장 |
| `heading_only` | (선택) 제목만으로 실패해야 하는 사례 |

## Jev 상한과 하한

통과 0.85 이상, 실패 0.5 미만, 그 사이는 보류다 (`rules.yaml` jev). 사례를 늘리면 실패 예시와 통과 예시를 동시에 만족하는지 보고 조정한다.
