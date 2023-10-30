from re import sub


def pascal_to_snake(pascal_case: str) -> str:
    return sub(r"(?<!^)(?=[A-Z])", "_", pascal_case).lower()


def snake_to_pascal(snake_case: str) -> str:
    words: list[str] = snake_case.split("_")
    return "".join(x.title() for x in words)


def camel_to_snake(camel_case: str) -> str:
    pascal_case: str = camel_case[0].upper() + camel_case[1:]
    return sub(r"(?<!^)(?=[A-Z])", "_", pascal_case).lower()


def snake_to_camel(snake_case: str) -> str:
    words: list[str] = snake_case.split("_")
    return words[0] + "".join(x.title() for x in words[1:])


def kebab_to_snake(kebab_case: str) -> str:
    words: list[str] = kebab_case.split("-")
    return "_".join(x for x in words)


def snake_to_kebab(snake_case: str) -> str:
    words: list[str] = snake_case.split("_")
    return "-".join(x for x in words)
