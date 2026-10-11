# 산출물 (outputs)

> 하네스가 만드는 파일과 형식이다. 내용의 원본은 md 하나이고, docx와 html은 거기서 만든다. 그래야 세 파일의 내용이 어긋나지 않는다.

## 고정 파일

- 규칙의 단일 출처: `harness/rules.yaml` (수치, 목록, 임계값은 이 파일 한 곳에만)
- 엔진 모델 ID: `harness/engines.yaml` 한 파일에만
- 재개 상태: `runs/<slug>/state.json`

## 실행 폴더 구조

```
runs/<slug>/                     slug 예: 2026-10-07-oneday-class
  state.json                     재개 상태
  s1_brief.md                    승인된 브리프
  s1_modules.md                  세부 작업 선택과 이유
  s2_raw/<engine>/market.md      엔진별 결과 (competitors.md, solution-gap.md 동일)
  s2_sources/                    원문 저장본 + sources.json (URL, 접속일, 기준일)
  s2_uibowl.md                   유사 서비스 UI (ui_url, MAU, 조회일)
  s3_verdicts.json               주장별 판정 (스크립트 결과, Jev 확률)
  s3_crosscheck.md               확정, 보류, 폐기 표
  s3_failures.json               재시도 대상과 횟수
  s4_insights.md                 표지, KEY FINDINGS, 헤드라인, 조사 한계 (항상, 사람 승인)
  s4_why-ai.md, s4_hypotheses.md (조건부)
  s5_report.md / .docx / .html   최종 3종 (md가 원본)
  s5_figures/                    다이어그램 svg, png
```

## 재개 (state.json)

- 단계 × 엔진 × 섹션 단위로 상태 기록 (예: gemini/competitors 완료, exa/solution-gap 진행 중).
- 끊기면 진행 중이던 항목부터 다시 시작.
- 재시도 횟수(최대 3)와 사람 승인 여부(S1 브리프, S4 인사이트, S4 가설)도 기록.

## html

웹사이트처럼 한 페이지를 위에서 아래로 스크롤하며 읽는 구조다. 탭으로 나누지 않는다.

| 순서 | 영역 | 내용 |
| --- | --- | --- |
| 1 | 상단 고정 내비게이션 | 섹션 목차. 누르면 해당 섹션으로 이동하고, 지금 읽는 섹션이 표시됨 |
| 2 | 첫 화면 요약 | 리서치 주제, 실행 날짜, 사용한 소스, 확정 사실 수, 최종 가설 수, 핵심 발견 3개 |
| 3 | MARKET | 본문 + 다이어그램 1개 이상 |
| 4 | COMPETITORS | 본문 + 다이어그램 1개 이상 |
| 4-1 | 유사 서비스 UI | 서비스별 핵심 화면 설명, UI Bowl 원본 링크(`ui_url`), MAU |
| 5 | SOLUTION GAP | 본문 + 다이어그램 1개 이상 |
| 6 | 교차검증 결과 | 확정, 보류, 폐기 건수와 목록. 폐기 항목은 "서베이에서 물을 질문"으로 연결 |
| 7 | WHY AI | 문제와 AI 강점 6분류 대응 (조건부) |
| 8 | HYPOTHESIS | 사람이 승인한 가설과 5원칙 체크 결과 (조건부) |
| 9 | 출처 | 번호별 출처 목록. 본문의 출처 번호를 누르면 이 목록으로 이동 |

- 한 파일. CSS와 SVG를 파일 안에 넣고, 외부 서버의 스크립트나 이미지를 불러오지 않는다.
- 휴대폰 폭에서도 가로 스크롤 없이 읽힌다.
- 색, 모서리, 간격, 글자 크기는 `harness/rules.yaml` visual 값만 쓴다. 그림자와 애니메이션은 쓰지 않는다.
- 서체: Pretendard, 자간 -2% (`letter-spacing: -0.02em`).

## 다이어그램

기본 (단계마다 1개 이상):

| 단계 | 유형 |
| --- | --- |
| MARKET | 타임라인 |
| COMPETITORS | 매트릭스 또는 사분면 |
| SOLUTION GAP | 사용자 여정 |
| 교차검증 | 막대 차트 |
| WHY AI | 매트릭스 (조건부) |

- 데이터에 따라 기본 외 다이어그램을 보고서 전체에서 최대 5개까지 추가할 수 있다.
- 워드에는 PNG로 넣는다 (워드 버전에 따라 SVG가 깨질 수 있다).

## docx

- 서체: 맑은 고딕.
- md 원본에서 변환 (pandoc 또는 python-docx).

## 분량과 상세 블록

- docx는 출처 목록을 뺀 본문이 8~12쪽(목표 10쪽). A4, 맑은 고딕 본문 10pt, 표 9pt, 제목 16/13pt 기준으로 잰다. 값은 `harness/rules.yaml` report.
- md 원본은 하나. 10쪽을 넘는 세부 근거는 md 안에서 `<!-- detail -->` … `<!-- /detail -->`로 감싼다. docx에서는 빠지고, html에서는 접어서(펼치기) 보여준다.
- html은 포트폴리오용. 섹션마다 영문 라벨 + 그 목차 내용을 한 문장으로 정리한 헤드라인(40~70자, 확정 사실만)을 두고, 문구는 md 앞부분(front matter) `sections`에 둔다. 한 줄 설명은 쓰지 않는다. 표지만 `#191f28` 배경과 큰 글자(rules.yaml visual type_sizes_display), 인용 블록은 INSIGHT 박스.
- 인사이트 카드: 주장, 왜, 그래서, 근거, 확신도, HMW. HMW 아래 '참고 아이디어(검증 전)' 기능 1개와 전략 1개는 html에서 접고 docx에서 뺀다. 표지는 질문, 답 한 줄, 부제로 짠다. 교차검증 섹션 끝에 조사 한계와 방법 박스 (report-writing 스킬).
