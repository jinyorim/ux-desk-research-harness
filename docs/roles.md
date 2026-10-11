# 역할 (roles)

> 에이전트마다 맡는 단계와 쓸 수 있는 범위, API 키 보호 규칙이다.

## 에이전트와 편집 범위 (에이전트마다 편집 범위 1곳)

| 에이전트 | 단계 | 편집 가능 | 읽기만 |
| --- | --- | --- | --- |
| orchestrator | 전체 | `runs/<slug>/state.json` | 전부 |
| interviewer | S1 | `runs/<slug>/s1_*` | docs/ |
| (검사자 역할) | | `runs/<slug>/reviews/<단계>/` | docs/review.md 2번 표: researcher→S1, judge→S2, S4, S5, analyst→S5, 감사자(다른 모델)→S3, S5 |
| researcher | S2 | `runs/<slug>/s2_*` (엔진 호출, UI Bowl, 원문 저장) | s1_brief.md |
| judge | S3 | `runs/<slug>/s3_*` (판정 결과만 씀) | s2_* 전체 (수정 불가) |
| analyst | S4 (인사이트 항상, WHY AI와 가설 조건부) | `runs/<slug>/s4_*` | s3_crosscheck.md |
| publisher | S5 | `runs/<slug>/s5_*` | s3_*, s4_*, harness/rules.yaml visual |

- `harness/`와 `docs/`는 실행 중 어떤 에이전트도 수정하지 않는다. 수정은 사람만 한다.

## 판정자

- 판정 스크립트(`harness/judge/`)가 먼저 실행되고, judge 에이전트는 그 결과를 읽어 정리만 한다.
- Jev 호출 코드는 `harness/judge/jev.py` 한 곳에만 둔다. 다른 에이전트는 실행 권한이 없다 (docs/gates.md).

## API 키 보호

- 키는 로컬 `.env`에만 둔다. `.env`는 GitHub에 절대 올리지 않는다 (`.gitignore`).
- GitHub에는 키 값이 비어 있는 상태로 올린다: 키 이름만 있고 값은 빈 `.env.example`.
- `.claude/settings.json`에서 `.env` 읽기를 차단한다 (Read, cat, type, Get-Content 등).
- 스크립트는 환경변수로만 키를 받는다.
- 첫 커밋과 매 푸시 전 `git status`에 `.env`가 없는지 확인한다. 키가 한 번이라도 커밋되면 삭제가 아니라 재발급한다.

## 자연어 트리거

| 말 | 동작 |
| --- | --- |
| 리서치 시작: <주제 한 문장> | S1부터 시작 |
| 이어서 | state.json에서 재개 |
| 다시 판정 | S3만 재실행 |
| 보고서 만들어 | S5만 실행 (S3 통과 상태일 때만) |
