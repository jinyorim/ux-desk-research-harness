# 사용자 리서치·인사이트·보고서 작성 실무 정리 (research-practice)

> 조사일 2026-10-11. UX 기획, 서비스 기획, 마케팅에서 사용자 리서치와 인사이트를 다루는 최신 문서를 모아, 하네스 스킬 규칙의 근거로 정리했다.
> 세 갈래로 조사했다: A. UX 인사이트 작성 / B. 마케팅·기획의 소비자 인사이트와 데스크 리서치 / C. AI 리서치 검증과 발표용 문장.
> 이 문서를 근거로 쓰는 스킬: `.claude/skills/ux-insight/`(S4 analyst), `.claude/skills/report-writing/`(S5 publisher).
> 표시: (검증) 원문 직접 확인 / (요약) 검색 요약만 확인. 요약은 각 출처를 우리말로 다시 쓴 것이고 원문 인용은 짧은 어구만.

## 1. 출처

### A. UX 인사이트 작성

| # | 출처 | 날짜 | 핵심 |
| --- | --- | --- | --- |
| A1 | NN/g, Data vs. Findings vs. Insights (검증) https://www.nngroup.com/articles/data-findings-insights-differences/ | 2023-04-23 | 데이터 → 발견(패턴, 맥락 없음) → 인사이트(발견을 사용자 니즈·목표와 연결한 설명). 인사이트는 해법을 정하지 않고 가능성을 좁힌다. 통계적 한계를 문장 안에 넣은 예시 |
| A2 | Smashing Magazine, Data Vs. Findings Vs. Insights In UX (검증) https://smashingmagazine.com/2025/05/data-vs-findings-vs-insights-ux/ | 2025-05-27 | What happened + Why + So what. 본문 예시 수치가 데이터와 안 맞음(반면교사) |
| A3 | NN/g, Secondary Research in UX (검증) https://www.nngroup.com/articles/secondary-research-in-ux/ | 2022-02-20 | 데스크 리서치 4단계(문제 진술 → 자료 식별 → 편향·한계 평가 → 공백 정리). 방법론 없는 연구는 위험 신호. 다른 집단 결과는 가설로만. 2차 자료는 1차 리서치를 대체하지 못함 |
| A4 | NN/g, Using "How Might We" Questions (검증) https://www.nngroup.com/articles/how-might-we-questions/ | 2021-01-17, 2026-08-07 재검토 | HMW는 인사이트 하나에서 출발. 해법이 숨은 질문, 증상만 겨냥한 질문, 부정형 동사, 너무 넓은 질문을 피함 |
| A5 | dscout People Nerds, Writing User Insights (검증) https://dscout.com/people-nerds/writing-user-insights | 2026-06-01 재게재 | 1인칭 템플릿(역할·하려는 것·장벽·원인·감정). 단기 사용성 문제는 인사이트가 아니라 발견. 가정을 바꾸는 것이 인사이트 |
| A6 | Lyssna, User research insights (검증) https://www.lyssna.com/blog/user-research-insights | 2026-01-26 | "because/suggests" 같은 해석어가 없으면 데이터일 뿐. 일관된 출처 3개 > 상충 출처 10개. 신뢰도별로 묶어 보고. 행동 제안까지 문장에 넣는 형식(다른 출처와 이견) |
| A7 | Lyssna, UX insights (검증) https://lyssna.com/blog/ux-insights | 2023-10-05 | 한 프로젝트 3~5개. 발표 땐 인사이트 먼저, 근거 뒤 |
| A8 | IDEO.org Design Kit, Create Insight Statements (검증) https://www.designkit.org/methods/create-insight-statements.html | 날짜 없음(정본) | 테마를 해법 없는 한 문장으로. 3~5개. 외부인 반응으로 검증 후 HMW로 |
| A9 | Koji docs, Writing Insight Statements (검증, 벤더) https://www.koji.so/docs/writing-insight-statements | 2026-10-01 | Tension 형식(사용자·목표·장벽·원인·함의). 근거 1건이면 "signal". 관찰에 인사이트 라벨 붙이기·1건 일반화·해법 넣기가 흔한 실수 |
| A10 | UXPin, Desk Research in UX (검증) https://www.uxpin.com/studio/?p=48502 | 2026-06-03 | 출처 신뢰 순위, 발견마다 신뢰도 기록, 독립 보고서 3개가 같은 문제면 강한 신호 |
| A11 | GitLab Handbook, Research insights (검증) https://handbook.gitlab.com/handbook/product/ux/ux-research/research-insights | 상시 | 실행 항목은 모호한 동사(consider/maybe) 금지 |
| A12 | Atomic UX Research 해설, Prototypr (검증) https://blog.prototypr.io/what-is-atomic-research-e5d9fbc1285c | 2차 해설 | Experiments → Facts → Insights → Recommendations. 모든 인사이트는 사실로 거슬러 추적 가능해야 함 |
| A13 | 토스피드, 우리는 사용자를 믿지 않는다 (검증) https://toss.im/tossfeed/article/how-to-understand-users | 2021-08-24 | 말보다 행동. 데이터는 무엇, 리서치는 왜. 처음 가설("몰라서")과 실제 원인("소득이 불규칙해서")이 달랐던 사례 |
| A14 | 오픈서베이, UXR 퀵상담소 인사이트 얻기 (검증) https://blog.opensurvey.co.kr/event/uxr-quick-qna-6/ | 2023-06-21 | 여러 사람이 교차 해석해 과대 해석을 걸러냄. 결과가 가설과 다르면 인정. 권고는 데이터가 받칠 때만 구체적으로 |
| A15 | inspireX, 잘 이해되는 UX 리서치 보고서 (검증) https://maily.so/inspirex/posts/g0zm85j7oql | 2025-01-15 | 인사이트 = 영향이 크고 해결 가능한 발견. 3~5개, 각각 한 문장 |

### B. 마케팅·기획의 소비자 인사이트와 데스크 리서치

| # | 출처 | 날짜 | 핵심 |
| --- | --- | --- | --- |
| B1 | HBR, Know Your Customers' "Jobs to Be Done" (요약) https://www.innosight.com/?p=19201 | 2016-09 | 분석 단위는 "특정 상황에서 이루려는 진전". 기능·사회·감정 차원 |
| B2 | HES-SO 마케팅 교육 자료, Truth·Motivation·Tension (요약) | 날짜 미상 | 인사이트 3층: 드러난 진실 / 숨은 동기 / 풀리지 않은 긴장. 교육용 모델 |
| B3 | WARC Awards 2025 Strategist viewpoints (요약, 유료) https://www.warc.com/newsandopinion/opinion/warc-awards-2025-strategist-viewpoints-lessons-in-bravery-insights-and-proving-impact/7038 | 2025 | 좋은 인사이트는 놀랍지만 돌아보면 필연적인 이유 |
| B4 | Adobe Blog, 5 Cardinal Rules of Good Insight (요약, 오래됨) | 2017 | 업계 상식은 인사이트가 아님. 설문 문구를 그대로 옮긴 것도 아님 |
| B5 | Babson FME 가이드 외, Hierarchy of Sources (요약) https://libguides.babson.edu/FME/secondaryresearch | 2024~2026 | 1·2·3차 구분은 원자료와의 거리일 뿐, 신뢰도는 별도 축. 빠른 시장일수록 2차 자료가 빨리 낡음 |
| B6 | Slideworks, How to Write Action Titles Like McKinsey (검증) https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey | 2023-09-20 | 제목은 주제가 아니라 결론. 15단어 이하, 두 줄 이내, 수치로 구체적으로, 과정이 아니라 발견 |
| B7 | CleverX, How to Write a UX Research Report (검증) https://cleverx.com/blog/how-to-write-a-ux-research-report/ | 2026-06-18 | 관찰과 해석을 소제목으로 분리. "대부분" 대신 "12명 중 9명". 요약은 마지막에 쓰고 맨 앞에 둠 |
| B8 | 브런치 Maven, 인사이트는 결과를 의미로 바꾸는 과정 (검증) https://brunch.co.kr/@maven/507 | 2026-06-12 | "높다·낮다·많다"는 관찰. 인사이트는 "그래서 무엇을 의미하는가" |
| B9 | 캐릿(대학내일), 2023 상반기 유행템 총정리 (검증) https://www.careet.net/1113 | 2023-06-30 | 한 달 이상 지속된 것만. 정량 지표 + 자문단 정성 검증 |
| B10 | 대학내일20대연구소 보도자료 (요약) https://www.newswire.co.kr/newsRead.php?no=897138 | 2018~2020 | 조어형 트렌드 키워드 헤드라인이 마케팅 관행. 근거·방법은 드러나지 않음 |
| B11 | 패스트캠퍼스, 직장인 보고서 작성법 (검증) https://fastcampus.co.kr/story_article_bsk | 날짜 미상 | 용건 → 이유 → 근거의 두괄식. 6~7개 항목은 3~4개로 묶음. "보는 글" |
| B12 | 표시광고법 '업계 최다' 제재 해설 (요약) https://cheongchul.com/blog/업계최다-업계유일-광고-표시광고법-거짓과장-과징금 | 2026-08~09 | 최상급 표현은 비교 기준과 근거가 있어야 함 |

### C. AI 리서치 검증과 발표용 문장

| # | 출처 | 날짜 | 핵심 |
| --- | --- | --- | --- |
| C1 | NN/g, Synthetic Users (검증) https://www.nngroup.com/articles/synthetic-users/ | 2024-06-21 | AI 결과는 데스크 리서치·가설 생성까지. 실제 행동·우선순위·최종 결정에는 쓰지 않음. 모든 합성 결과는 가설 |
| C2 | NN/g, Evaluating AI-Simulated Behavior (검증) https://www.nngroup.com/articles/ai-simulations-studies/ | 2025-08-15 | 방향은 맞아도 크기·분산이 다름. 새 질문 정확도 낮음 |
| C3 | NN/g, Accelerating Research with AI (검증) https://www.nngroup.com/articles/research-with-ai/ | 2024-09-27, 2026-01 재검토 | AI는 출발점이지 최종 출처가 아님. 1차 출처를 요구하고 사람이 확인. 해석과 인사이트는 사람 몫 |
| C4 | NN/g, GenAI for Complex Questions, Search for Critical Facts (검증) https://www.nngroup.com/articles/ai-search-infoseeking/ | 2026-02-27 | 출처 링크가 있어도 어느 주장이 어느 출처인지, 어디가 인용 없는 종합인지 구분하기 어려움 |
| C5 | Salesforce AI Research, DeepTRACE (검증) https://arxiv.org/html/2509.04499v1 | 2025-09 | 딥리서치 9종 인용 정확도 약 40~80%. 근거 없는 진술 비율 Gemini DR 53.6%, GPT-5 DR 12.5%. 출처 수가 많다고 근거가 탄탄한 것은 아님 |
| C6 | CJR Tow Center, AI Search Has a Citation Problem (검증) https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php | 2025-03-06 | AI 검색 8종, 60% 이상 출처 오류. 딥리서치 모드 평가는 아님 |
| C7 | 디지털마케터, ChatGPT 딥 리서치 인용 확인하기 (검증) https://www.digitalmarketer.co.kr/class/chatgpt-astra-in-practice/chatgpt-deep-research | 2026-10-01 | 결론에 쓰일 주장부터 원문 대조. 확인 못 한 값은 "미확인"으로 근거에서 뺌 |
| C8 | NN/g, Creating Engaging Reports (검증) https://www.nngroup.com/articles/engaging-reports-presentations/ | 2022-04-03 | 3층: 헤드라인(결정자) / 큰 주제 / 방법·세부. 헤드라인만 읽어도 이해. 일화는 데이터를 뒷받침만 |
| C9 | GetYourGuide, UX researcher 커뮤니케이션 (검증) https://www.getyourguide.careers/posts/3-tips-for-improving-your-communication-skills-as-a-ux-researcher | 2022-01-24 | 답을 맨 앞에. 요약은 1분 안에. 핵심 인사이트 3개 |
| C10 | Duarte, The Big Idea (검증) https://www.duarte.com/?p=19986 | 날짜 없음 | 발표 전체를 한 문장으로. 누군가 반대할 수 있어야 주제가 아니라 주장 |
| C11 | Barbara Minto, Pyramid Principle / SCQ (요약) https://barbaraminto.com/ | — | 상황 → 복잡화 → 질문 → 답 |
| C12 | Deckary, McKinsey-Style Slides (검증, 업체 블로그) https://deckary.com/blog/mckinsey-style-slides | 2026-08-09 | 제목만 이어 읽어도 이해되는지(가로 흐름 테스트) |
| C13 | GoTranscript, Present Qual Findings Without Overclaiming (검증) https://gotranscript.com/en/blog/present-qualitative-findings-without-overclaiming-confidence-limitations-guide | 2026-03-06 | 관찰·해석·권고 분리. 문장마다 단서 대신 테마별 확신도 + 이유. 한계는 무엇·왜·왜곡·읽는 법·다음 단계로 |
| C14 | 브런치 @note2026, 보고서가 반려된 이유 (검증) https://brunch.co.kr/@note2026/68 | 2026-07-06 | 결재자는 첫 줄만 읽음. 첫 줄에 결론과 수치 |

확인하지 못한 것: Kantar·Ipsos·Mintel의 공식 인사이트 정의 페이지, Dovetail·Maze·UserTesting의 공식 작성·검증 가이드, 국내 대형 IT 기업(당근·배민·카카오)의 인사이트 문장 작성 글.

## 2. 종합: 스킬에 넣은 규칙과 근거

| 규칙 | 근거 | 들어간 스킬 |
| --- | --- | --- |
| 인사이트 = 무엇(패턴) + 왜(긴장) + 그래서(함의). 해석어 없으면 발견에 머묾 | A1, A2, A6, A9, B2, B8 | ux-insight |
| 해법은 인사이트에 넣지 않고 HMW 질문으로 넘김. HMW는 긍정형, 해법·증상 겨냥 금지 | A1, A4, A8, A9 | ux-insight |
| 모든 인사이트는 확정 사실 ID로 추적 가능 | A12, C4 | ux-insight |
| 확신도(높음/중간/낮음 + 이유)는 문장 밖에 따로. 헤드라인은 단정적으로 | A6, C13 | ux-insight |
| 데스크 리서치 인사이트는 1차 리서치로 검증할 가설이라는 위치를 밝힘 | A3, C1, C2 | ux-insight |
| 핵심 발견 3개 (최대 5) | A7, A8, A15, C9 | ux-insight |
| 표지: 질문형 제목 + 답 한 줄(결론) + 부제(범위·대상·방법·시점) | C10, C11, B6 | ux-insight |
| 헤드라인은 주제 라벨이 아니라 결론 문장, 2줄 이내. 헤드라인만 이어 읽어도 이야기가 됨 | B6, C8, C12 | ux-insight, report-writing |
| 결론 먼저(요약을 맨 앞), 1분 안에 읽힘 | B7, B11, C9, C14 | report-writing |
| 관찰(출처 확인된 사실)과 해석(연구자 해석)을 보이게 구분 | B7, C4, C13 | report-writing |
| "대부분" 대신 구체 수치, 최상급은 비교 기준·출처 있을 때만 | B7, B12, research-rules 0-4 | report-writing |
| 한계는 무엇·왜·읽는 법·다음 단계로, 끝의 짧은 칸에 모음 | C13 | ux-insight(limits), report-writing |
| 방법 박스: 사용 엔진·실행일·검증 방식·미확인 수 공개 | C1, C5, C7 | report-writing |
| AI 결과는 출발점. 인사이트·가설은 사람 승인 | C1, C3 | ux-insight(승인 절차) |
| 다른 집단·업종 결과는 근거가 아니라 가설 | A3, research-rules 0-2 | ux-insight |
| 조어형 트렌드 단어를 단독 제목으로 쓰지 않음 (마케팅 관행과 다름) | B10과 A14·UX 쪽 대비 | ux-insight |

## 3. 출처 간 이견과 이 하네스의 선택

- **인사이트에 행동 제안을 넣을지**: Lyssna·Smashing은 넣고, NN/g·IDEO·Koji는 뺀다. → 빼고 "그래서(기회 영역)"와 HMW를 별도 칸으로 (제언 섹션 금지 규칙과도 맞음).
- **1인칭 vs 3인칭**: dscout는 1인칭, Koji·Lyssna는 3인칭. → 발표용 3인칭.
- **헤드라인 단정 수준**: 컨설팅은 수치로 단정, 오픈서베이는 데이터가 받칠 때만 구체적으로. → 헤드라인은 단정, 확신도는 칸으로 따로.
- **"출처 3개" 기준**: 실무 관행일 뿐 표준 아님(NN/g는 타당성·대상 적합성 중시). → 하네스의 확정 판정 기준(두 엔진 일치 + 원문 확인 + A/B 등급)을 그대로 쓰고, 확신도는 그 위에 얹는다.
