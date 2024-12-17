"""
Watcher app to look at pinchflat downloads and upload appropriately
"""
import os
import sqlite3
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
from pathlib import Path

from scripts.automations import InferenceRequest
from scripts.automations import convert_wav
from scripts.automations import run_inference
from webdav3.client import Client
from pydub import AudioSegment
import time

# Configurations
WATCH_DIR = os.environ.get("WATCH_DIR")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR")
DB_PATH = os.environ.get("DB_PATH")

PASSWORD = os.environ.get("NC_PASSWORD")
# TARGET = os.environ.get("NC_INSTRUMENTALS_ONLY_TARGET")
TARGET = os.environ.get("NC_TARGET")
URL = os.environ.get("NC_URL")
USER = os.environ.get("NC_USER")

options = {
    "webdav_hostname": URL,
    "webdav_login": USER,
    "webdav_password": PASSWORD,
}
client = Client(options)
client.verify = True

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Check if a file has already been processed
def is_processed(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_files WHERE file_path = ?", (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Mark a file as processed
def mark_as_processed(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)", (file_path,))
    conn.commit()
    conn.close()


# Transcode .m4a to .mp3 and save to OUTPUT_DIR
def transcode_to_mp3(m4a_path):
    file_name = Path(m4a_path).stem + ".mp3"  # Get filename without extension
    output_path = os.path.join(OUTPUT_DIR, file_name)
    print(f"Transcoding {m4a_path} to {output_path}...")
    try:
        audio = AudioSegment.from_file(m4a_path, format="m4a")
        audio.export(output_path, format="mp3")
        print(f"Transcoding completed: {output_path}")
        return Path(OUTPUT_DIR, file_name)
    except Exception as e:
        print(f"Error transcoding {m4a_path} to MP3: {e}")
        return None

# Placeholder for additional processing logic
def additional_logic(file: Path):
    inference_data = InferenceRequest(filename=str(file))
    data = InferenceRequest(filename=str(file.with_suffix("")))
    # run inference
    run_inference(inference_data)
    # upload the full song
    client.upload_file(remote_path=f"/{TARGET}/{file.name}", local_path=str(file))
    # upload the instrumental
    client.upload_file(remote_path=f"/{TARGET}/{file.stem}_Instruments.mp3", local_path=str(file))

# Logic to process a file
def process_file(file_path):
    print(f"Processing: {file_path}")
    mp3_path = transcode_to_mp3(file_path)
    if mp3_path:
        additional_logic(mp3_path)
        mark_as_processed(file_path)
        print(f"Marked as processed: {file_path}")
    else:
        print(f"Failed to process file: {file_path}")

# Handler for file system events
class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Only process files that match the folder/file.m4a pattern
        if not event.is_directory and event.src_path.endswith(".m4a"):
            file_path = event.src_path
            folder_path = Path(file_path).parent

            # Confirm it's within the correct directory structure
            if Path(folder_path).parent == Path(WATCH_DIR):
                if not is_processed(file_path):
                    print(f"New file detected: {file_path}")
                    process_file(file_path)
                    mark_as_processed(file_path)
                else:
                    print(f"Skipping already processed file: {file_path}")

# Main function to set up the observer
def main():
    init_db()
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    print(f"Watching directory: {WATCH_DIR}")
    
    try:
        observer.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
