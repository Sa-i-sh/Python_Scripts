import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from summarizer import MeetingSummarizer

WATCH_FOLDER = "input"
PROCESSED_FOLDER = "processed"
OUTPUT_FOLDER = "output"

class MeetingFileHandler(FileSystemEventHandler):
    def process_file(self, file_path):
        try: 
            if not file_path.endswith(".txt"):
                return
            
            filename = os.path.basename(file_path)
            output_path = os.path.join(OUTPUT_FOLDER, filename.replace('.txt','_summary.json'))

            print(f"Processing: {filename}")

            summarizer = MeetingSummarizer(file_path, output_path)
            summarizer.process()

            os.makedirs(PROCESSED_FOLDER, exist_ok = True)
            shutil.move(file_path, os.path.join(PROCESSED_FOLDER, filename))

            print("Processing complete and file moved.")

        except Exception as e:
            print(f"Error Processing {filename}: {e}")

    def on_create(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

def process_existing_file(handler):
    print("Checking for existing transcripts...")

    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)

    files_found = False

    for filename in os.listdir(WATCH_FOLDER):
        file_path = os.path.join(WATCH_FOLDER, filename)

        if os.path.isfile(file_path) and filename.endswith(".txt"):
            files_found = True
            time.sleep(2)
            handler.process_file(file_path)

    if not files_found:
        print("No existing files found.")

def start_monitoring():
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    event_handler = MeetingFileHandler()

    process_existing_file(event_handler)

    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive = False)
    observer.start()

    print("Watching for new meeting transcripts...")

    try:
        while observer.is_alive():
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    finally:
        observer.join()
        print("Shutdown Complete.")

if __name__ == "__main__":
    start_monitoring()