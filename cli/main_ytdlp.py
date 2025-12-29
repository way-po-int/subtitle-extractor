#!/usr/bin/env python3
"""
yt-dlp를 사용한 YouTube 자막 다운로드 스크립트
youtube-transcript-api보다 더 강력하고 안정적입니다.

사용법:
    python main_ytdlp.py <youtube_url> [옵션]
    
예시:
    python main_ytdlp.py "https://www.youtube.com/watch?v=xxxxx"
    python main_ytdlp.py "https://www.youtube.com/shorts/xxxxx" --lang ko
    python main_ytdlp.py "xxxxx" --output subtitle.txt
"""

import argparse
import sys
import re
from pathlib import Path
from src.ytdlp_fetcher import YtDlpFetcher
from src.subtitle_processor import SubtitleProcessor


def sanitize_filename(filename: str) -> str:
    """파일명에 사용할 수 없는 문자 제거"""
    # 파일명에 사용할 수 없는 문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 연속된 공백을 하나로
    filename = re.sub(r'\s+', ' ', filename)
    # 앞뒤 공백 제거
    filename = filename.strip()
    # 너무 긴 파일명 제한 (200자)
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def create_metadata_header(video_info: dict) -> str:
    """자막 파일 상단에 추가할 메타데이터 생성"""
    header = []
    header.append("="*80)
    header.append("YouTube 영상 정보")
    header.append("="*80)
    header.append(f"영상 타입: {video_info['video_type'].upper()}")
    header.append(f"영상 ID: {video_info['video_id']}")
    header.append(f"영상 제목: {video_info['title']}")
    header.append(f"영상 길이: {video_info['duration_string']} ({video_info['duration']}초)")
    header.append(f"채널명: {video_info['uploader']}")
    header.append(f"업로드 날짜: {video_info['upload_date']}")
    header.append("="*80)
    header.append("")
    return "\n".join(header)


def print_available_subtitles(video_url: str):
    """사용 가능한 자막 목록 출력"""
    try:
        subs = YtDlpFetcher.get_available_subtitles(video_url)
        
        has_subs = False
        
        if subs['manual']:
            has_subs = True
            print("\n📝 수동 작성 자막:")
            print("-" * 60)
            for sub in subs['manual']:
                formats = ', '.join(sub['formats']) if sub['formats'] else 'N/A'
                print(f"  • {sub['name']} ({sub['lang']}) - 형식: {formats}")
            print("-" * 60)
        
        if subs['automatic']:
            has_subs = True
            print("\n🤖 자동 생성 자막:")
            print("-" * 60)
            for sub in subs['automatic']:
                formats = ', '.join(sub['formats']) if sub['formats'] else 'N/A'
                print(f"  • {sub['name']} ({sub['lang']}) - 형식: {formats}")
            print("-" * 60)
        
        if not has_subs:
            print("\n❌ 사용 가능한 자막이 없습니다.")
        
    except Exception as e:
        print(f"❌ 오류: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='yt-dlp를 사용하여 YouTube 자막을 다운로드하고 정리합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  %(prog)s "https://www.youtube.com/watch?v=xxxxx"
  %(prog)s "https://www.youtube.com/shorts/xxxxx" --lang ko
  %(prog)s "xxxxx" --lang en --merge 5
  %(prog)s "https://youtu.be/xxxxx" --output result.txt
  %(prog)s "xxxxx" --list
        """
    )
    
    parser.add_argument(
        'url',
        help='YouTube 영상 URL 또는 video ID'
    )
    
    parser.add_argument(
        '-l', '--lang',
        type=str,
        default='ko',
        help='자막 언어 코드 (기본값: ko)'
    )
    
    parser.add_argument(
        '-m', '--merge',
        type=int,
        default=3,
        help='병합할 자막 블록 개수 (기본값: 3)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='출력 파일 경로 (지정하지 않으면 영상 제목으로 자동 저장)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='파일로 저장하지 않고 화면에만 출력'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='사용 가능한 자막 목록만 출력'
    )
    
    parser.add_argument(
        '--raw',
        action='store_true',
        help='처리하지 않은 원본 VTT 출력'
    )
    
    parser.add_argument(
        '--no-auto',
        action='store_true',
        help='자동 생성 자막 제외 (수동 작성 자막만)'
    )
    
    args = parser.parse_args()
    
    # Video ID 추출
    video_id = YtDlpFetcher.extract_video_id(args.url)
    if not video_id:
        print(f"❌ 오류: 유효하지 않은 YouTube URL - {args.url}")
        print("\n지원 형식:")
        print("  • https://www.youtube.com/watch?v=VIDEO_ID")
        print("  • https://youtu.be/VIDEO_ID")
        print("  • https://www.youtube.com/shorts/VIDEO_ID")
        print("  • VIDEO_ID (11자리)")
        sys.exit(1)
    
    print(f"🎬 Video ID: {video_id}")
    
    # 자막 목록만 출력
    if args.list:
        print_available_subtitles(args.url)
        sys.exit(0)
    
    try:
        # 1. 영상 정보 가져오기
        print("📋 영상 정보 조회 중...")
        video_info = YtDlpFetcher.get_video_info(args.url)
        print(f"✅ 제목: {video_info['title']}")
        print(f"   타입: {video_info['video_type'].upper()} | 길이: {video_info['duration_string']}")
        
        # 2. 자막 다운로드
        auto_gen = not args.no_auto
        print(f"\n📥 자막 다운로드 중... (언어: {args.lang}, 자동생성: {'허용' if auto_gen else '제외'})")
        vtt_text = YtDlpFetcher.fetch_subtitle(args.url, args.lang, auto_generated=auto_gen)
        
        if not vtt_text:
            print("❌ 자막을 가져올 수 없습니다.")
            sys.exit(1)
        
        print("✅ 자막 다운로드 완료")
        
        # 원본 VTT 출력
        if args.raw:
            result = vtt_text
            print("\n" + "="*60)
            print("원본 VTT:")
            print("="*60)
        else:
            # 3. 자막 처리
            print(f"\n⚙️  자막 처리 중... (병합 개수: {args.merge})")
            processor = SubtitleProcessor()
            processed_text = processor.process(vtt_text, args.merge)
            
            if not processed_text:
                print("❌ 자막 처리 결과가 비어있습니다.")
                sys.exit(1)
            
            # 메타데이터 헤더 추가
            metadata_header = create_metadata_header(video_info)
            result = metadata_header + "\n" + processed_text
            
            print("✅ 자막 처리 완료")
            print("\n" + "="*60)
            print("처리된 자막:")
            print("="*60)
        
        # 4. 결과 출력 또는 저장
        if args.no_save:
            # 화면에만 출력
            print(result)
            print("="*60)
        elif args.output:
            # 지정된 경로로 저장
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result, encoding='utf-8')
            print(f"\n💾 파일 저장 완료: {output_path.absolute()}")
        else:
            # 영상 제목으로 자동 저장 (output/ 디렉토리)
            script_dir = Path('output')
            script_dir.mkdir(exist_ok=True)
            
            # 파일명 생성 (영상 제목 + video_id)
            safe_title = sanitize_filename(video_info['title'])
            filename = f"{safe_title}.txt"
            output_path = script_dir / filename
            
            # 파일 저장
            output_path.write_text(result, encoding='utf-8')
            print(f"\n💾 파일 저장 완료: {output_path.absolute()}")
        
        # 통계 출력
        line_count = len(result.strip().split('\n'))
        char_count = len(result)
        print(f"\n📊 통계: {line_count}줄, {char_count}자")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n💡 해결 방법:")
        print("  1. --list 옵션으로 사용 가능한 언어 확인")
        print("  2. 다른 언어 코드 시도 (예: --lang en)")
        print("  3. 자동 생성 자막 허용 (--no-auto 제거)")
        sys.exit(1)


if __name__ == '__main__':
    main()
