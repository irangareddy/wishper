import importlib
import sys
import types
from unittest.mock import patch

import numpy as np


def load_recorder_module():
    fake_sounddevice = types.SimpleNamespace()

    with patch.dict(sys.modules, {"sounddevice": fake_sounddevice}):
        sys.modules.pop("wishper.recorder", None)
        module = importlib.import_module("wishper.recorder")

    return module


def test_recorder_init_with_custom_params():
    recorder_module = load_recorder_module()

    recorder = recorder_module.Recorder(
        sample_rate=44100,
        channels=2,
        max_duration=12.5,
        min_duration=1.2,
        silence_threshold=-30.0,
    )

    assert recorder.sample_rate == 44100
    assert recorder.channels == 2
    assert recorder.max_duration == 12.5
    assert recorder.min_duration == 1.2
    assert recorder.silence_threshold == -30.0


def test_start_and_stop_without_error():
    recorder_module = load_recorder_module()
    started = False
    stopped = False
    closed = False

    class FakeInputStream:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def start(self):
            nonlocal started
            started = True

        def stop(self):
            nonlocal stopped
            stopped = True

        def close(self):
            nonlocal closed
            closed = True

    recorder_module.sd.InputStream = FakeInputStream
    recorder = recorder_module.Recorder()

    recorder.start()
    recorder.stop()

    assert started is True
    assert stopped is True
    assert closed is True


def test_get_audio_returns_numpy_array():
    recorder_module = load_recorder_module()
    recorder = recorder_module.Recorder()
    recorder._chunks = [
        np.array([[0.1], [0.2]], dtype=np.float32),
        np.array([[0.3]], dtype=np.float32),
    ]

    audio = recorder.get_audio()

    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    np.testing.assert_array_equal(audio, np.array([0.1, 0.2, 0.3], dtype=np.float32))


def test_is_silent_with_empty_audio_returns_true():
    recorder_module = load_recorder_module()
    recorder = recorder_module.Recorder()

    assert recorder.is_silent() is True


def test_get_recent_audio_returns_correct_slice():
    recorder_module = load_recorder_module()
    recorder = recorder_module.Recorder(sample_rate=10)
    recorder._chunks = [np.arange(10, dtype=np.float32).reshape(-1, 1)]

    recent_audio = recorder.get_recent_audio(duration_s=0.3)

    np.testing.assert_array_equal(recent_audio, np.array([7.0, 8.0, 9.0], dtype=np.float32))

