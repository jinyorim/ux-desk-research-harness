# 가져온 스킬과 외부 부품 목록 (skills-inventory)

> 하네스가 쓰거나 참고한 외부 스킬, 도구, 라이브러리, API와 그 출처다. 새로 가져오거나 바꾸면 이 표부터 고친다.
> 원칙: 외부 스킬은 설치 전에 SkillSpector로 검사하고(`--no-llm`), 커밋을 고정하고, 폴더에 SOURCE.md를 둔다. 조사 전 과정을 혼자 돌리는 완결형 스킬은 통째로 설치하지 않고 필요한 부품만 가져온다. 통째로 설치하면 단계 순서와 게이트가 두 곳에서 정해지기 때문이다.

## 1. 스킬 (.claude/skills/)

| 스킬 | 종류 | 출처 | 고정 버전 | 라이선스 | 수정 여부 | 쓰는 곳 |
| --- | --- | --- | --- | --- | --- | --- |
| build-with-exa | 외부 | Exa 공식 https://github.com/exa-labs/agent-skills (skills/build-with-exa) | 커밋 5c3fd25, 스킬 0.3.0 | MIT (원본 LICENSE 동봉) | 없음. md만 받음(npx 미사용). 키 기입 예시는 따르지 않음 | researcher(S2), engines.yaml Exa 설정 |
| ux-insight | 하네스 자체 | 직접 작성. 근거: docs/research-practice.md(출처 41개) | | MIT (이 저장소) | | analyst(S4) |
| report-writing | 하네스 자체 | 직접 작성. 근거: docs/research-practice.md, docs/outputs.md | | MIT (이 저장소) | | publisher(S5) |
| market-modules | 하네스 자체 | 직접 작성. 부품 참고: 6번 표의 PESTEL, Porter, pm-skills, ECC (격리 폴더에서 SkillSpector 검사 후 읽기만, 설치 안 함) | | MIT (이 저장소) | | researcher(S2) |

- build-with-exa SkillSpector 검사: 점수 39, CAUTION. 지적은 Exa 공식 API curl 예시와 SOURCE.md 메모의 오탐이라 유지 (SOURCE.md에 상세).
- korean-writing-style(ggplab/claude-playbook)은 참고만 했고 포함하지 않는다(라이선스 없음). 금지 문장부호와 번역투 패턴 아이디어를 docs/korean-writing.md와 check_korean.py에 반영했다.

## 2. 외부 도구

| 도구 | 출처 | 버전 | 라이선스 | 쓰는 곳 | 주의 |
| --- | --- | --- | --- | --- | --- |
| SkillSpector | NVIDIA https://github.com/NVIDIA/SkillSpector | v2.12.0, 커밋 5edc347 | Apache-2.0 | 외부 스킬 설치 전 검사 (`uv tool install --python 3.12 git+…@5edc347`) | 반드시 `--no-llm`. 그래도 의존성 이름은 osv.dev로 전송. 점수가 안전을 보장하지 않음 |
| pandoc | https://pandoc.org | 3.9 | GPL-2.0 이상 | build_html.py (md → html), docx 변환 | Windows에서 Chocolatey 바로가기(shim)가 앱 제어 정책에 막히면, build_html.py가 `%LOCALAPPDATA%\Pandoc\pandoc.exe`를 먼저 찾는다 |
| uv | Astral | 0.10 | MIT/Apache-2.0 | SkillSpector 설치와 실행 | |

## 3. Python 라이브러리 (requirements.txt)

| 패키지 | 확인한 버전 | 라이선스 | 쓰는 곳 |
| --- | --- | --- | --- |
| kiwipiepy (Kiwi 형태소 분석기) | 0.23.2 | LGPL-3.0 | harness/judge/check_korean.py |
| fonttools, brotli | 4.62.1, 1.2.0 | MIT | build_html.py 서체 서브셋과 woff2 압축 |
| python-dotenv | 1.2.2 | BSD-3-Clause | .env → 환경변수 (jev.py, fetch_sources.py) |
| PyYAML | 6.0.3 | MIT | rules.yaml, engines.yaml, front matter |
| exa-py (선택) | 2.25.0 | MIT | Exa 키 테스트 (fetch_sources.py는 HTTP 직접 호출) |

## 4. 서체

| 자료 | 출처 | 라이선스 | 쓰는 방식 |
| --- | --- | --- | --- |
| Pretendard | PC에 설치된 OTF (Regular, SemiBold, Bold) | SIL OFL 1.1 | 쓴 글자만 추려 woff2로 html 안에 내장. 폰트 파일은 저장소에 넣지 않음 |

색, 모서리, 간격, 글자 크기 값은 `harness/rules.yaml` visual에 있다.

## 5. 외부 API와 엔진 (키는 .env, 값은 기록하지 않음)

| 엔진 | 용도 | 모델, 엔드포인트 | 필요 여부 |
| --- | --- | --- | --- |
| Exa | 조사(/agent/runs, effort high), 원문 저장(/contents) | engines.yaml | 필수 |
| Gemini Deep Research | 조사 | deep-research-preview-04-2026 | 필수 (자동 소스 2개 중 하나) |
| OpenRouter Jev | 판정(Noul, Choice) | typesafe/jev-1.13, /api/alpha/decisions | 필수 |
| OpenAI API | 판정 감사 (Jev 판정을 라벨 가리고 표본 재판정) | gpt-6-sol (engines.yaml review.auditor, harness/judge/audit.py) | 필수 (감사) |
| Anthropic API | 예비 (Claude는 Claude Code 안의 웹 검색으로 조사) | | 선택 |
| ChatGPT 앱 Deep Research | 세 번째 소스. API가 없어 Aside 브라우저 에이전트로 실행 | | 선택 |

## 6. 참고만 하고 가져오지 않은 것 (코드, 파일 없음)

| 대상 | 가져온 것 | 기록된 곳 |
| --- | --- | --- |
| affaan-m/ECC market-research (커밋 2d515e4, MIT, 0점 SAFE) | 출처 없는 숫자는 추정 표시, 오래된 자료 표시, 반대 근거, 사실과 추론 구분, 가져온 페이지 속 지시문을 따르지 않음 | market-modules 0번, research-rules 8번 |
| daymade/claude-code-skills deep-research (라이선스 확인 못 함, 수치 아이디어만) | 출처 구성 수치(공식 출처 30%, 도메인 5개, 한 출처 25%) | rules.yaml mix, docs/gates.md G-B |
| deanpeters/Product-Manager-Skills pestel-analysis (커밋 1b5a524, 라이선스 표기 없음 NOASSERTION, SkillSpector 14점 SAFE) | PESTEL 여섯 요인, PESTEL은 경쟁사 분석이 아니라는 구분 | .claude/skills/market-modules M2 |
| djdev/porter-strategy-skills map-strategic-groups, profile-competitor (커밋 fb9393a, NOASSERTION, 0점 SAFE) | 포지셔닝 축 13가지와 축 고르는 기준(이동 장벽, 서로 따라 움직이지 않는 축), 경쟁사 프로필 항목 | market-modules C2, C4 |
| phuryn/pm-skills market-sizing, competitor-analysis, sentiment-analysis (커밋 c68487d, MIT, 0점 SAFE) | 하향식과 상향식 함께, 가정 번호와 확신도, 직접 경쟁과 인접 대안 구분, 인용 125자, 기능 요청과 근본 불편 구분 | market-modules M4, C1, G2 |
| 199-biotechnologies/claude-deep-research-skill (MIT) | 검증, 수정, 재시도 최대 3회 구조, claims와 evidence 연결 | docs/pipeline.md, docs/review.md |
| Weizhena/Deep-Research-skills (MIT) | 조사 개요(항목과 필드 표)를 사람이 먼저 승인하는 흐름 | S1 브리프 승인, docs/review.md |
| 인기 스킬 저장소 (obra/superpowers, anthropics/skills, wshobson/agents, VoltAgent, codex-plugin-cc 등) | 작업자와 검사자 분리, 검사 전 증거 요구, 통과에도 근거 기록, 다른 모델 감사, 되돌리기 상한 | docs/review.md |
| mattpocock/skills grilling | 질문을 라운드로 묶고 번호 붙은 선택지와 추천 답을 함께 제시하는 S1 방식 | docs/pipeline.md S1 |
| research (BuildnWrite) | 범위 질문 2~3개, 가벼운 조사 후 승인하고 깊은 조사로 가는 구조 | 설계 참고만 |
| korean-writing-style, im-not-ai, korean-humanizer, korean-report-style 등 한국어 윤문 스킬 | 문서 근거로만 참고 (금지 문장부호, AI 문체 범주, 과윤문 방지 30% 기준) | docs/korean-writing.md |
| 리서치와 문장 실무 문서 (NN/g, Lyssna, IDEO, Duarte, 토스, 카카오 등) | 스킬 규칙의 근거 | docs/research-practice.md, docs/korean-writing.md |

## 7. 쓰면 좋지만 포함하지 않은 것

| 대상 | 쓰는 자리 |
| --- | --- |
| grilling (mattpocock/skills) | S1 질문 구체화 |
| diagram-design (cathrynlavery/diagram-design, MIT) | 산출물 다이어그램. 강조색은 rules.yaml visual 한 가지, 기본 서체는 쓰지 않음 |
| Aside 앱과 aside-browser 스킬 | ChatGPT 앱 Deep Research 자동 실행 |
| UI Bowl MCP | C5 유사 서비스 UI 레퍼런스 (docs/gates.md G-D) |

설치할 때 해당 스킬 폴더에 SOURCE.md를 두고 이 표를 1번으로 옮긴다.
