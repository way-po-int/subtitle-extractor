# YouTube 자막 추출 시퀀스 다이어그램

## 전체 프로세스 (yt-dlp 버전)

```mermaid
sequenceDiagram
    actor User
    participant CLI as run_ytdlp.sh
    participant Main as main_ytdlp.py
    participant Fetcher as YtDlpFetcher
    participant Processor as SubtitleProcessor
    participant YtDlp as yt-dlp Library
    participant YouTube as YouTube API
    participant FileSystem as File System

    User->>CLI: ./run_ytdlp.sh "VIDEO_URL"
    CLI->>CLI: 가상환경 활성화
    CLI->>CLI: PYTHONPATH 설정
    CLI->>Main: python main_ytdlp.py "VIDEO_URL"

    Main->>Fetcher: extract_video_id(url)
    Fetcher-->>Main: video_id

    alt 유효하지 않은 URL
        Main-->>User: ❌ 오류: 유효하지 않은 YouTube URL
    end

    rect rgb(200, 220, 250)
        Note over Main,YouTube: 1. 영상 정보 조회
        Main->>Fetcher: get_video_info(url)
        Fetcher->>YtDlp: extract_info(url)
        YtDlp->>YouTube: GET video metadata
        YouTube-->>YtDlp: video info (title, duration, etc.)
        YtDlp-->>Fetcher: video metadata
        Fetcher->>Fetcher: 영상 타입 판단 (WATCH/SHORTS)
        Fetcher->>Fetcher: 시간 포맷팅 (MM:SS)
        Fetcher-->>Main: video_info dict
        Main-->>User: ✅ 제목: {title}<br/>타입: {type} | 길이: {duration}
    end

    rect rgb(200, 250, 220)
        Note over Main,YouTube: 2. 자막 다운로드
        Main->>Fetcher: fetch_subtitle(url, lang, auto_generated)
        Fetcher->>YtDlp: extract_info(url)
        YtDlp->>YouTube: GET subtitle list
        YouTube-->>YtDlp: available subtitles

        alt 수동 작성 자막 있음
            YtDlp->>YouTube: GET manual subtitle URL
            YouTube-->>YtDlp: subtitle_url
        else 자동 생성 자막만 있음
            YtDlp->>YouTube: GET auto-generated subtitle URL
            YouTube-->>YtDlp: subtitle_url
        end

        Fetcher->>YouTube: GET subtitle content (VTT)
        YouTube-->>Fetcher: VTT text
        Fetcher-->>Main: vtt_text
        Main-->>User: ✅ 자막 다운로드 완료
    end

    rect rgb(250, 220, 200)
        Note over Main,Processor: 3. 자막 처리
        Main->>Processor: process(vtt_text, merge_count)

        Processor->>Processor: parse_vtt(vtt_text)
        Note over Processor: VTT 파싱<br/>타임스탬프 추출<br/>텍스트 추출

        Processor->>Processor: simplify_timestamp()
        Note over Processor: 00:01:23.456 → 01:23

        Processor->>Processor: remove_vtt_tags()
        Note over Processor: <c>, <v> 태그 제거

        Processor->>Processor: remove_emojis()
        Note over Processor: 이모지 제거

        Processor->>Processor: remove_rolling_overlap()
        Note over Processor: 중복 텍스트 제거

        Processor->>Processor: merge_blocks(group_size)
        Note over Processor: N개씩 블록 병합

        Processor-->>Main: processed_text
        Main-->>User: ✅ 자막 처리 완료
    end

    rect rgb(250, 250, 200)
        Note over Main,FileSystem: 4. 메타데이터 추가 & 파일 저장
        Main->>Main: create_metadata_header(video_info)
        Note over Main: 영상 타입, ID, 제목<br/>길이, 채널명, 업로드 날짜

        Main->>Main: sanitize_filename(title)
        Note over Main: 특수 문자 제거<br/>공백 정리<br/>길이 제한 (200자)

        Main->>Main: metadata + processed_text

        alt --no-save 옵션
            Main-->>User: 화면에 출력
        else --output 옵션
            Main->>FileSystem: write_text(custom_path)
            FileSystem-->>Main: 저장 완료
            Main-->>User: 💾 파일 저장 완료: {custom_path}
        else 기본 (자동 저장)
            Main->>FileSystem: mkdir('output/')
            Main->>FileSystem: write_text('output/{title}.txt')
            FileSystem-->>Main: 저장 완료
            Main-->>User: 💾 파일 저장 완료: output/{title}.txt
        end
    end

    Main-->>User: 📊 통계: {lines}줄, {chars}자
```

---

## 영상 정보 조회 상세

```mermaid
sequenceDiagram
    participant Main as main_ytdlp.py
    participant Fetcher as YtDlpFetcher
    participant YtDlp as yt-dlp
    participant YouTube as YouTube

    Main->>Fetcher: get_video_info(video_url)

    Fetcher->>Fetcher: extract_video_id(url)
    Note over Fetcher: URL 패턴 매칭<br/>video ID 추출

    Fetcher->>YtDlp: YoutubeDL(opts)
    Fetcher->>YtDlp: extract_info(url, download=False)

    YtDlp->>YouTube: API Request
    YouTube-->>YtDlp: Video Metadata

    YtDlp-->>Fetcher: info dict

    Fetcher->>Fetcher: 영상 타입 판단
    alt URL에 'shorts' 포함
        Note over Fetcher: video_type = 'shorts'
    else duration <= 60초
        Note over Fetcher: video_type = 'shorts'
    else
        Note over Fetcher: video_type = 'watch'
    end

    Fetcher->>Fetcher: 시간 포맷팅
    Note over Fetcher: duration(초) → MM:SS

    Fetcher-->>Main: {<br/>  video_id,<br/>  title,<br/>  duration,<br/>  duration_string,<br/>  video_type,<br/>  uploader,<br/>  upload_date<br/>}
```

---

## 자막 다운로드 상세

```mermaid
sequenceDiagram
    participant Main as main_ytdlp.py
    participant Fetcher as YtDlpFetcher
    participant YtDlp as yt-dlp
    participant YouTube as YouTube

    Main->>Fetcher: fetch_subtitle(url, lang='ko', auto_generated=True)

    Fetcher->>YtDlp: YoutubeDL(opts)
    Note over YtDlp: writesubtitles=True<br/>writeautomaticsub=True<br/>subtitleslangs=['ko']<br/>subtitlesformat='vtt'

    Fetcher->>YtDlp: extract_info(url, download=False)
    YtDlp->>YouTube: GET subtitle list
    YouTube-->>YtDlp: {<br/>  subtitles: {...},<br/>  automatic_captions: {...}<br/>}

    alt 수동 작성 자막 있음
        YtDlp-->>Fetcher: subtitles[lang]
        Fetcher->>Fetcher: VTT URL 추출
        Fetcher->>YouTube: GET subtitle content
        YouTube-->>Fetcher: VTT text
    else 자동 생성 자막만 있음 (auto_generated=True)
        YtDlp-->>Fetcher: automatic_captions[lang]
        Fetcher->>Fetcher: VTT URL 추출
        Fetcher->>YouTube: GET subtitle content
        YouTube-->>Fetcher: VTT text
    else 자막 없음
        Fetcher-->>Main: Exception: '{lang}' 언어의 자막을 찾을 수 없습니다
    end

    Fetcher-->>Main: vtt_text (string)
```

---

## 자막 처리 파이프라인

```mermaid
sequenceDiagram
    participant Main as main_ytdlp.py
    participant Processor as SubtitleProcessor

    Main->>Processor: process(vtt_text, merge_count=3)

    rect rgb(240, 240, 255)
        Note over Processor: Step 1: VTT 파싱
        Processor->>Processor: parse_vtt(vtt_text)
        Note over Processor: 정규식으로 파싱<br/>타임스탬프 & 텍스트 추출<br/>→ List[{timestamp, text}]
    end

    rect rgb(255, 240, 240)
        Note over Processor: Step 2: 텍스트 정리
        loop 각 블록마다
            Processor->>Processor: remove_vtt_tags(text)
            Note over Processor: <c>, <v> 등 제거

            Processor->>Processor: remove_emojis(text)
            Note over Processor: 유니코드 이모지 제거

            Processor->>Processor: text.strip()
            Note over Processor: 공백 제거
        end
    end

    rect rgb(240, 255, 240)
        Note over Processor: Step 3: 타임스탬프 단순화
        loop 각 블록마다
            Processor->>Processor: simplify_timestamp(ts)
            Note over Processor: 00:01:23.456 → 01:23<br/>00:00:05.123 → 00:05
        end
    end

    rect rgb(255, 255, 240)
        Note over Processor: Step 4: 중복 제거
        Processor->>Processor: remove_rolling_overlap(blocks)
        Note over Processor: 이전 블록과 중복되는<br/>앞부분 텍스트 제거
    end

    rect rgb(255, 240, 255)
        Note over Processor: Step 5: 블록 병합
        Processor->>Processor: merge_blocks(blocks, merge_count)
        Note over Processor: N개씩 묶어서<br/>하나의 블록으로 병합
    end

    rect rgb(240, 255, 255)
        Note over Processor: Step 6: 포맷팅
        Processor->>Processor: format_output(merged_blocks)
        Note over Processor: 타임스탬프\n텍스트\n\n 형식
    end

    Processor-->>Main: formatted_text (string)
```

---

## 파일 저장 프로세스

```mermaid
sequenceDiagram
    participant Main as main_ytdlp.py
    participant FS as File System

    Main->>Main: create_metadata_header(video_info)
    Note over Main: 메타데이터 헤더 생성<br/>영상 타입, ID, 제목 등

    Main->>Main: metadata + processed_text

    alt --no-save 옵션
        Main->>Main: print(result)
        Note over Main: 화면에만 출력
    else --output 지정
        Main->>Main: Path(output)
        Main->>FS: parent.mkdir(parents=True, exist_ok=True)
        Main->>FS: write_text(result, encoding='utf-8')
        FS-->>Main: 저장 완료
    else 기본 (자동 저장)
        Main->>Main: sanitize_filename(title)
        Note over Main: 특수 문자 제거<br/>< > : " / \ | ? *<br/>공백 정리<br/>길이 제한 200자

        Main->>FS: mkdir('output/', exist_ok=True)
        Main->>Main: filename = f"{safe_title}.txt"
        Main->>Main: output_path = 'output/' / filename
        Main->>FS: write_text(result, encoding='utf-8')
        FS-->>Main: 저장 완료
    end
```

---

## 에러 처리 플로우

```mermaid
sequenceDiagram
    participant User
    participant Main as main_ytdlp.py
    participant Fetcher as YtDlpFetcher
    participant YouTube as YouTube

    User->>Main: VIDEO_URL

    Main->>Fetcher: extract_video_id(url)

    alt 유효하지 않은 URL
        Fetcher-->>Main: None
        Main-->>User: ❌ 유효하지 않은 YouTube URL<br/>지원 형식 안내
    end

    Main->>Fetcher: get_video_info(url)

    alt 영상을 찾을 수 없음
        Fetcher->>YouTube: Request
        YouTube-->>Fetcher: 404 Error
        Fetcher-->>Main: Exception: 영상 정보 조회 실패
        Main-->>User: ❌ 오류 발생<br/>해결 방법 안내
    end

    Main->>Fetcher: fetch_subtitle(url, lang)

    alt 자막이 없음
        Fetcher->>YouTube: Request
        YouTube-->>Fetcher: No subtitles
        Fetcher-->>Main: Exception: '{lang}' 언어의 자막을 찾을 수 없습니다
        Main-->>User: ❌ 오류 발생<br/>💡 --list로 언어 확인<br/>💡 다른 언어 시도
    end

    alt 자막 처리 실패
        Main->>Main: process()
        Main-->>User: ❌ 자막 처리 결과가 비어있습니다
    end
```

---

## --list 옵션 플로우

```mermaid
sequenceDiagram
    participant User
    participant Main as main_ytdlp.py
    participant Fetcher as YtDlpFetcher
    participant YtDlp as yt-dlp
    participant YouTube as YouTube

    User->>Main: ./run_ytdlp.sh "URL" --list

    Main->>Fetcher: get_available_subtitles(url)

    Fetcher->>YtDlp: extract_info(url, download=False)
    YtDlp->>YouTube: GET subtitle list
    YouTube-->>YtDlp: {<br/>  subtitles,<br/>  automatic_captions<br/>}

    YtDlp-->>Fetcher: info dict

    Fetcher->>Fetcher: Parse subtitles
    loop 수동 작성 자막
        Fetcher->>Fetcher: {lang, name, formats}
    end

    loop 자동 생성 자막
        Fetcher->>Fetcher: {lang, name, formats}
    end

    Fetcher-->>Main: {<br/>  'manual': [...],<br/>  'automatic': [...]<br/>}

    Main->>Main: print_available_subtitles()
    Main-->>User: 📝 수동 작성 자막:<br/>  • Korean (ko)<br/>  • English (en)<br/><br/>🤖 자동 생성 자막:<br/>  • Japanese (ja)<br/>  ...
```

---

## 주요 컴포넌트 역할

### 1. run_ytdlp.sh

- 가상환경 활성화
- PYTHONPATH 설정
- main_ytdlp.py 실행

### 2. main_ytdlp.py

- CLI 인터페이스
- 옵션 파싱
- 전체 프로세스 조율
- 메타데이터 헤더 생성
- 파일명 생성 및 저장

### 3. YtDlpFetcher

- Video ID 추출
- 영상 정보 조회
- 자막 다운로드
- 영상 타입 판단

### 4. SubtitleProcessor

- VTT 파싱
- 텍스트 정리
- 중복 제거
- 블록 병합
- 포맷팅

### 5. yt-dlp Library

- YouTube API 통신
- 메타데이터 추출
- 자막 URL 제공

---

## 데이터 플로우

```
YouTube URL
    ↓
Video ID 추출
    ↓
영상 정보 조회 → {title, duration, type, ...}
    ↓
자막 다운로드 → VTT text
    ↓
VTT 파싱 → [{timestamp, text}, ...]
    ↓
텍스트 정리 → 태그/이모지 제거
    ↓
중복 제거 → 롤링 오버랩 제거
    ↓
블록 병합 → N개씩 묶기
    ↓
메타데이터 추가 → 헤더 + 자막
    ↓
파일 저장 → output/{title}.txt
```
