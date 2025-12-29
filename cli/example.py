#!/usr/bin/env python3
"""
사용 예시 스크립트
Python 코드에서 모듈을 직접 사용하는 방법을 보여줍니다.
"""

from src.youtube_fetcher import YouTubeFetcher
from src.subtitle_processor import SubtitleProcessor


def example_basic():
    """기본 사용 예시"""
    print("=" * 60)
    print("예시 1: 기본 사용")
    print("=" * 60)
    
    # YouTube URL
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        # 1. 자막 다운로드
        print(f"자막 다운로드 중: {url}")
        vtt_text = YouTubeFetcher.fetch_from_url(url, languages=['en'])
        
        # 2. 자막 처리
        print("자막 처리 중...")
        processor = SubtitleProcessor()
        transcript = processor.process(vtt_text, merge_count=3)
        
        # 3. 결과 출력
        if transcript:
            print("\n처리된 자막:")
            print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
        else:
            print("자막이 비어있습니다.")
            
    except Exception as e:
        print(f"오류: {e}")


def example_check_available():
    """사용 가능한 자막 확인 예시"""
    print("\n" + "=" * 60)
    print("예시 2: 사용 가능한 자막 확인")
    print("=" * 60)
    
    video_id = "dQw4w9WgXcQ"
    
    try:
        transcripts = YouTubeFetcher.get_available_transcripts(video_id)
        
        print(f"\nVideo ID: {video_id}")
        print("사용 가능한 자막:")
        for t in transcripts:
            print(f"  - {t['language']} ({t['language_code']})")
            print(f"    자동 생성: {t['is_generated']}")
            print(f"    번역 가능: {t['is_translatable']}")
            
    except Exception as e:
        print(f"오류: {e}")


def example_custom_processing():
    """커스텀 처리 예시"""
    print("\n" + "=" * 60)
    print("예시 3: 커스텀 처리")
    print("=" * 60)
    
    url = "https://youtu.be/dQw4w9WgXcQ"
    
    try:
        # 자막 다운로드
        vtt_text = YouTubeFetcher.fetch_from_url(url, languages=['en'])
        
        # 처리기 생성
        processor = SubtitleProcessor()
        
        # 1단계: VTT 파싱
        blocks = processor.parse_vtt(vtt_text)
        print(f"\n파싱된 블록 수: {len(blocks)}")
        print("첫 3개 블록:")
        for block in blocks[:3]:
            print(f"  [{block['time']}] {block['text']}")
        
        # 2단계: 중복 제거
        cleaned_blocks = processor.remove_rolling_overlap(blocks)
        print(f"\n중복 제거 후: {len(cleaned_blocks)}개 블록")
        
        # 3단계: 병합 (5개씩)
        merged_blocks = processor.merge_blocks(cleaned_blocks, group_size=5)
        print(f"병합 후: {len(merged_blocks)}개 블록")
        
        # 결과 출력
        print("\n병합된 첫 번째 블록:")
        if merged_blocks:
            print(f"[{merged_blocks[0]['time']}]")
            print(merged_blocks[0]['text'])
            
    except Exception as e:
        print(f"오류: {e}")


def example_save_to_file():
    """파일 저장 예시"""
    print("\n" + "=" * 60)
    print("예시 4: 파일 저장")
    print("=" * 60)
    
    from pathlib import Path
    
    url = "https://youtu.be/dQw4w9WgXcQ"
    output_file = "output/example_subtitle.txt"
    
    try:
        # 자막 다운로드 및 처리
        vtt_text = YouTubeFetcher.fetch_from_url(url, languages=['en'])
        processor = SubtitleProcessor()
        transcript = processor.process(vtt_text, merge_count=3)
        
        # 파일 저장
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(transcript, encoding='utf-8')
        
        print(f"파일 저장 완료: {output_path.absolute()}")
        print(f"파일 크기: {output_path.stat().st_size} bytes")
        
    except Exception as e:
        print(f"오류: {e}")


if __name__ == '__main__':
    print("\n🎬 YouTube 자막 처리 예시\n")
    
    # 주의: 실제 실행 시 네트워크 연결이 필요하며,
    # 해당 영상에 자막이 있어야 합니다.
    
    # 예시 1: 기본 사용
    # example_basic()
    
    # 예시 2: 사용 가능한 자막 확인
    # example_check_available()
    
    # 예시 3: 커스텀 처리
    # example_custom_processing()
    
    # 예시 4: 파일 저장
    # example_save_to_file()
    
    print("\n💡 위의 함수 주석을 해제하여 실행해보세요!")
    print("   예: example_basic() 주석 제거")
