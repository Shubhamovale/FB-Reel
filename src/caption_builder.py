from textwrap import shorten


def build_caption(video: dict) -> str:
    title = video.get("title", "").strip()
    channel = video.get("channel_title", "").strip()
    description = shorten(
        " ".join(video.get("description", "").split()),
        width=160,
        placeholder="...",
    )

    parts = [title]
    if description:
        parts.append(description)
    if channel:
        parts.append(f"Source inspiration: {channel}")

    parts.append("#food #shorts #reels")
    return "\n\n".join(parts)
