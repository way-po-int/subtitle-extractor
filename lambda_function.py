import json
import os
import boto3
# import psycopg2
from src.ytdlp_fetcher import YtDlpFetcher
from src.subtitle_processor import SubtitleProcessor

s3 = boto3.client('s3')
secrets_manager = boto3.client('secretsmanager')

def get_youtube_cookies():
    """Secrets Manager에서 YouTube 쿠키를 가져옵니다."""
    try:
        response = secrets_manager.get_secret_value(SecretId='youtube-cookies')
        return response.get('SecretString')
    except Exception as e:
        print(f"Error fetching youtube-cookies from Secrets Manager: {e}")
        return None

# def get_db_connection():
#     return psycopg2.connect(
#         host=os.environ['DB_HOST'],

def lambda_handler(event, context):
    # 1. 이벤트에서 비디오 URL 가져오기
    video_url = event.get('video_url')
    # social_media_id = event.get('social_media_id') # API 서버에서 전달

    if not video_url: # or not social_media_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'video_url is required'})
        }

    # 2. S3 버킷 이름 환경 변수에서 가져오기
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    if not bucket_name:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3_BUCKET_NAME environment variable is not set'})
        }

    try:
        # 1. Secrets Manager에서 쿠키 가져오기
        cookies = get_youtube_cookies()

        if cookies:
            print(f"Successfully fetched cookies from Secrets Manager. Length: {len(cookies)}, Preview: {cookies[:100]}...")
        else:
            print("Could not fetch cookies from Secrets Manager. Proceeding without cookies.")

        # 2. yt-dlp를 사용하여 정보 가져오기
        fetcher = YtDlpFetcher()
        data = fetcher.fetch_all_in_one(video_url, cookies=cookies)
        
        video_info = data.get('video_info', {})
        vtt_text = data.get('vtt_text')
        video_id = video_info.get('video_id', 'unknown_video')

        # 4. 자막 및 텍스트 처리
        processor = SubtitleProcessor()
        transcript = processor.process(vtt_text) if vtt_text else None

        # 5. 설명 및 고정 댓글 텍스트 정리
        if video_info.get('description'):
            video_info['description'] = processor.clean_text(video_info['description'])
        
        pinned_comment = data.get('pinned_comment')
        if pinned_comment and pinned_comment.get('text'):
            pinned_comment['text'] = processor.clean_text(pinned_comment['text'])

        # 6. S3에 저장할 최종 결과 데이터 구성
        result = {
            'video_info': video_info,
            'pinned_comment': pinned_comment,
            'transcript': transcript
        }
        
        # 7. S3에 JSON 파일로 업로드
        s3_key = f"{video_id}/scrap_result.json"
        # # 8. RDS 상태를 'SCRAPED'로 업데이트
        # update_status(db_conn, social_media_id, 'SCRAPED')

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(result, ensure_ascii=False, indent=4),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Successfully processed and uploaded to s3://{bucket_name}/{s3_key}'})
        }

    except Exception as e:
        # # 오류 발생 시 RDS 상태를 'FAILED'로 업데이트
        # if db_conn:
        #     update_status(db_conn, social_media_id, 'FAILED')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    # finally:
    #     if db_conn:
    #         db_conn.close()
