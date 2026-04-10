"""Main entry point and hotkey loop."""

from __future__ import annotations

import argparse
import threading
from pathlib import Path

from pynput.keyboard import Key, Listener

from wishper.cleaner import Cleaner
from wishper.config import Config
from wishper.context import get_active_app, get_tone
from wishper.injector import Injector
from wishper.recorder import Recorder
from wishper.transcriber import Transcriber


HOTKEY_MAP = {
    "cmd_r": Key.cmd_r,
}


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description="wishper — local voice-to-text with LLM cleanup")
    parser.add_argument(
        "--config",
        default="config.toml",
        help="Path to TOML config file",
    )
    return parser


def process_recording(
    cfg: Config,
    recorder: Recorder,
    transcriber: Transcriber,
    cleaner: Cleaner,
    injector: Injector,
    process_lock: threading.Lock,
) -> None:
    """Stop recording and run the text pipeline."""
    with process_lock:
        recorder.stop()
        if recorder.is_silent():
            print("[wishper] No speech detected, skipping")
            return

        audio = recorder.get_audio()
        print("[wishper] Transcribing...")
        raw = transcriber.transcribe(audio)
        print(f"[wishper] Raw: {raw}")

        if cfg.context["enabled"]:
            app = get_active_app()
            tone = get_tone(app)
            print(f"[wishper] App: {app} -> Tone: {tone}")
        else:
            tone = ""

        if cfg.cleanup["enabled"]:
            print("[wishper] Cleaning...")
            cleaned = cleaner.clean(raw, app_context=tone)
            print(f"[wishper] Cleaned: {cleaned}")
        else:
            cleaned = raw

        injector.inject(cleaned)
        print("[wishper] Injected!")


def spawn_processing_thread(
    cfg: Config,
    recorder: Recorder,
    transcriber: Transcriber,
    cleaner: Cleaner,
    injector: Injector,
    process_lock: threading.Lock,
) -> None:
    """Run the processing pipeline without blocking the hotkey listener."""

    def runner() -> None:
        try:
            process_recording(
                cfg=cfg,
                recorder=recorder,
                transcriber=transcriber,
                cleaner=cleaner,
                injector=injector,
                process_lock=process_lock,
            )
        except Exception as exc:
            print(f"[wishper] Processing error: {exc}")

    threading.Thread(target=runner, daemon=True).start()


def print_startup_banner(cfg: Config, config_path: str) -> None:
    """Print the startup banner and effective config summary."""
    print("[wishper] Starting wishper")
    print(f"[wishper] Config: {Path(config_path).resolve()}")
    print(
        "[wishper] Audio: "
        f"sample_rate={cfg.audio['sample_rate']}, "
        f"channels={cfg.audio['channels']}, "
        f"max_duration={cfg.audio['max_duration']}, "
        f"min_duration={cfg.audio['min_duration']}, "
        f"silence_threshold={cfg.audio['silence_threshold']}"
    )
    print(
        "[wishper] Hotkey: "
        f"key={cfg.hotkey['key']}, "
        f"mode={cfg.hotkey['mode']}"
    )
    print(
        "[wishper] Transcription: "
        f"model={cfg.transcription['model']}, "
        f"language={cfg.transcription['language']}, "
        f"temperature={cfg.transcription['temperature']}, "
        f"compression_ratio_threshold={cfg.transcription['compression_ratio_threshold']}, "
        f"no_speech_threshold={cfg.transcription['no_speech_threshold']}"
    )
    print(
        "[wishper] Cleanup: "
        f"enabled={cfg.cleanup['enabled']}, "
        f"model={cfg.cleanup['model']}, "
        f"max_tokens={cfg.cleanup['max_tokens']}"
    )
    print(f"[wishper] Injection: method={cfg.injection['method']}")
    print(f"[wishper] Context: enabled={cfg.context['enabled']}")
    print("[wishper] Press Ctrl+C to exit")


def main() -> None:
    """Run the wishper application."""
    args = build_parser().parse_args()
    cfg = Config.load(args.config)

    hotkey_name = cfg.hotkey["key"]
    hotkey = HOTKEY_MAP.get(hotkey_name)
    if hotkey is None:
        raise ValueError(f"Unsupported hotkey: {hotkey_name}")

    hotkey_mode = cfg.hotkey["mode"]
    if hotkey_mode not in {"push_to_talk", "toggle"}:
        raise ValueError(f"Unsupported hotkey mode: {hotkey_mode}")

    recorder = Recorder(
        sample_rate=cfg.audio["sample_rate"],
        channels=cfg.audio["channels"],
        max_duration=cfg.audio["max_duration"],
        min_duration=cfg.audio["min_duration"],
        silence_threshold=cfg.audio["silence_threshold"],
    )
    transcriber = Transcriber(
        model=cfg.transcription["model"],
        language=cfg.transcription["language"],
        temperature=cfg.transcription["temperature"],
        compression_ratio_threshold=cfg.transcription["compression_ratio_threshold"],
        no_speech_threshold=cfg.transcription["no_speech_threshold"],
    )
    cleaner = Cleaner(
        model=cfg.cleanup["model"],
        max_tokens=cfg.cleanup["max_tokens"],
        enabled=cfg.cleanup["enabled"],
    )
    injector = Injector(method=cfg.injection["method"])

    recording_lock = threading.Lock()
    recording_active = False
    toggle_recording = threading.Event()
    process_lock = threading.Lock()

    def start_recording() -> None:
        nonlocal recording_active
        with recording_lock:
            if recording_active:
                return
            recorder.start()
            recording_active = True
        print("[wishper] Recording...")

    def stop_recording_and_process() -> None:
        nonlocal recording_active
        with recording_lock:
            if not recording_active:
                return
            recording_active = False
        spawn_processing_thread(
            cfg=cfg,
            recorder=recorder,
            transcriber=transcriber,
            cleaner=cleaner,
            injector=injector,
            process_lock=process_lock,
        )

    def on_press(key: Key | object) -> None:
        if key != hotkey:
            return

        if hotkey_mode == "push_to_talk":
            start_recording()
            return

        if toggle_recording.is_set():
            toggle_recording.clear()
            stop_recording_and_process()
            return

        toggle_recording.set()
        start_recording()

    def on_release(key: Key | object) -> None:
        if key != hotkey or hotkey_mode != "push_to_talk":
            return
        stop_recording_and_process()

    print_startup_banner(cfg, args.config)

    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        listener.join()
    except KeyboardInterrupt:
        print("\n[wishper] Shutting down...")
        listener.stop()
        recorder.stop()


if __name__ == "__main__":
    main()
