import dataclasses
import json
import logging
import threading
from event import Events

SECRECTS_FILE = ".secret"
DATA_FILE = "events_data.json"

write_lock = threading.Lock()


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, set):
            return list(o)
        else:
            return super().default(o)


def flush_data_to_disk(events: Events) -> None:
    try:
        # If the lock it taken it is ok to just move on and wait for the next flush
        with write_lock:
            with open(DATA_FILE, "w") as f:
                json.dump(events, f, cls=EnhancedJSONEncoder)
    except:
        logging.warning("Failed to write data to the disk")


def load_data_from_disk() -> dict:
    try:
        with open(DATA_FILE, "r") as f:
            data = f.read()
            if data:
                return json.loads(data)
    except:
        logging.exception("Failed to read data from the disk")
        return dict()


def load_secrets() -> dict:
    with open(SECRECTS_FILE) as f:
        return json.load(f)
