from typing import Any, Iterable

try:
    from colorama import init as colorama_init
    from termcolor import colored

    colorama_init()
    USE_COLOR = True
except ModuleNotFoundError:
    USE_COLOR = False


def get_color(ratio: float) -> str:
    if ratio >= 0.75:
        return "green"
    elif ratio >= 0.5:
        return "yellow"
    else:
        return "red"


def print_color(
    text: str,
    color: str | None = None,
    on_color: str | None = None,
    attrs: Iterable[str] | None = None,
    *args: Any,
    **kwargs: Any,
) -> None:
    if USE_COLOR:
        print(colored(text, color, on_color, attrs), *args, **kwargs)
    else:
        print(text, *args, **kwargs)
