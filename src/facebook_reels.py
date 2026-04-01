import os

import requests


GRAPH_API_BASE = "https://graph.facebook.com/v23.0"


def publish_reel(page_id: str, access_token: str, description: str, file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    start_data = {
        "access_token": access_token,
        "upload_phase": "start",
    }
    endpoint = f"{GRAPH_API_BASE}/{page_id}/video_reels"
    start_response = requests.post(endpoint, data=start_data, timeout=60)
    start_response.raise_for_status()
    start_payload = start_response.json()

    upload_url = start_payload.get("upload_url")
    video_id = start_payload.get("video_id")
    if not upload_url or not video_id:
        raise RuntimeError(f"Unexpected start response: {start_payload}")

    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as video_file:
        upload_response = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {access_token}",
                "offset": "0",
                "file_size": str(file_size),
            },
            data=video_file,
            timeout=300,
        )
    upload_response.raise_for_status()

    finish_response = requests.post(
        endpoint,
        data={
            "access_token": access_token,
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description,
        },
        timeout=60,
    )
    finish_response.raise_for_status()
    return {
        "video_id": video_id,
        "start": start_payload,
        "upload": upload_response.json() if upload_response.content else {"success": True},
        "finish": finish_response.json(),
    }
