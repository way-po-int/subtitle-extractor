"""
yt-dlp를 사용한 YouTube 자막 다운로드 모듈
youtube-transcript-api보다 더 강력하고 안정적입니다.
"""

import re
import json
from typing import Optional, List, Dict
import yt_dlp


class YtDlpFetcher:
    """yt-dlp를 사용하여 YouTube 자막을 가져오는 클래스"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        YouTube URL에서 video ID 추출
        
        지원 형식:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # 직접 video ID 입력
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def fetch_all_in_one(video_url: str, lang: str = 'ko', auto_generated: bool = True) -> Dict:
        """
        단 한 번의 요청으로 영상 정보, 고정 댓글, 자막을 모두 가져옵니다.
        AWS 람다와 같이 실행 시간을 최소화해야 하는 환경에 최적화되었습니다.

        Args:
            video_url: YouTube 영상 URL 또는 video ID
            lang: 자막 언어 코드
            auto_generated: 자동 생성 자막 허용 여부

        Returns:
            {
                'video_info': { ... },
                'pinned_comment': { ... } or None,
                'vtt_text': '...' or None
            }
        """
        video_id = YtDlpFetcher.extract_video_id(video_url)
        if not video_id:
            raise ValueError("유효하지 않은 YouTube URL 또는 video ID입니다.")

        if len(video_url) == 11:
            video_url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': auto_generated,
            'subtitleslangs': [lang],
            'subtitlesformat': 'vtt',
            'getcomments': True,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                # 1. 영상 정보 파싱
                video_type = 'shorts' if 'shorts' in video_url.lower() or info.get('duration', 0) <= 60 else 'watch'
                duration = info.get('duration', 0)
                minutes, seconds = divmod(int(duration), 60)
                duration_string = f"{minutes:02d}:{seconds:02d}"

                video_info = {
                    'video_id': info.get('id', video_id),
                    'title': info.get('title', 'Unknown'),
                    'duration': duration,
                    'duration_string': duration_string,
                    'video_type': video_type,
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'description': info.get('description', 'No description')
                }

                # 2. 고정 댓글 파싱
                pinned_comment = None
                if 'comments' in info and info['comments']:
                    for comment in info['comments']:
                        if comment.get('is_pinned'):
                            pinned_comment = {
                                'author': comment.get('author', 'Unknown'),
                                'text': comment.get('text', 'No content')
                            }
                            break

                # 3. 자막 내용 파싱
                vtt_text = None
                requested_subtitles = info.get('requested_subtitles')
                if requested_subtitles and lang in requested_subtitles:
                    vtt_url = requested_subtitles[lang].get('url')
                    if vtt_url:
                        import requests
                        response = requests.get(vtt_url, timeout=10)
                        response.raise_for_status()
                        vtt_text = response.text

                if not vtt_text:
                    print(f"⚠️ '{lang}' 언어의 자막을 찾을 수 없습니다.")

                return {
                    'video_info': video_info,
                    'pinned_comment': pinned_comment,
                    'vtt_text': vtt_text
                }

        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"영상을 찾을 수 없거나 접근할 수 없습니다: {str(e)}")
        except Exception as e:
            raise Exception(f"데이터 조회 실패: {str(e)}")
