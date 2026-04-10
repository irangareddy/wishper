from unittest.mock import Mock, patch

from wishper.context import get_active_app, get_tone


def test_get_tone_for_known_apps():
    assert get_tone("Slack") == "casual, concise messaging"
    assert get_tone("Discord") == "casual, concise messaging"
    assert get_tone("Mail") == "professional, complete sentences"
    assert get_tone("Outlook") == "professional, complete sentences"
    assert get_tone("Cursor") == "technical, code-aware"
    assert get_tone("VS Code") == "technical, code-aware"
    assert get_tone("Visual Studio Code") == "technical, code-aware"
    assert get_tone("Xcode") == "technical, code-aware"
    assert get_tone("Terminal") == "technical, code-aware"
    assert get_tone("iTerm") == "technical, code-aware"
    assert get_tone("iTerm2") == "technical, code-aware"
    assert get_tone("Notes") == "clear, organized notes"
    assert get_tone("Obsidian") == "clear, organized notes"
    assert get_tone("Safari") == "general web content"
    assert get_tone("Chrome") == "general web content"
    assert get_tone("Arc") == "general web content"
    assert get_tone("Messages") == "casual, brief"


def test_get_tone_is_case_insensitive():
    assert get_tone("slack") == get_tone("Slack")
    assert get_tone("vs code") == get_tone("VS Code")


def test_get_tone_for_unknown_app_returns_default():
    assert get_tone("Unknown App") == "clear and natural"


def test_get_active_app_returns_string():
    completed_process = Mock(stdout="Finder\n")
    with patch("wishper.context.subprocess.run", return_value=completed_process):
        result = get_active_app()

    assert isinstance(result, str)

