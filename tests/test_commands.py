import pytest

from wishper.commands import process_commands


@pytest.mark.parametrize(
    ("spoken", "expected"),
    [
        ("Hello period", "Hello."),
        ("Hello comma how are you question mark", "Hello, how are you?"),
        ("new paragraph Hello", "\n\nHello"),
        ("capitalize hello", "Hello"),
        ("This is wrong scratch that This is right", "This is right"),
        ("open parenthesis note close parenthesis", "(note)"),
        ("Hello exclamation mark", "Hello!"),
        ("one semicolon two", "one; two"),
        ("add a dash here", "add a — here"),
        ("Hello ellipsis", "Hello..."),
        ("", ""),
        ("No commands here", "No commands here"),
        ("PERIOD", "."),
        (
            "new line capitalize hello comma world exclamation mark",
            "\nHello, world!",
        ),
        (
            "open quote hello comma world close quote period",
            '"hello, world".',
        ),
    ],
)
def test_process_commands(spoken, expected):
    assert process_commands(spoken) == expected


def test_process_commands_is_case_insensitive():
    assert process_commands("Hello PERIOD") == "Hello."
    assert process_commands("Hello CoMmA world QuEsTiOn MaRk") == "Hello, world?"

