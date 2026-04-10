"""Active app context detection."""

import subprocess


def get_active_app() -> str:
    """Return the frontmost macOS application name."""
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get name of first application process whose frontmost is true',
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or "Unknown"
    except Exception:
        return "Unknown"


def get_tone(app_name: str) -> str:
    """Return a tone hint for the given application."""
    tones = {
        ("slack", "discord"): "casual, concise messaging",
        ("mail", "outlook"): "professional, complete sentences",
        ("cursor", "vs code", "visual studio code", "xcode", "terminal", "iterm", "iterm2"): "technical, code-aware",
        ("notes", "obsidian"): "clear, organized notes",
        ("safari", "chrome", "arc"): "general web content",
        ("messages",): "casual, brief",
    }
    name = app_name.strip().lower()
    for apps, tone in tones.items():
        if name in apps:
            return tone
    return "clear and natural"
