# Reduce Video Size

A small Python utility for compressing large video files using FFmpeg.

## Files

- `compress_video.py` - command-line script to compress a video using FFmpeg with CRF, preset, and optional scaling.

## Prerequisites

1. Install FFmpeg and make sure the `ffmpeg` executable is available on your system PATH.
   - Windows: download from https://ffmpeg.org/download.html and add the `bin` folder to PATH.
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
2. No Python packages are required for `compress_video.py`.
   The script calls the FFmpeg executable directly, so `pip install -r requirements.txt` is not needed unless you want the optional `ffmpeg-python` wrapper.

## Usage

Run the script with an input file and output path:

```bash
python compress_video.py input.mp4 output.mp4
```

### Optional arguments

- `--crf`: CRF quality setting (0=best quality, 51=smallest size). Default is `28`.
- `--preset`: FFmpeg encoding preset. Default is `medium`.
- `--scale`: optional video scaling filter, e.g. `-1:720` to downscale to 720p.
- `--force`: overwrite the output file if it already exists.

### Examples

Compress with default settings:

```bash
python compress_video.py large_video.mp4 compressed_video.mp4
```

Compress using a faster preset:

```bash
python compress_video.py large_video.mp4 compressed_video.mp4 --preset fast
```

Compress and downscale to 720p:

```bash
python compress_video.py large_video.mp4 compressed_video.mp4 --crf 30 --scale -1:720
```

## Notes

- This script streams the video through FFmpeg and does not load the entire file into memory, making it suitable for large files.
- If the file is still too large, increase the `--crf` value or use `--scale` to reduce resolution.
