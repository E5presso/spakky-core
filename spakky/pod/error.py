from abc import ABC

from spakky.core.error import AbstractSpakkyCoreError


class AbstractSpakkyPodError(AbstractSpakkyCoreError, ABC): ...


class PodAnnotationFailedError(AbstractSpakkyPodError):
    message = "Pod annotation failed"


class PodInstantiationFailedError(AbstractSpakkyPodError):
    message = "Pod instantiation failed"
