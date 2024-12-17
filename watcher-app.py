import os
import sqlite3
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging

from scripts.automations import InferenceRequest
from scripts.automations import run_inference
from webdav3.client import Client
from pydub import AudioSegment

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to stdout (captured by Docker)
    ]
)

# Configurations
WATCH_DIR = os.environ.get("WATCH_DIR")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR")
DB_PATH = os.environ.get("DB_PATH")
PASSWORD = os.environ.get("NC_PASSWORD")
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


def init_db():
    """Initialize the SQLite database."""
    logging.info("Initializing the database...")
    try:
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
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing the database: {e}")


def is_processed(file_path):
    """Check if a file has already been processed."""
    logging.debug(f"Checking if file has been processed: {file_path}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_files WHERE file_path = ?", (file_path,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logging.error(f"Database check failed for {file_path}: {e}")
        return False


def mark_as_processed(file_path):
    """Mark a file as processed."""
    logging.debug(f"Marking file as processed: {file_path}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)", (file_path,))
        conn.commit()
        conn.close()
        logging.info(f"File marked as processed: {file_path}")
    except Exception as e:
        logging.error(f"Failed to mark file as processed: {file_path}, Error: {e}")


def transcode_to_mp3(m4a_path):
    """Transcode .m4a to .mp3."""
    file_name = Path(m4a_path).stem + ".mp3"
    output_path = os.path.join(OUTPUT_DIR, file_name)
    logging.info(f"Transcoding file {m4a_path} to {output_path}")
    try:
        audio = AudioSegment.from_file(m4a_path, format="m4a")
        audio.export(output_path, format="mp3")
        logging.info(f"Transcoding completed: {output_path}")
        return Path(output_path)
    except Exception as e:
        logging.error(f"Error transcoding {m4a_path} to MP3: {e}")
        return None


def additional_logic(file: Path):
    """Run inference and upload files."""
    logging.info(f"Running additional logic on file: {file}")
    try:
        inference_data = InferenceRequest(filename=str(file))
        run_inference(inference_data)
        
        # Upload files
        client.upload_file(remote_path=f"/{TARGET}/{file.name}", local_path=str(file))
        logging.info(f"File uploaded: {file}")
        
        client.upload_file(remote_path=f"/{TARGET}/{file.stem}_Instruments.mp3", local_path=str(file))
        logging.info(f"Instrumental uploaded: {file.stem}_Instruments.mp3")
    except Exception as e:
        logging.error(f"Error during additional logic: {e}")


def process_file(file_path):
    """Process a new .m4a file."""
    logging.info(f"Processing file: {file_path}")
    mp3_path = transcode_to_mp3(file_path)
    if mp3_path:
        additional_logic(mp3_path)
        mark_as_processed(file_path)
    else:
        logging.error(f"Failed to process file: {file_path}")


class FileHandler(FileSystemEventHandler):
    """Handler for file system events."""
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".m4a"):
            file_path = event.src_path
            logging.info(f"New file detected: {file_path}")
            if not is_processed(file_path):
                process_file(file_path)
            else:
                logging.info(f"File already processed, skipping: {file_path}")


def main():
    """Main function to watch for new files."""
    if not WATCH_DIR or not OUTPUT_DIR or not DB_PATH:
        logging.critical("Environment variables WATCH_DIR, OUTPUT_DIR, or DB_PATH are missing. Exiting.")
        return

    init_db()

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    logging.info(f"Watching directory: {WATCH_DIR}")

    try:
        observer.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Shutting down observer...")
        observer.stop()
    observer.join()
    logging.info("Observer stopped.")


if __name__ == "__main__":
    main()
