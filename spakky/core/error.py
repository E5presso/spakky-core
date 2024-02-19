from typing import ClassVar


class SpakkyCoreError(Exception):
    """Core error from all spakky framework"""

    message: ClassVar[str]

    def __repr__(self) -> str:
        return self.message
