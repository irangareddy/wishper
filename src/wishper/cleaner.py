"""LLM post-processing cleanup module."""

import re

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

        system_prompt = (
            "You are a dictation cleanup assistant. Your ONLY job is to clean raw dictated text.\n\n"
            "Rules:\n"
            "- Remove ALL filler words: um, uh, like, you know, so, basically, actually, I mean, kind of, sort of\n"
            "- Remove false starts and repeated words\n"
            "- Fix grammar and punctuation\n"
            '- Remove leading fillers (do NOT start output with "So," or "Like,")\n'
            "- Keep the FULL original meaning — do not summarize, truncate, or shorten\n"
            "- Keep ALL sentences — do not drop or merge sentences\n"
            "- Output ONLY the cleaned text, nothing else\n"
            "- Do NOT explain, comment, or think out loud\n"
            "- The output should be roughly the same length as the input\n"
            f'{f"- Tone: {app_context}" if app_context else ""}'
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ]

        try:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
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
        output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL)
        output = re.sub(
            r"^(So,?\s*|Like,?\s*|Well,?\s*|I mean,?\s*)",
            "",
            output,
            flags=re.IGNORECASE,
        )
        output = output.strip()
        return output or raw_text
