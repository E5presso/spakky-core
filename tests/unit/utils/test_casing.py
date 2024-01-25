from spakky.utils.casing import pascal_to_snake, snake_to_pascal


def test_pascal_to_snake() -> None:
    assert pascal_to_snake("PascalCase") == "pascal_case"
    assert pascal_to_snake("ISampleClass") == "i_sample_class"


def test_snake_to_pascal() -> None:
    assert snake_to_pascal("snake_case") == "SnakeCase"
