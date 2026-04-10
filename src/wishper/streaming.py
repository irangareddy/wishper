"""Streaming transcription with chunked audio processing."""

from __future__ import annotations

import threading
import time

import mlx_whisper
import numpy as np


class StreamingTranscriber:
    def __init__(
        self,
        model: str,
        language: str,
        temperature: float = 0.0,
        compression_ratio_threshold: float = 2.4,
        no_speech_threshold: float = 0.6,
        chunk_duration_s: float = 3.0,
    ) -> None:
        self.model = model
        self.language = language
        self.temperature = temperature
        self.compression_ratio_threshold = compression_ratio_threshold
        self.no_speech_threshold = no_speech_threshold
        self.chunk_duration_s = chunk_duration_s

    def _transcribe_audio(self, audio: np.ndarray) -> str:
        result = mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=self.model,
            language=self.language,
            temperature=self.temperature,
            compression_ratio_threshold=self.compression_ratio_threshold,
            no_speech_threshold=self.no_speech_threshold,
            condition_on_previous_text=False,
            word_timestamps=False,
        )
        text = result.get("text") if isinstance(result, dict) else None
        return text.strip() if isinstance(text, str) else ""

    def start_streaming(
        self,
        recorder,
        callback,
        stop_event: threading.Event,
    ) -> str:
        text = ""
        last_transcription_at = time.monotonic()

        while not stop_event.wait(timeout=self.chunk_duration_s):
            audio = recorder.get_audio()
            if audio.size < 16000:
                continue

            updated_text = self._transcribe_audio(audio)
            last_transcription_at = time.monotonic()
            if updated_text != text:
                text = updated_text
                callback(text)

        audio = recorder.get_audio()
        if audio.size >= 16000 or time.monotonic() >= last_transcription_at:
            updated_text = self._transcribe_audio(audio) if audio.size else ""
            if updated_text != text:
                text = updated_text
                callback(text)

        return text
