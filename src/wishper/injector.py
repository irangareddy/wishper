"""Text injection module."""

import subprocess
import time

import pyperclip
from pynput.keyboard import Controller


class Injector:
    """Inject text using clipboard paste, direct keystrokes, or clipboard only."""

    VALID_METHODS = {"clipboard_paste", "keystroke", "clipboard_only"}

    def __init__(self, method="clipboard_paste"):
        if method not in self.VALID_METHODS:
            raise ValueError(f"Invalid injection method: {method}")
        self.method = method
        self._keyboard = Controller()

    def inject(self, text: str) -> bool:
        try:
            if self.method == "clipboard_paste":
                return self._inject_via_clipboard_paste(text)
            if self.method == "keystroke":
                return self._inject_via_keystroke(text)
            if self.method == "clipboard_only":
                return self._inject_via_clipboard_only(text)
            return False
        except Exception:
            return False

    def _inject_via_clipboard_paste(self, text: str) -> bool:
        original_clipboard = pyperclip.paste()
        try:
            pyperclip.copy(text)
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to keystroke "v" using command down',
                ],
                check=True,
            )
            time.sleep(0.1)
            return True
        finally:
            pyperclip.copy(original_clipboard)

    def _inject_via_keystroke(self, text: str) -> bool:
        self._keyboard.type(text)
        return True

    def _inject_via_clipboard_only(self, text: str) -> bool:
        pyperclip.copy(text)
        return True
