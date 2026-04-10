"""LLM post-processing cleanup module."""

from mlx_lm import generate, load


class Cleaner:
    def __init__(
        self,
        model="mlx-community/Qwen3-0.6B-4bit",
        max_tokens=512,
        enabled=True,
    ):
        self.max_tokens = max_tokens
        self.enabled = enabled
        self.model = None
        self.tokenizer = None
        if enabled:
            self.model, self.tokenizer = load(model)

    def clean(self, raw_text: str, app_context: str = "") -> str:
        if not self.enabled:
            return raw_text

        if not raw_text:
            return ""

        tone_line = f"Tone: {app_context}\n" if app_context else ""
        prompt = (
            f"<|im_start|>system\nYou clean dictated text. "
            f"Remove filler words (um, uh, like, you know), fix grammar and punctuation. "
            f"Output ONLY the cleaned text, nothing else. "
            f"No explanations, no thinking, no commentary. /no_think\n"
            f"{tone_line}<|im_end|>\n"
            f"<|im_start|>user\n{raw_text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        try:
            output = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=self.max_tokens,
            )
        except Exception:
            return raw_text

        # Strip chat template artifacts and thinking tags
        for tag in ("<|im_end|>", "<|im_start|>", "<|endoftext|>"):
            output = output.split(tag)[0]
        # Remove <think>...</think> blocks from Qwen3
        import re
        output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL)
        output = output.strip()
        return output or raw_text
