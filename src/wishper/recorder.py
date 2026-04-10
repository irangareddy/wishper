"""Audio capture module for microphone recording."""

from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd


class Recorder:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        max_duration: float = 30.0,
        min_duration: float = 0.0,
        silence_threshold: float = -40.0,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration = max_duration
        self.min_duration = min_duration
        self.silence_threshold = silence_threshold

        self._chunks: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._stream: sd.InputStream | None = None
        self._recording = False

    def start(self) -> None:
        if self._recording:
            return

        with self._lock:
            self._chunks = []

        max_frames = (
            int(self.max_duration * self.sample_rate)
            if self.max_duration and self.max_duration > 0
            else None
        )

        def callback(indata: np.ndarray, frames: int, time, status) -> None:
            if status:
                return

            chunk = indata.copy()
            if max_frames is not None:
                with self._lock:
                    current_frames = sum(part.shape[0] for part in self._chunks)
                    remaining = max_frames - current_frames
                    if remaining <= 0:
                        return
                    if chunk.shape[0] > remaining:
                        chunk = chunk[:remaining]
                    self._chunks.append(chunk)
                return

            with self._lock:
                self._chunks.append(chunk)

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=callback,
        )
        self._stream.start()
        self._recording = True

    def stop(self) -> None:
        if not self._recording:
            return

        stream = self._stream
        self._stream = None
        self._recording = False

        if stream is not None:
            stream.stop()
            stream.close()

    def get_audio(self) -> np.ndarray:
        with self._lock:
            if not self._chunks:
                return np.array([], dtype=np.float32)
            chunks = [chunk.copy() for chunk in self._chunks]

        audio = np.concatenate(chunks, axis=0)
        return audio.reshape(-1).astype(np.float32, copy=False)

    def is_silent(self) -> bool:
        audio = self.get_audio()
        if audio.size == 0:
            return True

        rms = float(np.sqrt(np.mean(np.square(audio, dtype=np.float32))))
        if rms <= 0.0:
            return True

        rms_db = 20.0 * np.log10(rms)
        return rms_db < self.silence_threshold
