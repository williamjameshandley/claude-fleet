import json
import os
import wave
from pathlib import Path
from time import time


ROOT = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "agent-fleet/alan"


class Archive:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.events = self.root / "events.jsonl"

    def record(self, composition, event, **fields):
        item = {"ts": time(), "composition": composition.id, "event": event, **fields}
        with self.events.open("a") as stream:
            stream.write(json.dumps(item, separators=(",", ":")) + "\n")

    def audio(self, composition, data, rate):
        directory = self.root / "compositions" / composition.id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{time():.6f}.wav"
        with wave.open(str(path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(rate)
            output.writeframes(data)
        return path
