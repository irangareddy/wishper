"""Voice command detection and execution."""

from __future__ import annotations

import re


COMMAND_REPLACEMENTS = {
    "exclamation point": "!",
    "exclamation mark": "!",
    "question mark": "?",
    "full stop": ".",
    "semicolon": ";",
    "em dash": " — ",
    "ellipsis": "...",
    "open parenthesis": "(",
    "close parenthesis": ")",
    "open quotes": '"',
    "close quotes": '"',
    "open quote": '"',
    "close quote": '"',
    "new paragraph": "\n\n",
    "new line": "\n",
    "newline": "\n",
    "period": ".",
    "comma": ",",
    "colon": ":",
    "dash": " — ",
    "hyphen": "-",
    "tab": "\t",
}

CAPITALIZE_COMMANDS = {"capitalize", "cap"}
DELETE_COMMANDS = {"delete that", "scratch that"}

COMMAND_PATTERN = re.compile(
    "|".join(
        [
            rf"\b{re.sub(r'\\ ', r'\\s+', re.escape(command))}\b"
            for command in sorted(
                [
                    *COMMAND_REPLACEMENTS.keys(),
                    *CAPITALIZE_COMMANDS,
                    *DELETE_COMMANDS,
                ],
                key=len,
                reverse=True,
            )
        ]
    ),
    flags=re.IGNORECASE,
)
WORD_PATTERN = re.compile(r"[^\W_]+(?:['-][^\W_]+)*", flags=re.UNICODE)


def _trim_output(output: list[str]) -> None:
    while output:
        if output[-1] == "":
            output.pop()
            continue
        trimmed = output[-1].rstrip(" ")
        if trimmed != output[-1]:
            output[-1] = trimmed
        if output[-1] == "":
            output.pop()
            continue
        break


def _delete_previous_clause(output: list[str]) -> None:
    text = "".join(output)
    boundary = max(text.rfind("."), text.rfind("\n"))
    if boundary == -1:
        output[:] = []
        return

    retained = text[: boundary + 1]
    retained = retained.rstrip(" ")
    output[:] = [retained] if retained else []


def _cleanup_spacing(text: str) -> str:
    text = re.sub(r"[ \t]+([,.;:?!])", r"\1", text)
    text = re.sub(r"([(\n]) +", r"\1", text)
    text = re.sub(r' +([)\n])', r"\1", text)
    text = re.sub(r'" +', '"', text)
    text = re.sub(r' +"', '"', text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(" ")


def process_commands(text: str) -> str:
    """Replace supported voice commands with their text equivalents."""
    output: list[str] = []
    position = 0
    capitalize_next = False

    while position < len(text):
        command_match = COMMAND_PATTERN.match(text, position)
        if command_match:
            command = re.sub(r"\s+", " ", command_match.group(0).lower()).strip()

            if command in DELETE_COMMANDS:
                _delete_previous_clause(output)
            elif command in CAPITALIZE_COMMANDS:
                capitalize_next = True
            else:
                output.append(COMMAND_REPLACEMENTS[command])

            position = command_match.end()
            continue

        word_match = WORD_PATTERN.match(text, position)
        if word_match:
            word = word_match.group(0)
            if capitalize_next:
                word = word[:1].upper() + word[1:]
                capitalize_next = False
            output.append(word)
            position = word_match.end()
            continue

        output.append(text[position])
        position += 1

    return _cleanup_spacing("".join(output))
