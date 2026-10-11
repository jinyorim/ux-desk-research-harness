# 교차 검사 (review)

> 여러 에이전트가 서로의 과업을 정확히 수행했는지 검사하는 규칙이다.
> 요약: 단계별 교차 검사 / 판정자는 다른 모델로 표본 재판정 / 지적은 전부 되돌림(최대 3회) / 단계별 기록 파일과 장부.
> 근거: GitHub 인기 스킬 조사(obra/superpowers의 subagent-driven-development와 verification-before-completion, anthropics/skills의 skill-creator grader, codex-plugin-cc와 adversarial-review의 다른 모델 리뷰, 199-biotechnologies 딥리서치의 claims/evidence 구조). 출처 목록은 docs/skills-inventory.md.
> 수치는 harness/rules.yaml review, 감사 모델은 harness/engines.yaml review.

## 1. 원칙

1. **작업자와 검사자를 나눈다.** 자기 결과물을 자기가 통과시키지 않는다. 자기 점검표는 보조일 뿐이다.
2. **검사자는 결과물, 규칙 문서, 원문만 본다.** 작업자의 보고(무엇을 했다는 설명)는 근거로 쓰지 않는다.
3. **스크립트 검사를 먼저 돌린다.** 기계로 셀 수 있는 것은 스크립트가 판정한다. 스크립트가 실패하면 모델 검사는 하지 않는다.
4. **통과에도 증거를 남긴다.** 지적이든 통과든 근거 위치(파일, 문장 번호, 원문 인용)를 기록한다.
5. **같은 모델이 자기를 채점하지 않는다.** S3 판정(Jev)은 다른 회사 모델(감사자)이 라벨을 가린 채 다시 판정한다.
6. **지적은 전부 되돌린다.** 심각도(C 치명, I 중요, M 사소)는 기록하지만 셋 다 고친다. 같은 단계를 되돌리는 횟수는 최대 3회다.

## 2. 누가 누구를 검사하나

| 대상 (작업자) | 스크립트 검사 (먼저) | 모델 검사 (검사자) | 기록 |
| --- | --- | --- | --- |
| S1 브리프 (interviewer) | 브리프 필수 칸, 세부 작업(M1~G3) 선택과 이유 | researcher: 이 브리프로 실제 조사가 되는가 (모호한 질문, 빠진 범위, 엔진이 답할 수 없는 질문). 그다음 사람 승인 | reviews/s1/ |
| S2 조사 결과 (researcher) | `run.py --stage script` (출처 번호, 접속, 숫자와 인용 원문 대조, 기준일, 금지 제목) | judge: 주장 분해 후 Jev 판정 (`run.py --stage jev`). "없다" 주장은 문자열 검사 | s3_* (기존 S3) |
| S3 판정 (judge, Jev) | 판정 파일 형식, 모든 문장이 판정됐는지 | 감사자(다른 모델): `audit.py --target s3`. 보류와 실패 전부, 통과 20% 표본. 근거 인용을 원문에서 확인. Jev와 반대면 사람 확인 목록 | reviews/s3/ |
| S4 인사이트와 분석 (analyst) | `check_korean.py`, ux-insight 점검표의 기계 항목, 근거 사실 ID가 확정 사실에 있는지, 분석 표의 칸마다 주장 ID가 있는지 | judge: 주장, 왜, 그래서가 근거 사실에서 바로 나오는가 (새 정보, 과장, 다른 업종 근거). 감사자: 빠진 경쟁사나 다른 해석이 있는지 반대 입장에서 검토 | reviews/s4/ |
| S5 보고서 (publisher) | `check_korean.py`, `check_html.py`, `run.py --target s5 --stage script` (출처 있는 문장의 숫자 대조, 출처 없는 숫자 실패) | judge: 출처 있는 문장을 주장으로 쪼개 Jev (`--target s5 --stage jev`). 감사자: `audit.py --target s5`. analyst: 표지, 인사이트, 헤드라인이 승인본과 같고 본문이 인사이트를 왜곡하지 않는가 | reviews/s5/ |

- 검사자는 읽기 전용이다. 자기 기록 폴더(reviews/<단계>/)에만 쓴다.
- 오케스트레이터(메인 세션)는 검사 결과를 보고 되돌리거나 다음 단계로 넘긴다. 직접 판정하지 않는다.

## 3. 기록 형식

`runs/<slug>/reviews/<단계>/round<N>.json` (감사자는 `audit_round<N>.json`)

```json
{
  "stage": "s4", "reviewer": "judge", "model": "claude (구독)", "round": 1,
  "created": "2026-10-11T15:00:00",
  "verdict": "approved | needs_fixes | needs_human",
  "summary": {"checked": 12, "findings": 2},
  "findings": [
    {"id": "s4-1", "severity": "I", "check": "model", "location": "K2.why",
     "evidence": "s3_crosscheck.md F07: '두 리포트 모두 국내 미확인'", "passed": false,
     "note": "why가 근거 사실에 없는 '사용자 불편'을 덧붙임"}
  ]
}
```

- 통과 항목도 findings에 `passed: true`와 evidence를 남긴다.
- 모든 기록은 `runs/<slug>/reviews/ledger.jsonl`에 한 줄씩 쌓인다. 기록과 장부 추가는 `python harness/judge/record_review.py <slug> <기록 파일>`로 한다 (형식 검사 포함).

## 4. 되돌리기와 종료 코드

| 검사 결과 | 종료 코드 | 다음 행동 |
| --- | --- | --- |
| approved | 0 | 다음 단계 |
| needs_fixes | 1 | 지적 전부를 작업자에게 되돌림. 1~2회차는 같은 작업자, 3회차는 새 컨텍스트로. 재검사는 고친 부분과 그 영향 범위 |
| needs_human | 1 | 사람 확인 목록. 사람의 판단을 기록하고 진행 |
| 3회 초과, 앞 단계 결함(예: S4 문제가 S2 근거 부족 때문), 스크립트 오류 | 2 | 멈추고 앞 단계로 되돌리거나 사람에게 넘김 |

## 5. 비용과 지연을 줄이는 장치

- 스크립트 실패 시 모델 검사 생략.
- 감사자는 전수가 아니라 표본(통과 20%)과 보류, 실패만.
- 재검사는 고친 부분만.

## 6. 실제로 잡아낸 것 (원데이클래스 조사 샘플, 2026-10-11)

- S2 스크립트 판정과 S5 검사로 샘플의 실제 오류 4건(붙인 출처에 없는 "2~6주", "원데이클래스 전문" 과장, Google Play 출처 오기, 프립 "아웃도어와 소셜" 출처 없음)을 찾았다.
- 감사자(gpt-6-sol)가 Jev 오판 2건(원문에 그대로 있는 "30만개 이상 리뷰", "필터 탭 6개")을 근거 인용과 함께 잡았다.
- 해석을 사실 문장으로 쓴 1건(진입로 기준 묶기)이 사람 확인 목록에 올랐다.
