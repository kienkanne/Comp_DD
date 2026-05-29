import logging
from logging import Logger
import sys
from pathlib import Path


class CustomLogger(Logger):
    def __init__(self, path: str, time_verbose: bool = True):
        super().__init__(name="CustomLogger")
        self.path = path
        self.time_verbose = time_verbose

        self._setup_logger()

    def _setup_logger(self):
        #Creates console + file logger.
        log_file = Path(self.path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        self.setLevel(logging.INFO)

        for handler in self.handlers[:]:
            self.removeHandler(handler)
            handler.close()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        fh = logging.FileHandler(log_file)
        sh = logging.StreamHandler(sys.stdout)
        
        if self.time_verbose:
            fh.setFormatter(formatter)
            sh.setFormatter(formatter)

        self.addHandler(fh)
        self.addHandler(sh)

    def get_path(self) -> str:
        return self.path


class DummyLogger:
    """Fallback logger that mimics basic logging behavior using standard prints."""
    def info(self, message: str):
        print(f"[INFO] {message}")

    def error(self, message: str):
        print(f"[ERROR] {message}")

    def debug(self, message: str):
        print(f"[DEBUG] {message}")

    def warning(self, message: str):
        print(f"[WARNING] {message}")