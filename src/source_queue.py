import json
import os
from datetime import datetime


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi"}


def _load_state(state_file: str) -> dict:
    if not os.path.exists(state_file):
        return {"posted": []}
    with open(state_file, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_state(state_file: str, state: dict) -> None:
    with open(state_file, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)


def _normalize(path: str) -> str:
    return os.path.abspath(path)


def _list_videos(source_dir: str) -> list[str]:
    if not os.path.isdir(source_dir):
        raise NotADirectoryError(source_dir)

    assets: list[str] = []
    for entry in os.scandir(source_dir):
        if entry.is_file() and os.path.splitext(entry.name)[1].lower() in VIDEO_EXTENSIONS:
            assets.append(_normalize(entry.path))
    assets.sort(key=lambda item: os.path.getmtime(item))
    return assets


def pick_unposted_videos(source_dir: str, state_file: str, limit: int) -> list[str]:
    state = _load_state(state_file)
    posted_paths = {_normalize(item["path"]) for item in state.get("posted", [])}
    assets = _list_videos(source_dir)
    return [asset for asset in assets if asset not in posted_paths][:limit]


def build_caption_from_asset(asset_path: str) -> str:
    sidecar_path = os.path.splitext(asset_path)[0] + ".txt"
    if os.path.exists(sidecar_path):
        with open(sidecar_path, "r", encoding="utf-8") as handle:
            return handle.read().strip()

    title = os.path.splitext(os.path.basename(asset_path))[0].replace("_", " ").replace("-", " ")
    title = " ".join(title.split())
    return f"{title}\n\n#reels #shortvideo #dailycontent"


def record_posted(state_file: str, asset_path: str, response: dict) -> None:
    state = _load_state(state_file)
    state.setdefault("posted", []).append(
        {
            "path": _normalize(asset_path),
            "posted_at": datetime.now().isoformat(timespec="seconds"),
            "facebook_video_id": response.get("video_id"),
        }
    )
    _save_state(state_file, state)


def delete_asset_files(asset_path: str) -> None:
    video_path = _normalize(asset_path)
    if os.path.exists(video_path):
        os.remove(video_path)

    sidecar_path = os.path.splitext(video_path)[0] + ".txt"
    if os.path.exists(sidecar_path):
        os.remove(sidecar_path)
