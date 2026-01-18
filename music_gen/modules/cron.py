
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

def cleanup_old_files():
    """
    Deletes files in music_gen/generated that are older than 1 day.
    Ignores subdirectories to be safe, or handles them if we structure by user.
    """
    OUTPUT_DIR = "music_gen/generated"
    if not os.path.exists(OUTPUT_DIR):
        return

    # print(f"[{datetime.now()}] Running cleanup...")
    current_time = time.time()
    
    # Walk through all directories in generated/
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            file_path = os.path.join(root, f)
            try:
                creation_time = os.path.getctime(file_path)
                if (current_time - creation_time) > 86400: # 1 day
                    os.remove(file_path)
                    print(f"Deleted old file: {file_path}")
            except Exception as e:
                print(f"Error cleaning {file_path}: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run cleanup every 15 minutes
    scheduler.add_job(cleanup_old_files, 'interval', minutes=15)
    scheduler.start()
    return scheduler
