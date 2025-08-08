#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
from typing import List, Optional

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed. Run 'pip install yt-dlp' or 'pip install -r requirements.txt' in the project directory.", file=sys.stderr)
    sys.exit(1)


def build_format_selector(quality: str) -> str:
    quality = quality.lower()
    if quality in {"best", "max"}:
        return (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"
        )
    # Map common labels to maximum height limits
    label_to_height = {
        "2160p": 2160,
        "1440p": 1440,
        "1080p": 1080,
        "720p": 720,
        "480p": 480,
        "360p": 360,
        "240p": 240,
    }
    # If numeric, interpret as height
    if quality.endswith("p") and quality in label_to_height:
        max_h = label_to_height[quality]
    else:
        try:
            max_h = int(quality)
        except ValueError:
            # Fallback to best
            return (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"
            )

    # Prefer MP4/M4A when available, but allow any as fallback under height cap
    return (
        f"bestvideo[height<={max_h}][ext=mp4]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={max_h}]+bestaudio/"
        f"best[height<={max_h}][ext=mp4]/"
        f"best[height<={max_h}]"
    )


def ensure_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def download_to_mp4(
    urls: List[str],
    output_dir: str,
    filename_template: Optional[str],
    quality: str,
    allow_playlist: bool,
    rate_limit: Optional[str],
    quiet: bool,
    cookies_file: Optional[str],
    proxy_url: Optional[str],
) -> int:
    if not ensure_ffmpeg_available():
        print(
            "Warning: ffmpeg not found on PATH. yt-dlp can still download, but merging/remuxing to MP4 may fail.\n"
            "Install ffmpeg: https://ffmpeg.org/download.html (Linux: 'sudo apt-get install ffmpeg').",
            file=sys.stderr,
        )

    os.makedirs(output_dir, exist_ok=True)

    format_selector = build_format_selector(quality)

    ydl_opts = {
        "format": format_selector,
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(output_dir, filename_template or "%(title)s.%(ext)s"),
        "noplaylist": not allow_playlist,
        # Retry some transient errors
        "retries": 5,
        "fragment_retries": 10,
        "ignoreerrors": True,
        "concurrent_fragment_downloads": 5,
        # Prefer no interactive prompts
        "yesplaylist": allow_playlist,
        # Reduce noise if requested
        "quiet": quiet,
        "no_warnings": quiet,
        # Be filesystem-friendly by default
        "restrictfilenames": True,
    }

    if rate_limit:
        # yt-dlp expects rate limit strings like '2M' or integer bytes per second
        ydl_opts["ratelimit"] = rate_limit

    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    if proxy_url:
        ydl_opts["proxy"] = proxy_url

    # Use a remuxer to force MP4 if needed
    ydl_opts["postprocessors"] = [
        {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
    ]

    last_code = 0
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                result_code = ydl.download([url])
                # yt-dlp returns 0 on success, 1 on error
                if result_code != 0:
                    last_code = result_code
            except Exception as exc:  # noqa: BLE001
                print(f"Error downloading {url}: {exc}", file=sys.stderr)
                last_code = 1
    return last_code


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YouTube to MP4 converter using yt-dlp (downloads and remuxes to MP4)",
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more YouTube URLs (video or playlist if --playlist is set)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="downloads",
        help="Output directory (default: downloads)",
    )
    parser.add_argument(
        "-t",
        "--template",
        default=None,
        help="Filename template for yt-dlp outtmpl (default: %%(title)s.%%(ext)s)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        help=(
            "Video quality target. Examples: best, 1080p, 720p, 480p, or a numeric height like 1080. "
            "Defaults to 'best'."
        ),
    )
    parser.add_argument(
        "-p",
        "--playlist",
        action="store_true",
        help="Allow playlist downloads (by default only single videos are downloaded)",
    )
    parser.add_argument(
        "-r",
        "--rate-limit",
        default=None,
        help="Maximum download rate (e.g. 2M, 500K)",
    )
    parser.add_argument(
        "--cookies",
        default=None,
        help="Path to cookies.txt in Netscape format for authenticated downloads",
    )
    parser.add_argument(
        "--proxy",
        default=None,
        help="Proxy URL, e.g. http://127.0.0.1:8888 or socks5://127.0.0.1:1080",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    return download_to_mp4(
        urls=args.urls,
        output_dir=args.output,
        filename_template=args.template,
        quality=args.quality,
        allow_playlist=args.playlist,
        rate_limit=args.rate_limit,
        quiet=args.quiet,
        cookies_file=args.cookies,
        proxy_url=args.proxy,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))