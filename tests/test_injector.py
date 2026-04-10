import importlib
import sys
import types
from unittest.mock import patch

import pytest


class ClipboardStub:
    def __init__(self):
        self.value = ""

    def copy(self, text):
        self.value = text

    def paste(self):
        return self.value


def load_injector_module(clipboard):
    fake_pyperclip = types.SimpleNamespace(copy=clipboard.copy, paste=clipboard.paste)

    class FakeController:
        def type(self, text):
            self.typed = text

    fake_keyboard_module = types.SimpleNamespace(Controller=FakeController)
    fake_pynput = types.SimpleNamespace(keyboard=fake_keyboard_module)

    with patch.dict(
        sys.modules,
        {
            "pyperclip": fake_pyperclip,
            "pynput": fake_pynput,
            "pynput.keyboard": fake_keyboard_module,
        },
    ):
        sys.modules.pop("wishper.injector", None)
        module = importlib.import_module("wishper.injector")

    return module


def test_injector_init_with_valid_methods():
    injector_module = load_injector_module(ClipboardStub())

    for method in injector_module.Injector.VALID_METHODS:
        injector = injector_module.Injector(method=method)
        assert injector.method == method


def test_injector_init_with_invalid_method_raises_value_error():
    injector_module = load_injector_module(ClipboardStub())

    with pytest.raises(ValueError, match="Invalid injection method"):
        injector_module.Injector(method="invalid")


def test_clipboard_only_inject_puts_text_in_clipboard():
    clipboard = ClipboardStub()
    injector_module = load_injector_module(clipboard)
    injector = injector_module.Injector(method="clipboard_only")

    result = injector.inject("hello world")

    assert result is True
    assert clipboard.paste() == "hello world"
