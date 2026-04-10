"""Configuration management."""

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


DEFAULTS = {
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "dtype": "float32",
        "max_duration": 300,
        "min_duration": 0.4,
        "silence_threshold": -55,
    },
    "hotkey": {
        "key": "cmd_r",
        "mode": "push_to_talk",
    },
    "transcription": {
        "model": "mlx-community/whisper-large-v3-turbo",
        "language": "en",
        "temperature": 0.0,
        "compression_ratio_threshold": 2.4,
        "no_speech_threshold": 0.6,
        "streaming": False,
        "chunk_duration_s": 3.0,
    },
    "cleanup": {
        "enabled": True,
        "model": "mlx-community/Qwen3-0.6B-4bit",
        "max_tokens": 512,
    },
    "injection": {
        "method": "clipboard_paste",
    },
    "context": {
        "enabled": True,
    },
    "sounds": {
        "enabled": True,
    },
    "vad": {
        "threshold": 0.5,
        "min_silence_ms": 700,
    },
}


@dataclass
class Config:
    audio: dict
    hotkey: dict
    transcription: dict
    cleanup: dict
    injection: dict
    context: dict
    sounds: dict
    vad: dict

    @classmethod
    def load(cls, path: str = "config.toml") -> "Config":
        config_path = Path(path)
        data = DEFAULTS
        if config_path.exists():
            with config_path.open("rb") as f:
                loaded = tomllib.load(f)
            data = {section: loaded.get(section, values).copy() for section, values in DEFAULTS.items()}
        else:
            data = {section: values.copy() for section, values in DEFAULTS.items()}
        return cls(**data)
