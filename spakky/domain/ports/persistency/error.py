from abc import ABC

from spakky.domain.ports.error import AbstractSpakkyInfrastructureError


class AbstractSpakkyPersistencyError(AbstractSpakkyInfrastructureError, ABC): ...
