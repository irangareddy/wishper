from pathlib import Path

from wishper.config import Config, DEFAULTS


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_uses_default_config_toml(monkeypatch):
    monkeypatch.chdir(PROJECT_ROOT)

    config = Config.load()

    assert config.audio == DEFAULTS["audio"]
    assert config.hotkey == DEFAULTS["hotkey"]
    assert config.transcription == DEFAULTS["transcription"]
    assert config.cleanup == DEFAULTS["cleanup"]
    assert config.injection == DEFAULTS["injection"]
    assert config.context == DEFAULTS["context"]
    assert config.sounds == DEFAULTS["sounds"]
    assert config.vad == DEFAULTS["vad"]


def test_load_missing_path_uses_defaults():
    config = Config.load("/path/that/does/not/exist/config.toml")

    assert config.audio == DEFAULTS["audio"]
    assert config.hotkey == DEFAULTS["hotkey"]
    assert config.transcription == DEFAULTS["transcription"]
    assert config.cleanup == DEFAULTS["cleanup"]
    assert config.injection == DEFAULTS["injection"]
    assert config.context == DEFAULTS["context"]
    assert config.sounds == DEFAULTS["sounds"]
    assert config.vad == DEFAULTS["vad"]


def test_default_values_are_correct():
    config = Config.load("/path/that/does/not/exist/config.toml")

    assert config.audio == {
        "sample_rate": 16000,
        "channels": 1,
        "dtype": "float32",
        "max_duration": 300,
        "min_duration": 0.4,
        "silence_threshold": -55,
    }
    assert config.hotkey == {
        "key": "cmd_r",
        "mode": "push_to_talk",
    }
    assert config.transcription == {
        "model": "mlx-community/whisper-large-v3-turbo",
        "language": "en",
        "temperature": 0.0,
        "compression_ratio_threshold": 2.4,
        "no_speech_threshold": 0.6,
        "streaming": False,
        "chunk_duration_s": 3.0,
    }
    assert config.cleanup == {
        "enabled": True,
        "model": "mlx-community/Qwen3-0.6B-4bit",
        "max_tokens": 512,
    }
    assert config.injection == {
        "method": "clipboard_paste",
    }
    assert config.context == {
        "enabled": True,
    }
    assert config.sounds == {
        "enabled": True,
    }
    assert config.vad == {
        "threshold": 0.5,
        "min_silence_ms": 700,
    }


def test_all_sections_exist():
    config = Config.load("/path/that/does/not/exist/config.toml")

    assert hasattr(config, "audio")
    assert hasattr(config, "hotkey")
    assert hasattr(config, "transcription")
    assert hasattr(config, "cleanup")
    assert hasattr(config, "injection")
    assert hasattr(config, "context")
    assert hasattr(config, "sounds")
    assert hasattr(config, "vad")

