import argparse
import os
import sys

from dotenv import load_dotenv

from src.caption_builder import build_caption
from src.facebook_reels import publish_reel
from src.source_queue import (
    build_caption_from_asset,
    delete_asset_files,
    pick_unposted_videos,
    record_posted,
)
from src.youtube_client import get_video_details, search_videos


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover YouTube videos and publish approved Facebook Reels."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search YouTube videos")
    search_parser.add_argument(
        "--query",
        default=os.getenv("DEFAULT_SEARCH_QUERY", "food vlogger shorts"),
        help="Search query for YouTube",
    )
    search_parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of videos to return",
    )
    search_parser.add_argument(
        "--region-code",
        default=os.getenv("DEFAULT_REGION_CODE", "IN"),
        help="Two-letter region code",
    )

    caption_parser = subparsers.add_parser(
        "caption", help="Generate a Facebook caption from YouTube metadata"
    )
    caption_parser.add_argument("--video-id", required=True, help="YouTube video ID")

    publish_parser = subparsers.add_parser(
        "publish", help="Publish an approved Reel to Facebook Page"
    )
    publish_parser.add_argument("--video-id", required=True, help="YouTube video ID")
    publish_parser.add_argument(
        "--file",
        required=True,
        help="Path to a local video file you own or are licensed to reuse.",
    )
    publish_parser.add_argument(
        "--description",
        help="Optional override for the generated caption.",
    )

    daily_parser = subparsers.add_parser(
        "publish-daily", help="Publish a daily batch from a local source folder"
    )
    daily_parser.add_argument(
        "--source-dir",
        default=os.getenv("VIDEO_SOURCE_DIR"),
        help="Folder containing approved local videos, such as a Google Drive synced folder.",
    )
    daily_parser.add_argument(
        "--count",
        type=int,
        default=int(os.getenv("DAILY_POST_COUNT", "3")),
        help="Maximum number of videos to publish in this run.",
    )
    daily_parser.add_argument(
        "--state-file",
        default=os.getenv("POSTED_STATE_FILE", "posted_state.json"),
        help="JSON file used to track which assets have already been posted.",
    )
    daily_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview selected videos without uploading them.",
    )
    daily_parser.add_argument(
        "--delete-after-post",
        action="store_true",
        default=os.getenv("DELETE_AFTER_POST", "").lower() in {"1", "true", "yes", "on"},
        help="Delete the posted video from the source folder after a successful upload.",
    )

    return parser


def ensure_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def run_search(args: argparse.Namespace) -> int:
    api_key = ensure_env("YOUTUBE_API_KEY")
    videos = search_videos(
        api_key=api_key,
        query=args.query,
        max_results=args.max_results,
        region_code=args.region_code,
    )
    for video in videos:
        print(f"- {video['title']}")
        print(f"  video_id: {video['video_id']}")
        print(f"  channel: {video['channel_title']}")
        print(f"  published_at: {video['published_at']}")
        print(f"  url: https://www.youtube.com/watch?v={video['video_id']}")
    return 0


def run_caption(args: argparse.Namespace) -> int:
    api_key = ensure_env("YOUTUBE_API_KEY")
    details = get_video_details(api_key=api_key, video_id=args.video_id)
    print(build_caption(details))
    return 0


def run_publish(args: argparse.Namespace) -> int:
    api_key = ensure_env("YOUTUBE_API_KEY")
    fb_page_id = ensure_env("FB_PAGE_ID")
    fb_access_token = ensure_env("FB_PAGE_ACCESS_TOKEN")

    details = get_video_details(api_key=api_key, video_id=args.video_id)
    description = args.description or build_caption(details)

    response = publish_reel(
        page_id=fb_page_id,
        access_token=fb_access_token,
        description=description,
        file_path=args.file,
    )
    print("Publish request submitted.")
    print(response)
    return 0


def run_publish_daily(args: argparse.Namespace) -> int:
    if not args.source_dir:
        raise RuntimeError("Provide --source-dir or set VIDEO_SOURCE_DIR in .env.")

    selected_assets = pick_unposted_videos(
        source_dir=args.source_dir,
        state_file=args.state_file,
        limit=args.count,
    )
    if not selected_assets:
        print("No unposted videos found.")
        return 0

    if args.dry_run:
        print("Dry run: the following videos would be posted:")
        for asset in selected_assets:
            print(f"- {asset}")
        return 0

    fb_page_id = ensure_env("FB_PAGE_ID")
    fb_access_token = ensure_env("FB_PAGE_ACCESS_TOKEN")

    for asset in selected_assets:
        description = build_caption_from_asset(asset)
        print(f"Posting: {asset}")
        response = publish_reel(
            page_id=fb_page_id,
            access_token=fb_access_token,
            description=description,
            file_path=asset,
        )
        record_posted(state_file=args.state_file, asset_path=asset, response=response)
        print(f"Posted video_id={response['video_id']}")
        if args.delete_after_post:
            delete_asset_files(asset)
            print(f"Deleted local source files for: {asset}")

    return 0


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "search":
            return run_search(args)
        if args.command == "caption":
            return run_caption(args)
        if args.command == "publish":
            return run_publish(args)
        if args.command == "publish-daily":
            return run_publish_daily(args)
        parser.print_help()
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
