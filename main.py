#!/usr/bin/env python3
"""
Phase 3: Automation Logic
Watches for app updates and triggers capture/processing pipeline
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(SCRIPT_DIR, 'recordings')
CAPTURE_SCRIPT = os.path.join(SCRIPT_DIR, 'capture.js')
PROCESS_SCRIPT = os.path.join(SCRIPT_DIR, 'process_video.py')


class AppChangeHandler(FileSystemEventHandler):
    """Handler for file system changes - triggers video pipeline"""
    
    def __init__(self, on_change_callback):
        self.on_change_callback = on_change_callback
        self.last_trigger = 0
        self.cooldown = 60  # 60 seconds cooldown between triggers
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Check if modified file is in the watched directory
        file_path = event.src_path
        if file_path.endswith(('.js', '.py', '.html', '.css', '.json')):
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_trigger > self.cooldown:
                print(f"File change detected: {file_path}")
                self.last_trigger = current_time
                self.on_change_callback()


def run_capture():
    """Run the capture phase (Node.js)"""
    print("=== Phase 1: Visual Capture ===")
    try:
        result = subprocess.run(
            ['node', CAPTURE_SCRIPT],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Capture failed: {e}")
        return False


def run_processing():
    """Run the video processing phase (Python)"""
    print("=== Phase 2: Video Processing ===")
    try:
        result = subprocess.run(
            ['python3', PROCESS_SCRIPT],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Processing failed: {e}")
        return False


def run_pipeline():
    """Run the full capture + processing pipeline"""
    print("Starting marketing bot pipeline...")
    
    # Phase 1: Capture
    if not run_capture():
        print("Pipeline failed at capture phase")
        return False
    
    # Phase 2: Process
    if not run_processing():
        print("Pipeline failed at processing phase")
        return False
    
    print("Pipeline completed successfully!")
    return True


def watch_for_changes(watch_dir=None):
    """Watch for file changes in the specified directory"""
    if watch_dir is None:
        watch_dir = SCRIPT_DIR
    
    print(f"Watching for changes in: {watch_dir}")
    
    event_handler = AppChangeHandler(on_change_callback=run_pipeline)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Marketing Bot Automation')
    parser.add_argument('--watch', action='store_true', help='Watch for file changes')
    parser.add_argument('--once', action='store_true', help='Run pipeline once and exit')
    parser.add_argument('--dir', type=str, help='Directory to watch (for --watch mode)')
    
    args = parser.parse_args()
    
    if args.watch:
        watch_for_changes(args.dir)
    elif args.once:
        run_pipeline()
    else:
        # Default: run once
        run_pipeline()


if __name__ == '__main__':
    main()