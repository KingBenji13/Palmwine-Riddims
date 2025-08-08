# yt2mp4

Simple YouTube-to-MP4 downloader using yt-dlp.

## Prerequisites
- Python 3.9+
- ffmpeg installed and on PATH (for merging/remuxing to MP4)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python yt2mp4.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Options:
- `-o, --output`: Output directory (default: `downloads`)
- `-t, --template`: Filename template (default: `%(title)s.%(ext)s`)
- `-q, --quality`: Quality target (e.g. `best`, `1080p`, `720p`, or numeric like `1080`)
- `-p, --playlist`: Allow playlist downloads
- `-r, --rate-limit`: Rate limit (e.g. `2M`, `500K`)
- `--cookies`: Path to cookies.txt (Netscape format) for authenticated downloads
- `--proxy`: Proxy URL (e.g. `http://127.0.0.1:8888` or `socks5://127.0.0.1:1080`)
- `--quiet`: Reduce verbosity

Examples:
```bash
# Best available quality
python yt2mp4.py -q best "https://youtu.be/VIDEO"

# Cap at 1080p
python yt2mp4.py -q 1080p "https://youtu.be/VIDEO"

# Playlist to a custom folder, custom filename template
python yt2mp4.py -p -o out -t "%(playlist_index)03d - %(title)s.%(ext)s" "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Use cookies for age/captcha/region-locked videos
python yt2mp4.py --cookies ~/.config/yt-cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"

# Use a proxy
python yt2mp4.py --proxy http://127.0.0.1:8888 "https://youtu.be/VIDEO"
```

## Exporting YouTube cookies
If YouTube asks you to sign in/verify, export cookies from your browser in Netscape format and pass them with `--cookies`.
- See yt-dlp docs: `https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies`
- Or use `--cookies-from-browser` directly with yt-dlp if preferred.

## Notes
- If MP4 streams are not available, the tool downloads best available and remuxes to MP4 (requires ffmpeg).
- For Linux, install ffmpeg with: `sudo apt-get install ffmpeg`.