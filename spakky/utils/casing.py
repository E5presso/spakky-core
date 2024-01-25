import re

PATTERN: re.Pattern[str] = re.compile(r"(?<!^)(?=[A-Z])")


def pascal_to_snake(pascal_case: str) -> str:
    return PATTERN.sub("_", pascal_case).lower()


def snake_to_pascal(snake_case: str) -> str:
    return "".join(word.title() for word in snake_case.split("_"))
