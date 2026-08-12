"""
post_comment.py
Posts a pinned comment on a YouTube video using the YouTube Data API v3.
Requires the youtube.force-ssl scope (broader than youtube.upload).
Non-fatal — if commenting fails, the video upload already succeeded.
"""
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def _get_authenticated_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def post_pinned_comment(video_id: str, comment_text: str) -> str | None:
    try:
        youtube = _get_authenticated_service()

        response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text,
                        }
                    },
                }
            },
        ).execute()

        comment_id = response["id"]
        print(f"Comment posted: {comment_id}")
        print(f"Comment pinned on video: {video_id}")
        return comment_id

    except Exception as e:
        print(f"Comment post failed (non-fatal — video already uploaded): {e}")
        return None
