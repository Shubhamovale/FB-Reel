# Facebook Reel Auto Poster Starter

This project is a compliant starter for a Facebook Reel pipeline.

What it does:

- Searches YouTube for food-vlogger videos using the YouTube Data API
- Pulls title, channel, and description metadata
- Builds a Facebook-ready caption from that metadata
- Publishes a Reel to a Facebook Page from a video file you own
- Publishes up to 3 videos per day from a local folder such as a Google Drive synced folder

What it does not do:

- It does not download YouTube Shorts or videos from other creators
- It does not automate posting to personal Facebook profiles
- It does not bypass platform rules, browser flows, or login protections

## Why this limitation exists

Using another creator's YouTube Short as a source file is usually a copyright and platform-policy problem unless you have explicit permission or a separate licensed copy of the media.

This starter keeps the pipeline on the safe side:

1. Discover videos and metadata on YouTube
2. Review or approve the content source
3. Publish only approved media that you own or are licensed to reuse

## Setup

1. Create and activate a virtual environment
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in:

- `YOUTUBE_API_KEY`
- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN`

## Usage

Search YouTube for candidate videos:

```powershell
python main.py search --query "street food shorts" --max-results 5
```

Generate a caption from a specific YouTube video:

```powershell
python main.py caption --video-id VIDEO_ID
```

Publish from a local file you own:

```powershell
python main.py publish --file "C:\media\licensed-short.mp4" --video-id VIDEO_ID
```

Publish 3 videos from a Drive-synced folder:

```powershell
python main.py publish-daily --source-dir "C:\Users\YourName\Google Drive\fb-reels"
```

Publish and delete successfully posted files from the source folder:

```powershell
python main.py publish-daily --source-dir "C:\Users\YourName\Google Drive\fb-reels" --delete-after-post
```

Preview which videos would be posted without uploading:

```powershell
python main.py publish-daily --source-dir "C:\Users\YourName\Google Drive\fb-reels" --dry-run
```

## Typical workflow

1. Use `search` to find food-vlogger candidates
2. Pick a video whose creator has given you permission, or replace it with your own stored copy from a licensed source
3. Use `caption` to draft the Facebook description
4. Use `publish` to send the Reel to your Facebook Page

## Drive Folder Workflow

If you use Google Drive for desktop, sync a folder to your PC and point `VIDEO_SOURCE_DIR` or `--source-dir` to it.

The daily batch command:

- scans for `.mp4`, `.mov`, `.m4v`, and `.avi` files
- skips files already recorded as posted
- posts up to `DAILY_POST_COUNT` videos per run
- uses a sidecar text file for captions when present
- can delete the posted video and matching caption sidecar after a successful upload

Caption sidecar example:

- `my-video.mp4`
- `my-video.txt`

If the `.txt` file exists, its content is used as the Facebook description. Otherwise, the file name becomes the caption.

If you enable `--delete-after-post` or set `DELETE_AFTER_POST=true`, the tool removes:

- the uploaded video file
- the matching `.txt` sidecar file, if present

Important: if this folder is synced by Google Drive for desktop, deleting the local file usually deletes it from Drive too.

## Notes

- Facebook publishing support depends on your app, Page permissions, and current Meta review/access setup.
- If you want, the next step can be adding a simple approval queue, scheduler, or dashboard.

## GitHub Actions Schedule

A starter workflow is included at [.github/workflows/daily-post.yml](C:\p practice\FB reel poster\.github\workflows\daily-post.yml).

It is designed for this flow:

- GitHub Actions starts on a schedule
- `rclone` syncs your Google Drive folder into the runner
- the script posts up to 3 videos
- successfully posted videos are deleted locally
- `rclone sync` pushes those deletions back to Google Drive

Set these repository secrets before using it:

- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN`
- `RCLONE_CONFIG`
- `RCLONE_REMOTE_PATH`

Example `RCLONE_REMOTE_PATH`:

```text
gdrive:fb-reels
```

Important:

- GitHub Actions cannot access your local PC's Drive sync folder directly
- the workflow uses a cloud Drive remote through `rclone`
- the sample schedule `0 4 * * *` runs daily at 04:00 UTC, so adjust it to match your preferred India time
# FB-Reel
