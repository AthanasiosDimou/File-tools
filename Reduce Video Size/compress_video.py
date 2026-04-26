import argparse
import os
import shutil
import subprocess
import sys


def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def compress_video(input_file: str, output_file: str, crf: int = 28, preset: str = "medium", scale: str | None = None) -> None:
    """Compress a video file using FFmpeg."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vcodec",
        "libx264",
        "-crf",
        str(crf),
        "-preset",
        preset,
        "-acodec",
        "aac",
        "-movflags",
        "+faststart",
    ]

    if scale:
        ffmpeg_cmd.extend(["-vf", scale])

    ffmpeg_cmd.append(output_file)

    print("Running FFmpeg:", " ".join(ffmpeg_cmd))
    completed = subprocess.run(ffmpeg_cmd, capture_output=True)

    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"FFmpeg failed:\n{stderr}")

    original_size = os.path.getsize(input_file) / (1024 * 1024)
    new_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Done! Original size: {original_size:.2f} MB")
    print(f"New size:      {new_size:.2f} MB")
    print(f"Size reduction: {original_size - new_size:.2f} MB ({(1 - new_size / original_size) * 100:.1f}%)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compress a video file using FFmpeg and reduce file size.")
    parser.add_argument("input", help="Path to the input video file")
    parser.add_argument("output", help="Path for the compressed output video file")
    parser.add_argument("--crf", type=int, default=28, help="CRF value (0=best quality, 51=smallest size). Default: 28")
    parser.add_argument("--preset", default="medium", choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], help="FFmpeg encoding preset. Default: medium")
    parser.add_argument("--scale", default=None, help="Optional scale filter, e.g. -1:720 to force 720p height")
    parser.add_argument("--force", action="store_true", help="Overwrite output if it already exists")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not is_ffmpeg_available():
        print("FFmpeg is not available on PATH. Please install FFmpeg and ensure the 'ffmpeg' command is accessible.")
        sys.exit(1)

    if os.path.exists(args.output) and not args.force:
        print(f"Output file already exists: {args.output}")
        print("Use --force to overwrite it.")
        sys.exit(1)

    try:
        compress_video(args.input, args.output, crf=args.crf, preset=args.preset, scale=args.scale)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
