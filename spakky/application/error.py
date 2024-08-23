from abc import ABC

from spakky.core.error import SpakkyCoreError


class SpakkyApplicationError(SpakkyCoreError, ABC): ...
