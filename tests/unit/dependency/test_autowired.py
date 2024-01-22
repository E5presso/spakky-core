from spakky.dependency.autowired import Autowired, autowired


def test_autowired_with_full_annotations() -> None:
    @autowired
    def sample_function(name: str, age: int) -> tuple[str, int]:
        return name, age

    assert Autowired.single(sample_function).dependencies == {"name": str, "age": int}


def test_autowired_with_partial_annotations() -> None:
    @autowired
    def sample_function(name: str, _age) -> str:  # type: ignore
        return name

    assert Autowired.single(sample_function).dependencies == {"name": str}
