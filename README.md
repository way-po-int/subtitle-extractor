# YouTube 자막 추출기

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-blue.svg)](CHANGELOG.md)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FYOUR_USERNAME%2Fyoutube-subtitle&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

YouTube 영상(Shorts 포함)의 자막을 자동으로 추출하고 저장하는 Python 스크립트입니다.

**yt-dlp 기반으로 거의 모든 YouTube 영상을 지원합니다.**

## ✨ 주요 기능

- ✅ **거의 모든 YouTube 영상 지원** - yt-dlp 기반 높은 성공률
- ✅ **Shorts 완벽 지원** - YouTube Shorts 자막 100% 추출
- ✅ **자동 저장** - 영상 제목으로 `output/` 디렉토리에 자동 저장
- ✅ **메타데이터 자동 추가** - 영상 타입, ID, 길이, 채널명, 업로드 날짜
- ✅ **100개 이상 언어** - 한국어, 영어, 일본어, 중국어 등
- ✅ **VTT 처리** - 타임스탬프 정리, 태그 제거, 중복 제거, 블록 병합
- ✅ **CLI 인터페이스** - 다양한 옵션 제공

## 🚀 빠른 시작

```bash
# 1. 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행 (자동 저장)
./run_ytdlp.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# 생성된 파일 확인
ls script/
```

**완료!** `output/` 디렉토리에 영상 제목으로 자막 파일이 생성됩니다.

**📖 자세한 가이드:** [docs/GUIDE.md](docs/GUIDE.md)

## 💻 사용법

### 기본 사용

```bash
# 일반 영상
./run_ytdlp.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# Shorts
./run_ytdlp.sh "https://www.youtube.com/shorts/VIDEO_ID"

# Video ID만
./run_ytdlp.sh "VIDEO_ID"
```

**결과:** `output/영상제목.txt` 파일 자동 생성 (메타데이터 포함)

### 자주 사용하는 옵션

```bash
# 화면에만 출력 (저장 안 함)
./run_ytdlp.sh "VIDEO_URL" --no-save

# 사용 가능한 자막 언어 확인
./run_ytdlp.sh "VIDEO_URL" --list

# 영어 자막
./run_ytdlp.sh "VIDEO_URL" --lang en

# 커스텀 경로로 저장
./run_ytdlp.sh "VIDEO_URL" --output "custom/path.txt"
```

**📖 더 많은 옵션:** [docs/GUIDE.md](docs/GUIDE.md)

### 지원 URL 형식

```bash
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
VIDEO_ID (11자리)
```

## 출력 형식

### 처리된 자막 (기본)

```
01:23
첫 번째 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다.

04:56
네 번째 문장입니다. 다섯 번째 문장입니다. 여섯 번째 문장입니다.
```

### 원본 VTT (`--raw`)

```
WEBVTT

00:01:23.000 --> 00:01:25.500
첫 번째 문장입니다.

00:01:25.500 --> 00:01:28.000
두 번째 문장입니다.
```

## 📂 프로젝트 구조

```
youtube-subtitle/
├── src/                       # 소스 코드
│   ├── __init__.py
│   ├── ytdlp_fetcher.py      # yt-dlp 자막 다운로드
│   └── subtitle_processor.py # VTT 파싱 및 처리
├── cli/                   # 실행 스크립트
│   ├── main_ytdlp.py         # CLI 인터페이스
│   └── example.py            # 사용 예시
├── script/                    # 자막 파일 저장 위치 (자동 생성)
├── docs/                      # 문서
│   ├── README.md             # 완벽 가이드
│   └── SEQUENCE_DIAGRAM.md   # 시퀀스 다이어그램
├── run_ytdlp.sh              # 실행 스크립트
├── requirements.txt          # 의존성 (yt-dlp, requests)
└── README.md                 # 이 문서
```

## 💻 Python 코드에서 사용

```python
from src.ytdlp_fetcher import YtDlpFetcher
from src.subtitle_processor import SubtitleProcessor

# 1. 영상 정보 조회
video_info = YtDlpFetcher.get_video_info("VIDEO_URL")
print(f"제목: {video_info['title']}")
print(f"타입: {video_info['video_type']}")

# 2. 자막 다운로드
vtt_text = YtDlpFetcher.fetch_subtitle("VIDEO_URL", lang='ko')

# 3. 자막 처리
processor = SubtitleProcessor()
transcript = processor.process(vtt_text, merge_count=3)

print(transcript)
```

**자세한 예시:** `cli/example.py` 참고

## 처리 과정

1. **VTT 파싱**: WebVTT 형식의 자막을 타임스탬프와 텍스트로 분리
2. **태그 제거**: `<c>`, `<v>` 등의 VTT 태그 제거
3. **이모지 제거**: 유니코드 이모지 필터링
4. **타임스탬프 단순화**: `00:01:23.456` → `01:23`
5. **중복 제거**: 롤링 오버랩 텍스트 제거 (자막이 누적되는 경우)
6. **블록 병합**: 지정된 개수만큼 자막 블록 병합
7. **포맷팅**: 읽기 쉬운 형식으로 출력

## 🔧 문제 해결

### 1. "ModuleNotFoundError"

**원인:** 가상 환경이 활성화되지 않음

**해결:**

```bash
# run_ytdlp.sh 사용 (자동 활성화)
./run_ytdlp.sh "VIDEO_URL"

# 또는 수동 활성화
source venv/bin/activate
python cli/main_ytdlp.py "VIDEO_URL"
```

### 2. "자막을 찾을 수 없습니다"

**원인:** 해당 언어의 자막이 없음

**해결:**

```bash
# 사용 가능한 언어 확인
./run_ytdlp.sh "VIDEO_URL" --list

# 확인한 언어로 다운로드
./run_ytdlp.sh "VIDEO_URL" --lang en
```

### 3. "유효하지 않은 YouTube URL"

**지원 형식:**

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `VIDEO_ID` (11자리)

**📖 더 많은 문제 해결:** [docs/GUIDE.md](docs/GUIDE.md)

## ⚠️ 면책 조항 (Disclaimer)

이 도구는 **교육 및 연구 목적**으로 제공됩니다.

### 사용 시 주의사항

- ✅ **개인적 사용**: 학습, 연구, 접근성 향상 목적
- ✅ **공개 자막만**: YouTube에서 공개한 자막만 추출
- ⚠️ **YouTube ToS 준수**: YouTube 서비스 약관을 준수하세요
- ❌ **상업적 이용 금지**: 자막을 판매하거나 상업적으로 이용하지 마세요
- ❌ **대량 수집 금지**: 과도한 요청으로 서비스에 부담을 주지 마세요

### 법적 책임

- 이 도구의 사용으로 인한 법적 책임은 사용자에게 있습니다.
- YouTube의 서비스 약관 및 저작권법을 준수하세요.
- 자막 제작자 및 영상 업로더의 권리를 존중하세요.

**권장 사용 사례:**

- 청각 장애인을 위한 접근성 향상
- 언어 학습 및 연구
- 개인적인 자막 아카이빙

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다!

## 📚 문서

- **[docs/GUIDE.md](docs/GUIDE.md)** - 완벽 가이드 (설치, 사용법, 문제 해결, FAQ 등)
- **[docs/SEQUENCE_DIAGRAM.md](docs/SEQUENCE_DIAGRAM.md)** - 시퀀스 다이어그램 (Mermaid)
- **[CHANGELOG.md](CHANGELOG.md)** - 변경 이력
- **[UPDATE_SUMMARY.md](UPDATE_SUMMARY.md)** - v1.1.0 업데이트 요약

## 참고

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - YouTube 자막 다운로드 라이브러리
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 강력한 비디오 다운로더
- [WebVTT 형식](https://www.w3.org/TR/webvtt1/) - Web Video Text Tracks 표준
