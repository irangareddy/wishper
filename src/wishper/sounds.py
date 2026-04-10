"""Audio feedback using macOS system sounds."""

from __future__ import annotations

import subprocess


class SoundPlayer:
    """Play simple non-blocking feedback sounds."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def play(self, sound_name: str) -> None:
        """Play a system sound asynchronously when enabled."""
        if not self.enabled:
            return

        try:
            subprocess.Popen(["afplay", f"/System/Library/Sounds/{sound_name}.aiff"])
        except FileNotFoundError:
            pass

    def start_recording(self) -> None:
        """Play the recording-start sound."""
        self.play("Tink")

    def stop_recording(self) -> None:
        """Play the recording-stop sound."""
        self.play("Pop")

    def done(self) -> None:
        """Play the success sound."""
        self.play("Glass")

    def error(self) -> None:
        """Play the error sound."""
        self.play("Basso")
