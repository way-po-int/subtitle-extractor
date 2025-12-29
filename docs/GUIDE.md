# YouTube 자막 추출 프로젝트 - 완벽 가이드

> YouTube 영상(Shorts 포함)의 자막을 자동으로 추출하고 저장하는 Python 스크립트

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📑 목차

- [개요](#-개요)
- [주요 기능](#-주요-기능)
- [빠른 시작](#-빠른-시작)
- [설치 가이드](#-설치-가이드)
- [사용법](#-사용법)
- [자동 저장 기능](#-자동-저장-기능)
- [옵션 상세](#-옵션-상세)
- [실전 예시](#-실전-예시)
- [문제 해결](#-문제-해결)
- [프로젝트 구조](#-프로젝트-구조)
- [FAQ](#-faq)

---

## 🎯 개요

YouTube 영상의 자막을 추출하여 텍스트 파일로 저장하는 Python 스크립트입니다. **yt-dlp**를 사용하여 거의 모든 YouTube 영상(Shorts 포함)에서 안정적으로 자막을 추출할 수 있습니다.

### 특징

- ✅ **거의 모든 영상 지원** - yt-dlp 기반으로 높은 성공률
- ✅ **Shorts 완벽 지원** - YouTube Shorts 자막 100% 추출
- ✅ **자동 저장** - 영상 제목으로 `output/` 디렉토리에 자동 저장
- ✅ **메타데이터 포함** - 영상 타입, ID, 길이, 채널명 등 자동 추가
- ✅ **100개 이상 언어** - 한국어, 영어, 일본어, 중국어 등
- ✅ **VTT 처리** - 타임스탬프 정리, 태그 제거, 중복 제거, 블록 병합
- ✅ **CLI 인터페이스** - 다양한 옵션 제공

---

## 🚀 주요 기능

### 1. 자동 저장 (v1.1.0+)

```bash
./run_ytdlp.sh "VIDEO_URL"
```

**자동으로 수행:**

- 영상 정보 조회 (제목, 타입, 길이)
- 자막 다운로드 및 처리
- 메타데이터 헤더 추가
- `output/영상제목.txt` 파일 생성

### 2. 메타데이터 헤더

모든 자막 파일 상단에 자동 추가:

```
================================================================================
YouTube 영상 정보
================================================================================
영상 타입: WATCH (또는 SHORTS)
영상 ID: xxxxx
영상 제목: 영상 제목
영상 길이: 12:42 (762초)
채널명: 채널명
업로드 날짜: 20230914
================================================================================

[자막 내용]
```

### 3. VTT 처리 파이프라인

1. **VTT 파싱** - WebVTT 형식 자막 파싱
2. **타임스탬프 단순화** - `00:01:23.456` → `01:23`
3. **태그 제거** - `<c>`, `<v>` 등 VTT 태그 제거
4. **이모지 제거** - 유니코드 이모지 제거
5. **중복 제거** - 롤링 오버랩 텍스트 제거
6. **블록 병합** - N개씩 묶어서 가독성 향상

---

## ⚡ 빠른 시작

### 1분 안에 시작하기

```bash
# 1. 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행 (자동 저장)
./run_ytdlp.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# 생성된 파일 확인
ls output/
```

**완료!** `output/` 디렉토리에 영상 제목으로 자막 파일이 생성됩니다.

---

## 📦 설치 가이드

### 요구사항

- Python 3.7 이상
- 인터넷 연결 (YouTube 접근)

### 1단계: 가상 환경 생성

```bash
# 프로젝트 디렉토리로 이동
cd youtube-subtitle

# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2단계: 의존성 설치

```bash
pip install -r requirements.txt
```

**설치되는 패키지:**

- `youtube-transcript-api==0.6.2` - 기존 버전용
- `requests==2.31.0` - HTTP 요청
- `yt-dlp>=2023.12.30` - 강력한 자막 추출 (권장)

### 3단계: 실행 테스트

```bash
./run_ytdlp.sh --help
```

성공하면 도움말이 출력됩니다.

### 가상 환경 종료

```bash
deactivate
```

### 다음 실행 시

```bash
source venv/bin/activate
./run_ytdlp.sh "VIDEO_URL"
```

---

## 💻 사용법

### 기본 사용 (자동 저장)

```bash
# 일반 영상
./run_ytdlp.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# Shorts
./run_ytdlp.sh "https://www.youtube.com/shorts/VIDEO_ID"

# Video ID만 입력
./run_ytdlp.sh "VIDEO_ID"
```

**결과:**

- `output/영상제목.txt` 파일 자동 생성
- 메타데이터 포함
- 화면에는 요약만 출력

### 지원 URL 형식

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (11자리 직접 입력)

### 자주 사용하는 명령어

```bash
# 화면에만 출력 (저장 안 함)
./run_ytdlp.sh "VIDEO_URL" --no-save

# 사용 가능한 자막 언어 확인
./run_ytdlp.sh "VIDEO_URL" --list

# 영어 자막
./run_ytdlp.sh "VIDEO_URL" --lang en

# 커스텀 경로로 저장
./run_ytdlp.sh "VIDEO_URL" --output "custom/path.txt"

# 5개씩 병합 (더 긴 문장)
./run_ytdlp.sh "VIDEO_URL" --merge 5

# 원본 VTT 출력
./run_ytdlp.sh "VIDEO_URL" --raw
```

---

## 📁 자동 저장 기능

### 파일명 생성 규칙

#### 1. 영상 제목 사용

- 영상 제목을 그대로 파일명으로 사용
- 예: `하루 종일 즐기는 2만 원 드라이브 코스🚗.txt`

#### 2. 특수 문자 처리

파일명에 사용할 수 없는 문자는 자동으로 제거:

- 제거: `< > : " / \ | ? *`
- 연속 공백 → 하나로 통합
- 앞뒤 공백 제거

#### 3. 길이 제한

- 최대 200자
- 초과 시 자동으로 잘림

### 저장 위치

```
youtube-subtitle/
├── output/                 # 자막 파일 저장 위치 (자동 생성)
│   ├── 영상제목1.txt
│   ├── 영상제목2.txt
│   └── ...
└── ...
```

### 영상 타입 구분

#### WATCH (일반 영상)

- URL에 `/watch?v=` 포함
- 또는 duration > 60초

#### SHORTS

- URL에 `/shorts/` 포함
- 또는 duration ≤ 60초

---

## 🔧 옵션 상세

### 언어 선택 (`-l`, `--lang`)

```bash
# 한국어 (기본값)
./run_ytdlp.sh "VIDEO_URL" --lang ko

# 영어
./run_ytdlp.sh "VIDEO_URL" --lang en

# 일본어
./run_ytdlp.sh "VIDEO_URL" --lang ja

# 중국어 간체
./run_ytdlp.sh "VIDEO_URL" --lang zh-Hans
```

**지원 언어:** 100개 이상 (ko, en, ja, zh-Hans, zh-Hant, es, fr, de, ru, ar 등)

### 병합 개수 (`-m`, `--merge`)

```bash
# 3개씩 병합 (기본값)
./run_ytdlp.sh "VIDEO_URL" --merge 3

# 5개씩 병합 (더 긴 문장)
./run_ytdlp.sh "VIDEO_URL" --merge 5

# Shorts는 2개 추천
./run_ytdlp.sh "SHORTS_URL" --merge 2
```

### 파일 저장 (`-o`, `--output`)

```bash
# 커스텀 파일명
./run_ytdlp.sh "VIDEO_URL" --output "subtitle.txt"

# 디렉토리 자동 생성
./run_ytdlp.sh "VIDEO_URL" --output "output/my_subtitle.txt"
```

### 화면 출력 (`--no-save`)

```bash
# 파일 저장 안 함, 화면에만 출력
./run_ytdlp.sh "VIDEO_URL" --no-save
```

### 자막 목록 (`--list`)

```bash
# 사용 가능한 자막 언어 확인
./run_ytdlp.sh "VIDEO_URL" --list
```

**출력 예시:**

```
📝 수동 작성 자막:
  • Korean (ko)
  • English (en)

🤖 자동 생성 자막:
  • Korean (auto-generated) (ko)
  • English (auto-generated) (en)
  • Japanese (auto-generated) (ja)
  ... (100개 이상!)
```

### 원본 VTT (`--raw`)

```bash
# 처리하지 않은 원본 VTT 출력
./run_ytdlp.sh "VIDEO_URL" --raw
```

### 수동 작성 자막만 (`--no-auto`)

```bash
# 자동 생성 자막 제외
./run_ytdlp.sh "VIDEO_URL" --no-auto
```

---

## 📊 실전 예시

### 예시 1: Shorts 자막 추출

```bash
./run_ytdlp.sh "https://www.youtube.com/shorts/HOg0upGxjeY"
```

**출력:**

```
🎬 Video ID: HOg0upGxjeY
📋 영상 정보 조회 중...
✅ 제목: 하루 종일 즐기는 2만 원 드라이브 코스🚗
   타입: SHORTS | 길이: 00:17

📥 자막 다운로드 중... (언어: ko, 자동생성: 허용)
✅ 자막 다운로드 완료

⚙️  자막 처리 중... (병합 개수: 3)
✅ 자막 처리 완료

💾 파일 저장 완료: /path/to/output/하루 종일 즐기는 2만 원 드라이브 코스🚗.txt

📊 통계: 25줄, 578자
```

**생성된 파일:** `output/하루 종일 즐기는 2만 원 드라이브 코스🚗.txt`

**파일 내용:**

```
================================================================================
YouTube 영상 정보
================================================================================
영상 타입: SHORTS
영상 ID: HOg0upGxjeY
영상 제목: 하루 종일 즐기는 2만 원 드라이브 코스🚗
영상 길이: 00:17 (17초)
채널명: 맛또리
업로드 날짜: 20250320
================================================================================

00:00
1인 2만 원대로 하루 종일 먹고 즐기는 드라이브 필수 코스인데 속식

00:03
하나만 시켜도 수육부터 양념 계장 불구이랑 20여가지가 넘는 반찬이
...
```

---

### 예시 2: 일반 영상 자막 추출

```bash
./run_ytdlp.sh "https://www.youtube.com/watch?v=vuufIjvjbU0"
```

**출력:**

```
🎬 Video ID: vuufIjvjbU0
📋 영상 정보 조회 중...
✅ 제목: 서울근교 가볼만한 곳 파주여행 BEST23 현지인 맛집, 카페, 여행지 모음 | 서울근교 여행 | 당일치기 여행 | 경기도 가볼만한 곳
   타입: WATCH | 길이: 12:42

📥 자막 다운로드 중... (언어: ko, 자동생성: 허용)
✅ 자막 다운로드 완료

⚙️  자막 처리 중... (병합 개수: 3)
✅ 자막 처리 완료

💾 파일 저장 완료: /path/to/output/서울근교 가볼만한 곳 파주여행 BEST23 현지인 맛집, 카페, 여행지 모음 서울근교 여행 당일치기 여행 경기도 가볼만한 곳.txt

📊 통계: 313줄, 5656자
```

---

### 예시 3: 여러 언어 시도

```bash
# 1단계: 사용 가능한 언어 확인
./run_ytdlp.sh "VIDEO_URL" --list

# 2단계: 원하는 언어로 다운로드
./run_ytdlp.sh "VIDEO_URL" --lang en
./run_ytdlp.sh "VIDEO_URL" --lang ja
```

---

### 예시 4: 일괄 처리

```bash
# 여러 영상 자막 추출
for url in \
  "https://www.youtube.com/watch?v=xxxxx1" \
  "https://www.youtube.com/watch?v=xxxxx2" \
  "https://www.youtube.com/shorts/xxxxx3"
do
  ./run_ytdlp.sh "$url"
  sleep 2  # API 제한 방지
done
```

**결과:**

```
output/
├── 영상제목1.txt
├── 영상제목2.txt
└── 영상제목3.txt
```

---

### 예시 5: URL 목록 파일 사용

```bash
# urls.txt 파일 생성
cat > urls.txt << EOF
https://www.youtube.com/watch?v=xxxxx1
https://www.youtube.com/watch?v=xxxxx2
https://www.youtube.com/shorts/xxxxx3
EOF

# 일괄 처리
while read url; do
  ./run_ytdlp.sh "$url"
  sleep 2
done < urls.txt
```

---

## 🔍 문제 해결

### 1. "No module named 'youtube_transcript_api'"

**원인:** 가상 환경이 활성화되지 않음

**해결:**

```bash
# 방법 1: run_ytdlp.sh 사용 (자동 활성화)
./run_ytdlp.sh "VIDEO_URL"

# 방법 2: 수동 활성화
source venv/bin/activate
python cli/main_ytdlp.py "VIDEO_URL"

# 방법 3: 의존성 재설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 2. "유효하지 않은 YouTube URL"

**원인:** URL 형식이 잘못됨

**해결:**

지원 형식:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `VIDEO_ID` (11자리)

**올바른 예시:**

```bash
./run_ytdlp.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
./run_ytdlp.sh "https://youtu.be/dQw4w9WgXcQ"
./run_ytdlp.sh "dQw4w9WgXcQ"
```

---

### 3. "자막을 찾을 수 없습니다"

**원인:** 해당 언어의 자막이 없음

**해결:**

```bash
# 1단계: 사용 가능한 언어 확인
./run_ytdlp.sh "VIDEO_URL" --list

# 2단계: 확인한 언어로 다운로드
./run_ytdlp.sh "VIDEO_URL" --lang en
```

---

### 4. "externally-managed-environment" 오류

**원인:** 시스템 Python에 직접 설치 시도

**해결:**

```bash
# 가상 환경 사용 필수
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 5. zsh: no matches found

**원인:** URL에 특수 문자가 있어 쉘이 해석

**해결:**

```bash
# URL을 따옴표로 감싸기
./run_ytdlp.sh "https://www.youtube.com/watch?v=xxxxx"
```

---

### 6. 가상 환경 재생성

```bash
# 기존 가상 환경 삭제
rm -rf venv

# 새로 생성
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 일반적인 문제 해결 순서

1. **가상환경 확인**

   ```bash
   ./run_ytdlp.sh --help  # 도움말이 나오면 OK
   ```

2. **영상 ID 확인**

   ```bash
   ./run_ytdlp.sh "VIDEO_ID" --list  # 자막 목록 확인
   ```

3. **언어 코드 확인**

   ```bash
   ./run_ytdlp.sh "VIDEO_ID" --lang ko
   ```

4. **다른 영상 시도**

   - 유명한 영상
   - 공식 채널 영상
   - 오래된 영상

5. **라이브러리 업데이트**
   ```bash
   source venv/bin/activate
   pip install --upgrade yt-dlp youtube-transcript-api requests
   ```

---

## 📂 프로젝트 구조

```
youtube-subtitle/
├── src/                        # 소스 코드
│   ├── __init__.py            # 패키지 초기화
│   ├── ytdlp_fetcher.py       # yt-dlp 자막 다운로드 (권장)
│   ├── youtube_fetcher.py     # youtube-transcript-api
│   └── subtitle_processor.py  # VTT 파싱 및 처리
│
├── cli/                    # 실행 스크립트
│   ├── main_ytdlp.py          # yt-dlp CLI (권장)
│   └── main.py                # youtube-transcript-api CLI
│
├── docs/                       # 문서
│   ├── README.md              # 이 문서 (통합 가이드)
│   └── SEQUENCE_DIAGRAM.md    # 시퀀스 다이어그램
│
├── output/                     # 자막 파일 저장 위치 (자동 생성)
│   └── *.txt                  # 추출된 자막 파일들
│
├── run_ytdlp.sh               # yt-dlp 실행 스크립트 (권장)
├── run.sh                     # 기존 버전 실행 스크립트
├── requirements.txt           # Python 의존성
├── .gitignore                 # Git 제외 파일
├── LICENSE                    # MIT 라이선스
├── CHANGELOG.md               # 변경 이력
├── UPDATE_SUMMARY.md          # v1.1.0 업데이트 요약
└── README.md                  # 프로젝트 메인 문서
```

---

## 💡 메타데이터 활용

### 1. 영상 타입별 분류

```bash
# SHORTS만 찾기
grep -l "영상 타입: SHORTS" output/*.txt

# WATCH만 찾기
grep -l "영상 타입: WATCH" output/*.txt
```

### 2. 채널별 분류

```bash
# 특정 채널 찾기
grep -l "채널명: 맛또리" output/*.txt
```

### 3. 날짜별 분류

```bash
# 2025년 3월 업로드 영상
grep -l "업로드 날짜: 202503" output/*.txt
```

### 4. 파일 정리 스크립트

```bash
# 날짜별 디렉토리로 이동
for file in output/*.txt; do
  date=$(grep "업로드 날짜:" "$file" | cut -d: -f2 | tr -d ' ')
  mkdir -p "output/$date"
  mv "$file" "output/$date/"
done
```

---

## ❓ FAQ

### Q1. youtube-transcript-api vs yt-dlp 중 어떤 것을 사용해야 하나요?

**A:** **yt-dlp 버전을 강력히 권장합니다.**

| 기능        | youtube-transcript-api | yt-dlp           |
| ----------- | ---------------------- | ---------------- |
| 성공률      | ⚠️ 낮음                | ✅ 매우 높음     |
| Shorts 지원 | ⚠️ 불안정              | ✅ 완벽          |
| 최신 영상   | ❌ 자주 실패           | ✅ 잘 작동       |
| 안정성      | ⚠️ API 변경에 취약     | ✅ 지속 업데이트 |

---

### Q2. 자막이 없는 영상은 어떻게 하나요?

**A:** 자막이 없는 영상은 추출할 수 없습니다. `--list` 옵션으로 먼저 확인하세요.

```bash
./run_ytdlp.sh "VIDEO_URL" --list
```

---

### Q3. 파일명이 너무 길어요.

**A:** 자동으로 200자로 제한됩니다. 커스텀 파일명을 사용하세요.

```bash
./run_ytdlp.sh "VIDEO_URL" --output "짧은이름.txt"
```

---

### Q4. 동일한 제목의 영상을 다시 다운로드하면?

**A:** 기존 파일을 덮어씁니다. 방지하려면:

```bash
./run_ytdlp.sh "VIDEO_URL" --output "output/영상제목_v2.txt"
```

---

### Q5. 여러 영상을 한 번에 처리할 수 있나요?

**A:** 네, 쉘 스크립트로 가능합니다.

```bash
for url in "URL1" "URL2" "URL3"; do
  ./run_ytdlp.sh "$url"
  sleep 2
done
```

---

### Q6. 자막 품질이 낮아요.

**A:** 자동 생성 자막은 품질이 낮을 수 있습니다. 수동 작성 자막만 사용하세요.

```bash
./run_ytdlp.sh "VIDEO_URL" --no-auto
```

---

### Q7. 특정 언어만 다운로드하고 싶어요.

**A:** `--lang` 옵션을 사용하세요.

```bash
./run_ytdlp.sh "VIDEO_URL" --lang en
```

---

### Q8. 원본 VTT 형식이 필요해요.

**A:** `--raw` 옵션을 사용하세요.

```bash
./run_ytdlp.sh "VIDEO_URL" --raw --output "subtitle.vtt"
```

---

## 🎉 결론

### 권장 사용법

```bash
# 이것만 기억하세요!
./run_ytdlp.sh "VIDEO_URL"
```

### 주요 장점

✅ **자동 저장** - 영상 제목으로 `output/` 디렉토리에 자동 저장  
✅ **메타데이터** - 영상 타입, ID, 길이, 채널명 자동 추가  
✅ **높은 성공률** - yt-dlp 기반으로 거의 모든 영상 지원  
✅ **Shorts 완벽 지원** - YouTube Shorts 자막 100% 추출  
✅ **100개 이상 언어** - 한국어, 영어, 일본어 등  
✅ **VTT 처리** - 타임스탬프 정리, 태그 제거, 중복 제거, 블록 병합

---

## ⚠️ 면책 조항 및 법적 고지

### 사용 목적

이 도구는 **교육, 연구, 접근성 향상** 목적으로 제공됩니다.

### 법적 책임

- ✅ **합법적 사용**: 공개된 자막을 개인적 목적으로 사용
- ⚠️ **YouTube ToS**: YouTube 서비스 약관을 준수해야 합니다
- ❌ **금지 사항**: 상업적 이용, 대량 수집, 자막 재판매

### 사용자 책임

- 이 도구의 사용으로 인한 법적 책임은 **사용자에게** 있습니다
- YouTube의 서비스 약관 및 저작권법을 준수하세요
- 자막 제작자 및 영상 업로더의 권리를 존중하세요

### 권장 사용 사례

```
✅ 청각 장애인을 위한 접근성 향상
✅ 언어 학습 및 연구
✅ 개인적인 자막 아카이빙
✅ 학술 연구 및 분석

❌ 자막 판매 또는 상업적 이용
❌ 대량 자동 수집 (스크래핑)
❌ YouTube 서비스 방해
```

---

## 📚 추가 문서

- **[SEQUENCE_DIAGRAM.md](SEQUENCE_DIAGRAM.md)** - 시퀀스 다이어그램 (Mermaid)
- **[LICENSE](../LICENSE)** - MIT 라이선스

---

## 📞 지원

문제가 계속되면:

1. **GitHub Issues** - [yt-dlp](https://github.com/yt-dlp/yt-dlp/issues)
2. **대안 도구** - `youtube-dl`
3. **수동 다운로드** - YouTube 웹사이트에서 직접 다운로드

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

**단, 사용 시 YouTube ToS 및 저작권법을 준수해야 합니다.**

---

**이제 YouTube의 거의 모든 영상(Shorts 포함)에서 자막을 안정적으로 추출할 수 있습니다!** 🚀
