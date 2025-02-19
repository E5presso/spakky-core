from abc import ABC

from spakky.core.error import SpakkyCoreError


class SpakkyPodError(SpakkyCoreError, ABC): ...


class PodAnnotationFailedError(SpakkyPodError):
    message = "Pod annotation failed"


class PodInstantiationFailedError(SpakkyPodError):
    message = "Pod instantiation failed"
