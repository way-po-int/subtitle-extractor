#!/bin/bash
# yt-dlp 버전 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 가상 환경 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상 환경이 없습니다."
    echo ""
    echo "다음 명령어로 설치하세요:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 가상 환경 활성화
source venv/bin/activate

# yt-dlp 설치 확인
if ! python -c "import yt_dlp" 2>/dev/null; then
    echo "⚠️  yt-dlp가 설치되지 않았습니다. 설치 중..."
    pip install yt-dlp
fi

# Python 경로 설정
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# 인자가 없으면 도움말 출력
if [ $# -eq 0 ]; then
    python cli/main_ytdlp.py --help
else
    python cli/main_ytdlp.py "$@"
fi
