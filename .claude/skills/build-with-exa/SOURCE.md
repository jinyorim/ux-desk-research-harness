# 출처 기록

- 저장소: https://github.com/exa-labs/agent-skills (MIT)
- 경로: skills/build-with-exa
- 커밋: 5c3fd25c258a34cfaad196fecb1b135a2dc7fa87
- 스킬 버전: 0.3.0
- 가져온 날짜: 2026-10-07
- 방법: npx skills 미사용. GitHub에서 md 파일만 내려받음
- 하네스 적용 규칙: 키는 .env 환경변수(EXA_API_KEY)로만 사용. 스킬 예시의 export·코드 내 키 기입 방식은 따르지 않음 (docs/roles.md)

## 설치 후 검사 (2026-10-11)
- SkillSpector v2.12.0 `--no-llm`: 점수 39, CAUTION, 파일 15개 전부 검사
- HIGH 1: 이 SOURCE.md의 ".env" 언급(키 사용 규칙 메모)을 권한 상승으로 본 오탐
- MEDIUM 27: Exa 공식 API(api.exa.ai) curl 예시를 데이터 유출로 본 것(API 설명서라 정상), SOURCE.md의 "npx 미사용" 메모, references/agent.md의 "상태 확인 없이 읽지 말라" 안내 문장
- 판단: 실행 코드 없음, 외부 전송 대상은 Exa 공식 API뿐이라 유지. 키는 계속 환경변수로만 사용
