r"""Watch raw CSV files and run the logged ETL after each saved change.

Run with:
    .\.store\Scripts\python.exe watch_pipeline.py
"""

import argparse
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from etl.load import main as run_etl
from pipeline_logs import run_with_logging


BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "Data" / "raw"
WATCHED_FILES = {"train.csv", "stores.csv", "features.csv"}


class DebouncedPipelineRunner:
    """Combine a burst of editor save events into one pipeline run."""

    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.timer = None
        self.run_lock = threading.Lock()
        self.timer_lock = threading.Lock()

    def schedule(self, changed_file: Path):
        with self.timer_lock:
            if self.timer is not None:
                self.timer.cancel()

            print(f"Detected change in {changed_file.name}; updating in {self.delay_seconds:.0f}s...")
            self.timer = threading.Timer(self.delay_seconds, self.run_pipeline)
            self.timer.daemon = True
            self.timer.start()

    def run_pipeline(self):
        # A second save can happen while an earlier update is still running.
        # In that case, the next scheduled run starts after this lock releases.
        with self.run_lock:
            print("\nStarting automatic Supabase update...")
            run_with_logging(run_etl, run_label="raw_csv_change")


class RawCsvHandler(FileSystemEventHandler):
    """Schedule the pipeline for create, edit, rename, or replacement events."""

    def __init__(self, runner: DebouncedPipelineRunner):
        self.runner = runner

    def on_any_event(self, event):
        if event.is_directory:
            return

        event_paths = [Path(event.src_path)]
        if getattr(event, "dest_path", None):
            event_paths.append(Path(event.dest_path))

        for event_path in event_paths:
            if event_path.name.lower() in WATCHED_FILES:
                self.runner.schedule(event_path)
                return


def main():
    parser = argparse.ArgumentParser(description="Automatically run the ETL after raw CSV changes.")
    parser.add_argument(
        "--run-on-start",
        action="store_true",
        help="Run one update immediately before watching for later changes.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds to wait after the latest save event (default: 3).",
    )
    args = parser.parse_args()

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"Raw-data directory not found: {RAW_DATA_DIR}")

    runner = DebouncedPipelineRunner(args.delay)
    observer = Observer()
    observer.schedule(RawCsvHandler(runner), str(RAW_DATA_DIR), recursive=False)
    observer.start()

    print(f"Watching {RAW_DATA_DIR} for changes to: {', '.join(sorted(WATCHED_FILES))}")
    print("Press Ctrl+C to stop watching.")

    if args.run_on_start:
        runner.run_pipeline()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
