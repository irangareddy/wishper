# wishper

Local voice-to-text with LLM cleanup for macOS, powered by MLX.

A free, open-source alternative to [Wispr Flow](https://wisprflow.ai/). Runs entirely on your Mac — no cloud, no subscription, no data leaves your machine.

## How it works

```
Hold right Cmd → Speak → Release → Clean text appears in your active app
```

**Pipeline:** Mic capture → MLX Whisper (ASR) → LLM cleanup (filler removal, grammar, tone) → Paste

The LLM adapts output tone based on the active app — casual in Slack, professional in Mail, technical in your IDE.

## Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- Accessibility permissions (System Settings → Privacy & Security → Accessibility)

## Install

```bash
git clone https://github.com/irangareddy/wishper.git
cd wishper
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Usage

```bash
wishper
```

Hold **Right Cmd** to record, release to transcribe and paste. That's it.

### Options

```bash
wishper --config path/to/config.toml
```

## Configuration

Edit `config.toml` to customize:

```toml
[transcription]
model = "mlx-community/whisper-large-v3-turbo"  # any mlx-whisper model
language = "en"

[cleanup]
enabled = true
model = "mlx-community/Qwen3-0.6B-4bit"  # any mlx-lm model
max_tokens = 512

[hotkey]
key = "cmd_r"        # right command key
mode = "push_to_talk" # or "toggle"

[injection]
method = "clipboard_paste"  # clipboard_paste, keystroke, clipboard_only
```

### Swap models

Any model from [mlx-community](https://huggingface.co/mlx-community) works as a drop-in replacement:

**ASR models:**
| Model | Config value | Notes |
|---|---|---|
| Whisper Large v3 Turbo | `mlx-community/whisper-large-v3-turbo` | Default, best balance |
| Whisper Tiny | `mlx-community/whisper-tiny` | Fastest, lower accuracy |
| Distil-Whisper | `mlx-community/distil-whisper-large-v3` | Fast, English only |

**LLM cleanup models:**
| Model | Config value | Notes |
|---|---|---|
| Qwen3 0.6B | `mlx-community/Qwen3-0.6B-4bit` | Default, fast |
| SmolLM2 135M | `mlx-community/SmolLM2-135M-4bit` | Ultra-fast, basic cleanup |
| Qwen3 1.7B | `mlx-community/Qwen3-1.7B-4bit` | Better quality, slower |
| Local model | `/path/to/your/model` | Any mlx-lm compatible model |

Set `enabled = false` under `[cleanup]` to skip LLM cleanup and get raw Whisper output.

## Architecture

```
src/wishper/
├── main.py         # CLI entry + hotkey loop
├── recorder.py     # Mic capture (sounddevice, 16kHz float32)
├── transcriber.py  # MLX Whisper inference
├── cleaner.py      # LLM post-processing (filler removal, grammar, tone)
├── injector.py     # Text paste (clipboard + Cmd+V)
├── context.py      # Active app detection + tone mapping
└── config.py       # TOML config management
```

## Benchmarks (Apple Silicon)

Tested with macOS `say`-generated speech:

| Metric | Result |
|---|---|
| ASR speed (whisper-tiny) | 29x realtime |
| LLM cleanup (Qwen3 0.6B) | ~0.6s per pass |
| Total pipeline | ~1.3s for 19s of audio |

## Roadmap

- [ ] Voice Activity Detection (auto-detect speech end)
- [ ] Streaming transcription (show text as you speak)
- [ ] Voice commands ("new paragraph", "period", "delete that")
- [ ] Personal dictionary
- [ ] Menu bar app (native macOS UI)
- [ ] PyPI publishing (`pip install wishper`)

## License

MIT
