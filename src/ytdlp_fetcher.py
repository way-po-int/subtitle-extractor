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
    def get_available_subtitles(video_url: str) -> Dict[str, List[Dict]]:
        """
        사용 가능한 자막 목록 조회
        
        Returns:
            {
                'automatic': [{'lang': 'ko', 'name': 'Korean'}, ...],
                'manual': [{'lang': 'en', 'name': 'English'}, ...]
            }
        """
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                result = {
                    'automatic': [],
                    'manual': []
                }
                
                # 자동 생성 자막
                if 'automatic_captions' in info and info['automatic_captions']:
                    for lang, subs in info['automatic_captions'].items():
                        result['automatic'].append({
                            'lang': lang,
                            'name': subs[0].get('name', lang) if subs else lang,
                            'formats': [s.get('ext') for s in subs]
                        })
                
                # 수동 작성 자막
                if 'subtitles' in info and info['subtitles']:
                    for lang, subs in info['subtitles'].items():
                        result['manual'].append({
                            'lang': lang,
                            'name': subs[0].get('name', lang) if subs else lang,
                            'formats': [s.get('ext') for s in subs]
                        })
                
                return result
                
        except Exception as e:
            raise Exception(f"자막 목록 조회 실패: {str(e)}")
    
    @staticmethod
    def fetch_subtitle(video_url: str, lang: str = 'ko', auto_generated: bool = True) -> str:
        """
        YouTube 영상의 자막을 VTT 형식으로 다운로드
        
        Args:
            video_url: YouTube 영상 URL 또는 video ID
            lang: 언어 코드 (예: 'ko', 'en')
            auto_generated: 자동 생성 자막 허용 여부
            
        Returns:
            VTT 형식의 자막 텍스트
        """
        # Video ID만 입력된 경우 전체 URL로 변환
        video_id = YtDlpFetcher.extract_video_id(video_url)
        if video_id and len(video_url) == 11:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': auto_generated,
            'subtitleslangs': [lang],
            'subtitlesformat': 'vtt',
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # 수동 작성 자막 우선
                if 'subtitles' in info and lang in info['subtitles']:
                    subs = info['subtitles'][lang]
                    vtt_url = next((s['url'] for s in subs if s.get('ext') == 'vtt'), None)
                    if vtt_url:
                        return YtDlpFetcher._download_subtitle_content(vtt_url)
                
                # 자동 생성 자막
                if auto_generated and 'automatic_captions' in info and lang in info['automatic_captions']:
                    subs = info['automatic_captions'][lang]
                    vtt_url = next((s['url'] for s in subs if s.get('ext') == 'vtt'), None)
                    if vtt_url:
                        return YtDlpFetcher._download_subtitle_content(vtt_url)
                
                raise Exception(f"'{lang}' 언어의 자막을 찾을 수 없습니다.")
                
        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"영상을 찾을 수 없거나 접근할 수 없습니다: {str(e)}")
        except Exception as e:
            if "찾을 수 없습니다" in str(e):
                raise
            raise Exception(f"자막 다운로드 실패: {str(e)}")
    
    @staticmethod
    def _download_subtitle_content(url: str) -> str:
        """자막 URL에서 실제 내용 다운로드"""
        import requests
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"자막 내용 다운로드 실패: {str(e)}")
    
    @staticmethod
    def get_video_info(video_url: str) -> Dict[str, any]:
        """
        YouTube 영상의 메타데이터 조회
        
        Args:
            video_url: YouTube 영상 URL 또는 video ID
            
        Returns:
            {
                'video_id': 'xxxxx',
                'title': '영상 제목',
                'duration': 123,  # 초 단위
                'duration_string': '02:03',  # 포맷된 시간
                'video_type': 'watch' or 'shorts',
                'uploader': '채널명',
                'upload_date': '20240101'
            }
        """
        # Video ID만 입력된 경우 전체 URL로 변환
        video_id = YtDlpFetcher.extract_video_id(video_url)
        if video_id and len(video_url) == 11:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # 영상 타입 판단 (Shorts vs 일반 영상)
                video_type = 'shorts' if 'shorts' in video_url.lower() else 'watch'
                # 또는 duration으로 판단 (Shorts는 보통 60초 이하)
                if info.get('duration', 0) <= 60:
                    video_type = 'shorts'
                
                # 시간 포맷팅
                duration = info.get('duration', 0)
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                duration_string = f"{minutes:02d}:{seconds:02d}"
                
                return {
                    'video_id': info.get('id', video_id),
                    'title': info.get('title', 'Unknown'),
                    'duration': duration,
                    'duration_string': duration_string,
                    'video_type': video_type,
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'description': info.get('description', 'No description')
                }
                
        except Exception as e:
            raise Exception(f"영상 정보 조회 실패: {str(e)}")
    
    @staticmethod
    def get_pinned_comment(video_url: str) -> Optional[Dict[str, str]]:
        """
        YouTube 영상의 고정 댓글 조회

        Args:
            video_url: YouTube 영상 URL 또는 video ID

        Returns:
            {
                'author': '댓글 작성자',
                'text': '고정 댓글 내용'
            }
            고정 댓글이 없으면 None을 반환합니다.
        """
        video_id = YtDlpFetcher.extract_video_id(video_url)
        if not video_id:
            raise ValueError("유효하지 않은 YouTube URL 또는 video ID입니다.")
        
        if len(video_url) == 11:
            video_url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'skip_download': True,
            'getcomments': True,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if 'comments' in info and info['comments']:
                    for comment in info['comments']:
                        if comment.get('is_pinned'):
                            return {
                                'author': comment.get('author', 'Unknown'),
                                'text': comment.get('text', 'No content')
                            }
                
                return None

        except Exception as e:
            raise Exception(f"고정 댓글 조회 실패: {str(e)}")
    
    @staticmethod
    def fetch_multiple_languages(video_url: str, languages: List[str] = None) -> Dict[str, str]:
        """
        여러 언어의 자막을 한 번에 다운로드
        
        Args:
            video_url: YouTube 영상 URL
            languages: 언어 코드 리스트 (None이면 ['ko', 'en'])
            
        Returns:
            {'ko': 'VTT 내용...', 'en': 'VTT 내용...'}
        """
        if languages is None:
            languages = ['ko', 'en']
        
        results = {}
        for lang in languages:
            try:
                vtt = YtDlpFetcher.fetch_subtitle(video_url, lang)
                results[lang] = vtt
            except Exception as e:
                print(f"⚠️  {lang} 자막 다운로드 실패: {e}")
                continue
        
        return results
