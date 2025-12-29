"""
YouTube 자막 추출 라이브러리 (yt-dlp 기반)
"""

from .ytdlp_fetcher import YtDlpFetcher
from .subtitle_processor import SubtitleProcessor

__all__ = ['YtDlpFetcher', 'SubtitleProcessor']
__version__ = '2.0.0'
