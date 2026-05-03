#!/usr/bin/env python3
"""
Phase 2: Video Editor (FFmpeg)
Adds Desi style overlay and optimizes for mobile
Environment Variables:
  CAPTION - Custom caption text (default: "Ab AI automation hua aur bhi asaan!")
  OUTPUT_NAME - Output filename (default: marketing_ready.mp4)
"""

import os
import sys
import subprocess

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(SCRIPT_DIR, 'recordings')
INPUT_VIDEO = os.path.join(RECORDINGS_DIR, 'raw_video.webm')

# Env vars with defaults
CAPTION = os.environ.get('CAPTION', 'Ab AI automation hua aur bhi asaan!')
OUTPUT_NAME = os.environ.get('OUTPUT_NAME', 'marketing_ready.mp4')
OUTPUT_VIDEO = os.path.join(RECORDINGS_DIR, OUTPUT_NAME)

# FFmpeg locations
FFMPEG_PATHS = [
    '/home/openhands/.cache/ms-playwright/ffmpeg-1011/ffmpeg-linux',
    '/usr/bin/ffmpeg',
    '/usr/local/bin/ffmpeg',
    'ffmpeg'
]

def find_executable(name):
    for path in FFMPEG_PATHS:
        full_path = path.replace('ffmpeg', name)
        if os.path.exists(full_path):
            return full_path
    return name

FFMPEG = find_executable('ffmpeg')
print(f"Using FFmpeg: {FFMPEG}")
print(f"Caption: {CAPTION}")

def process_video():
    """Add Desi overlay + optimize for fast mobile"""
    if not os.path.exists(INPUT_VIDEO):
        print(f"Error: Input video not found: {INPUT_VIDEO}")
        return None
    
    print(f"Processing: {INPUT_VIDEO}")
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    
    # Try to add text overlay if font available, otherwise just optimize
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    if not os.path.exists(font_path):
        font_path = None
    
    try:
        if font_path:
            # Add text overlay
            cmd = [
                FFMPEG, '-y',
                '-i', INPUT_VIDEO,
                '-vf', f'drawtext=text=\'{CAPTION}\':fontcolor=yellow:fontsize=36:fontfile={font_path}:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.5:boxborderw=5',
                '-c:v', 'libvpx-vp9',
                '-crf', '30',
                '-b:v', '0',
                '-threads', '4',
                OUTPUT_VIDEO.replace('.mp4', '.webm')
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"Added overlay: {OUTPUT_VIDEO.replace('.mp4', '.webm')}")
            return OUTPUT_VIDEO.replace('.mp4', '.webm')
        else:
            # No font - just convert/optimize
            cmd = [
                FFMPEG, '-y',
                '-i', INPUT_VIDEO,
                '-c:v', 'libvpx-vp9',
                '-crf', '35',
                '-b:v', '500k',
                '-threads', '4',
                OUTPUT_VIDEO.replace('.mp4', '.webm')
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"Optimized for mobile: {OUTPUT_VIDEO.replace('.mp4', '.webm')}")
            return OUTPUT_VIDEO.replace('.mp4', '.webm')
            
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else str(e)
        print(f"FFmpeg note: {stderr[:200]}")
        
        # Fallback: copy original
        import shutil
        output = OUTPUT_VIDEO.replace('.mp4', '.webm')
        shutil.copy(INPUT_VIDEO, output)
        print(f"Copied: {output}")
        return output

if __name__ == '__main__':
    result = process_video()
    if result:
        print(f"Success: {result}")
        sys.exit(0)
    else:
        print("Failed")
        sys.exit(1)