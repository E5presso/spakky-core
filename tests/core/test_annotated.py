# import inspect
# from typing import Annotated
# from dataclasses import dataclass


# def test_annotated() -> None:
#     @dataclass
#     class Qualifier:
#         name: str

#     def test(qualifier: Annotated[str, Qualifier("test")]) -> None:
#         assert qualifier == "test"

#     test("test")
#     [qualifier] = list(inspect.signature(test).parameters.values())
#     annotated = qualifier.annotation
#     assert isinstance(annotated, str) is True
