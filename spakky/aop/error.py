from abc import ABC

from spakky.core.error import AbstractSpakkyCoreError


class AbstractSpakkyAOPError(AbstractSpakkyCoreError, ABC): ...


class AspectInheritanceError(AbstractSpakkyAOPError):
    message = "Aspect classes must inherit from either IAspect or IAsyncAspect"
