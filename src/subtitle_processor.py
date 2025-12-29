"""
YouTube 자막 처리 모듈
VTT 형식의 자막을 파싱하고 정리합니다.
"""

import re
from typing import List, Dict, Optional


class SubtitleProcessor:
    """YouTube VTT 자막을 처리하는 클래스"""
    
    TIME_REGEX = re.compile(r'^(\d{2}:\d{2}:\d{2}\.\d{3}) -->')
    VTT_TAG_REGEX = re.compile(r'<[^>]*>')
    EMOJI_REGEX = re.compile(
        r'[\U0001F300-\U0001F9FF\U00002600-\U000026FF\U00002700-\U000027BF'
        r'\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\U0001F100-\U0001F64F'
        r'\U0001F680-\U0001F6FF\U0001F910-\U0001F96B\U0001F980-\U0001F9E0]',
        flags=re.UNICODE
    )
    
    @staticmethod
    def simplify_timestamp(timestamp: str) -> str:
        """
        타임스탬프를 간단한 형식으로 변환
        00:01:23.456 -> 01:23
        """
        parts = timestamp.split(':')
        if len(parts) == 3:
            minutes = parts[1]
            seconds = parts[2].split('.')[0]
            return f"{minutes}:{seconds}"
        return timestamp
    
    @staticmethod
    def remove_vtt_tags(text: str) -> str:
        """VTT 태그 제거 (예: <c>, <v> 등)"""
        return SubtitleProcessor.VTT_TAG_REGEX.sub('', text).strip()
    
    @staticmethod
    def remove_emojis(text: str) -> str:
        """이모지 제거"""
        return SubtitleProcessor.EMOJI_REGEX.sub('', text)
    
    def parse_vtt(self, vtt_text: str) -> List[Dict[str, str]]:
        """
        VTT 텍스트를 파싱하여 타임스탬프와 텍스트 블록으로 변환
        
        Args:
            vtt_text: VTT 형식의 자막 텍스트
            
        Returns:
            [{'time': '01:23', 'text': '자막 내용'}, ...]
        """
        if not vtt_text or not vtt_text.strip():
            return []
        
        lines = vtt_text.split('\n')
        time_blocks = []
        current_time = None
        current_text = ''
        
        for raw_line in lines:
            line = raw_line.strip()
            
            # 헤더 라인 스킵
            if (not line or 
                line.startswith('WEBVTT') or 
                line.startswith('Kind:') or 
                line.startswith('Language:')):
                continue
            
            # 타임스탬프 라인 감지
            match = self.TIME_REGEX.match(line)
            if match:
                if current_time is not None and current_text:
                    time_blocks.append({
                        'time': current_time,
                        'text': current_text
                    })
                current_time = self.simplify_timestamp(match.group(1))
                current_text = ''
            else:
                # 텍스트 라인 처리
                clean_text = self.remove_vtt_tags(line)
                clean_text = self.remove_emojis(clean_text)
                current_text = clean_text
        
        # 마지막 블록 추가
        if current_time is not None and current_text:
            time_blocks.append({
                'time': current_time,
                'text': current_text
            })
        
        return time_blocks
    
    def remove_rolling_overlap(self, blocks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        롤링 오버랩 제거
        이전 텍스트가 현재 텍스트의 시작 부분에 포함되어 있으면 중복 제거
        """
        if not blocks:
            return []
        
        final_blocks = [blocks[0]]
        
        for i in range(1, len(blocks)):
            prev = final_blocks[-1]
            curr = blocks[i]
            
            if curr['text'].startswith(prev['text']):
                # 중복 부분 제거
                diff = curr['text'][len(prev['text']):].strip()
                if diff:
                    final_blocks.append({
                        'time': curr['time'],
                        'text': diff
                    })
            else:
                final_blocks.append(curr)
        
        # 빈 텍스트 제거
        return [b for b in final_blocks if b['text'].strip()]
    
    def merge_blocks(self, blocks: List[Dict[str, str]], group_size: int = 3) -> List[Dict[str, str]]:
        """
        블록을 지정된 크기로 그룹화하여 병합
        
        Args:
            blocks: 자막 블록 리스트
            group_size: 병합할 블록 개수 (기본값: 3)
        """
        merged_blocks = []
        
        for i in range(0, len(blocks), group_size):
            base_time = blocks[i]['time']
            merged_text = blocks[i]['text']
            
            # 다음 블록들 병합
            for j in range(1, group_size):
                if i + j < len(blocks):
                    merged_text += ' ' + blocks[i + j]['text']
            
            merged_blocks.append({
                'time': base_time,
                'text': merged_text.strip()
            })
        
        return merged_blocks
    
    def process(self, vtt_text: str, merge_count: int = 3) -> Optional[str]:
        """
        VTT 자막을 처리하여 정리된 transcript 반환
        
        Args:
            vtt_text: VTT 형식의 자막 텍스트
            merge_count: 병합할 블록 개수 (기본값: 3)
            
        Returns:
            정리된 transcript 문자열 또는 None
        """
        # 1. VTT 파싱
        time_blocks = self.parse_vtt(vtt_text)
        if not time_blocks:
            return None
        
        # 2. 롤링 오버랩 제거
        final_blocks = self.remove_rolling_overlap(time_blocks)
        if not final_blocks:
            return None
        
        # 3. 블록 병합
        merged_blocks = self.merge_blocks(final_blocks, merge_count)
        
        # 4. 최종 포맷팅
        transcript = '\n\n'.join(
            f"{block['time']}\n{block['text']}"
            for block in merged_blocks
        )
        
        return transcript if transcript.strip() else None
