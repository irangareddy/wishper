"""Voice activity detection using Silero VAD."""

from __future__ import annotations

import numpy as np
import torch


class VoiceActivityDetector:
    def __init__(
        self,
        threshold: float = 0.5,
        min_silence_ms: int = 700,
        sample_rate: int = 16000,
    ) -> None:
        self.threshold = threshold
        self.min_silence_ms = min_silence_ms
        self.sample_rate = sample_rate
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
        )
        self.model.to(torch.device("cpu"))
        self.model.eval()

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        if audio_chunk.size == 0:
            return False

        tensor = torch.from_numpy(audio_chunk.astype(np.float32, copy=False)).flatten()
        with torch.no_grad():
            probability = float(self.model(tensor, self.sample_rate).item())
        return probability > self.threshold

    def detect_silence_after_speech(
        self,
        audio: np.ndarray,
        chunk_size_ms: int = 30,
    ) -> bool:
        if audio.size == 0:
            return False

        self.reset()

        chunk_size = max(1, int(self.sample_rate * chunk_size_ms / 1000))
        speech_detected = False
        silence_duration_ms = 0.0
        flattened = audio.reshape(-1).astype(np.float32, copy=False)

        for start in range(0, flattened.size, chunk_size):
            chunk = flattened[start : start + chunk_size]
            if self.is_speech(chunk):
                speech_detected = True
                silence_duration_ms = 0.0
                continue

            if not speech_detected:
                continue

            silence_duration_ms += (chunk.size / self.sample_rate) * 1000.0
            if silence_duration_ms >= self.min_silence_ms:
                return True

        return False

    def reset(self) -> None:
        self.model.reset_states()
