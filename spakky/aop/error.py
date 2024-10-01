from abc import ABC

from spakky.core.error import SpakkyCoreError


class SpakkyAOPError(SpakkyCoreError, ABC): ...


class AspectInheritanceError(SpakkyAOPError):
    message = "Aspect classes must inherit from either IAspect or IAsyncAspect"
