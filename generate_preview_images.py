import os
import sys
import subprocess
from pathlib import Path

def generate_preview_images():
    # Determine the script directory
    if getattr(sys, 'frozen', False):
        script_dir = Path(sys._MEIPASS)
    else:
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    # Paths to video directories
    lower_case_path = script_dir / "Source" / "LOWER_CASE"
    upper_case_path = script_dir / "Source" / "UPPER_CASE"

    # Output directory for preview images
    preview_images_dir = script_dir / "PreviewImages"
    preview_images_dir.mkdir(exist_ok=True)

    # Desired output image size
    output_width = 300
    output_height = 300

    # Process lowercase characters
    for video_file in lower_case_path.glob("*.mp4"):
        char = video_file.stem
        output_image = preview_images_dir / f"lower_{char}.png"

        # FFmpeg command to extract the first frame and scale it
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_file),
            "-frames:v", "1",
            "-vf", f"scale={output_width}:{output_height}",
            "-q:v", "2",
            str(output_image)
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Process uppercase characters
    for video_file in upper_case_path.glob("*.mp4"):
        char = video_file.stem
        output_image = preview_images_dir / f"upper_{char}.png"

        # FFmpeg command to extract the first frame and scale it
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_file),
            "-frames:v", "1",
            "-vf", f"scale={output_width}:{output_height}",
            "-q:v", "2",
            str(output_image)
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("Preview images generated successfully.")

if __name__ == "__main__":
    generate_preview_images()
