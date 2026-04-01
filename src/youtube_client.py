import requests


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def search_videos(
    api_key: str,
    query: str,
    max_results: int = 5,
    region_code: str = "IN",
) -> list[dict]:
    response = requests.get(
        f"{YOUTUBE_API_BASE}/search",
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoDuration": "short",
            "maxResults": max_results,
            "regionCode": region_code,
            "key": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()

    items = response.json().get("items", [])
    results = []
    for item in items:
        snippet = item.get("snippet", {})
        results.append(
            {
                "video_id": item["id"]["videoId"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
            }
        )
    return results


def get_video_details(api_key: str, video_id: str) -> dict:
    response = requests.get(
        f"{YOUTUBE_API_BASE}/videos",
        params={
            "part": "snippet",
            "id": video_id,
            "key": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()
    items = response.json().get("items", [])
    if not items:
        raise ValueError(f"No YouTube video found for ID: {video_id}")

    snippet = items[0].get("snippet", {})
    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
    }
