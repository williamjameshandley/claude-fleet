import queue
import subprocess
import threading

import numpy as np
import sounddevice as sd


RATE = 16000
FRAME = 1280
SILENCE_LEVEL = 60
SILENCE_FRAMES = 15


class Capture:
    def __init__(self, root, frames):
        self.root = root
        self.frames = frames
        self.queue = queue.Queue()
        self.stream = sd.InputStream(
            samplerate=RATE, channels=1, dtype="int16", blocksize=FRAME,
            callback=self._capture,
        )
        self.writer = threading.Thread(target=self._write, daemon=True)

    def start(self):
        self.root.mkdir(parents=True, exist_ok=True)
        self.writer.start()
        self.stream.start()

    def _capture(self, data, _count, _time, _status):
        block = data[:, 0].copy()
        self.queue.put(block)
        self.frames(block)

    def _write(self):
        command = [
            "ffmpeg", "-nostdin", "-loglevel", "warning",
            "-f", "s16le", "-ar", str(RATE), "-ac", "1", "-i", "pipe:0",
            "-c:a", "flac", "-f", "segment", "-segment_time", "300",
            "-segment_format", "ogg", "-reset_timestamps", "1", "-strftime", "1",
            str(self.root / "%Y%m%d-%H%M%S.oga"),
        ]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
            while True:
                encoder.stdin.write(self.queue.get().tobytes())


class Segmenter:
    def __init__(self, complete):
        self.complete = complete
        self.enabled = False
        self.blocks = []
        self.silence = 0

    def feed(self, block):
        if not self.enabled:
            return
        self.blocks.append(block)
        level = np.sqrt(np.mean(block.astype(float) ** 2))
        self.silence = self.silence + 1 if level < SILENCE_LEVEL else 0
        if self.silence == SILENCE_FRAMES and len(self.blocks) > SILENCE_FRAMES:
            speech = self.blocks[:-SILENCE_FRAMES]
            self.blocks = []
            self.silence = 0
            self.complete(np.concatenate(speech).astype("int16").tobytes())
