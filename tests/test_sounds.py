from unittest.mock import patch

from wishper.sounds import SoundPlayer


def test_sound_player_disabled_methods_are_noops():
    player = SoundPlayer(enabled=False)

    with patch("wishper.sounds.subprocess.Popen") as popen:
        player.start_recording()
        player.stop_recording()
        player.done()
        player.error()
        player.play("Glass")

    popen.assert_not_called()


def test_sound_player_enabled_methods_do_not_raise():
    player = SoundPlayer(enabled=True)

    with patch("wishper.sounds.subprocess.Popen", side_effect=FileNotFoundError):
        player.start_recording()
        player.stop_recording()
        player.done()
        player.error()


def test_play_with_valid_sound_name_does_not_raise():
    player = SoundPlayer(enabled=True)

    with patch("wishper.sounds.subprocess.Popen") as popen:
        player.play("Glass")

    popen.assert_called_once_with(["afplay", "/System/Library/Sounds/Glass.aiff"])


def test_play_with_invalid_sound_name_does_not_raise():
    player = SoundPlayer(enabled=True)

    with patch("wishper.sounds.subprocess.Popen"):
        player.play("DefinitelyNotARealSystemSound")

