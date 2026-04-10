import mlx_whisper
import numpy as np


class Transcriber:
    def __init__(
        self,
        model: str,
        language: str,
        temperature: float,
        compression_ratio_threshold: float,
        no_speech_threshold: float,
    ) -> None:
        self.model = model
        self.language = language
        self.temperature = temperature
        self.compression_ratio_threshold = compression_ratio_threshold
        self.no_speech_threshold = no_speech_threshold

    def transcribe(self, audio: np.ndarray) -> str:
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
