from typing import ClassVar


class SpakkyCoreError(Exception):
    message: ClassVar[str]

    def __repr__(self) -> str:
        return self.message
