# 🎬 YouTube Video Clipper

<div align="center">

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macOS-lightgrey.svg)

_A powerful **command-line tool** to extract high-quality clips from YouTube videos_

</div>

---

## ✨ Features

-   ✅ **Interactive CLI**: Guided prompts for video URL, quality, and timestamp selection.
-   🎯 **Precise Clipping**: Extract any segment using `hh:mm:ss`, `mm:ss`, or raw seconds.
-   🖼️ **Thumbnail Preview**: Automatically fetches and displays the highest resolution thumbnail.
-   🧠 **Smart Format Detection**: Combines best audio and video streams using adaptive logic.
-   📦 **Multiple Formats**: Supports MP4, WebM, MKV, and more.
-   🎞️ **4K & High FPS Support**: Handles up to 3840×2160 resolution and 60+ FPS.
-   🔊 **Audio Preservation**: Ensures audio is retained and synced with clipped output.
-   🛠️ **Automatic Optimization**: Re-encodes for best balance of size and quality using FFmpeg.
-   🧾 **Video Metadata Display**: Shows video title, duration, view count, and more.
-   🧩 **Smart Naming**: Auto-generates file names using video title and time range.

---

## 🚀 Usage

### 1. Install Requirements

-   **Python 3.7+**
-   [yt-dlp](https://github.com/yt-dlp/yt-dlp)
-   [ffmpeg](https://ffmpeg.org/)

#### Install dependencies

```sh
pip install yt-dlp
```

**Install ffmpeg:**

```sh
# Windows (Using Chocolatey)
choco install ffmpeg
# Or manually download from:
# https://ffmpeg.org/download.html

# Linux (Debian/Ubuntu)
sudo apt update
sudo apt install ffmpeg

# macOS (Using Homebrew)
brew install ffmpeg
```

### 2. Clone or Download this repository

```sh
git clone https://github.com/yourusername/youtube_video_clipper.git
cd youtube_video_clipper
```

### 3. Run the script

```sh
python youtube_video_clipper.py
```

### 4. Follow the prompts

-   **Enter the YouTube video URL**
-   **Select the desired video quality**
-   **Enter the start and end times for your clip**

### 5. Find your clip in the `downloads/` folder!

---

### 🖥️ Example Session

```
🎬 YouTube Video Clipper
==================================================
📺 Enter YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

🔍 Fetching video information...

🎥 Video: Rick Astley - Never Gonna Give You Up (Official Music Video)
👤 Channel: Rick Astley
⏱️ Duration: 00:03:33.000
👁️ Views: 1,234,567,890
🖼️ Thumbnail: https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg

📺 Available video qualities:
------------------------------------------------------------------------------------------
#   Quality      Codec           Audio    Bitrate    Full Video Size
------------------------------------------------------------------------------------------
1   1080p        avc1.640028     ✓        2500k      120 MB
2   720p         avc1.4d401f     ✓        1500k      80 MB
...

📝 Select quality (1-2): 1

⏰ Enter start time (hh:mm:ss or seconds): 0:30
⏰ Enter end time (hh:mm:ss or seconds): 1:00

⬇️ Downloading video section (0:30 - 1:00)...
🔄 Optimizing video for high quality...

✅ Clip created successfully!
📁 File: downloads/Rick_Astley_-_Never_Gonna_Give_You_Up_0-30_to_1-00.mp4
📊 Size: 5.2 MB

🎉 All done! Enjoy your clip!
💝 Thank you for using YouTube Clipper by Mohit Khairnar!
```

---

### 📝 Output

-   All clips are saved in the `downloads/` directory.
-   Filenames include the video title and selected time range.

---

### ⚙️ How It Works

1. **Fetches video info** using `yt-dlp`.
2. **Lists available formats** (resolution, codec, audio, size).
3. **Prompts for start/end times** and validates input.
4. **Downloads only the selected section** using `yt-dlp --download-sections`.
5. **Re-encodes the clip** with `ffmpeg` for optimal quality and compatibility.
6. **Cleans up** temporary files.

---

### 🛠️ Troubleshooting

-   **yt-dlp or ffmpeg not found?**  
    Make sure both are installed and available in your system's PATH.
-   **Permission errors?**  
    Try running with elevated permissions or check the `downloads/` directory permissions.
-   **Unsupported video?**  
    Some videos may have restrictions or unsupported formats.

---

### 🙏 Credits

-   [yt-dlp](https://github.com/yt-dlp/yt-dlp)
-   [ffmpeg](https://ffmpeg.org/)
-   Inspired by the need for quick, high-quality YouTube video clipping.

---

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Enjoy your YouTube clips!
