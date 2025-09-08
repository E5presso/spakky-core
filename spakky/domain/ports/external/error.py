from abc import ABC

from spakky.domain.ports.error import AbstractSpakkyInfrastructureError


class AbstractSpakkyExternalError(AbstractSpakkyInfrastructureError, ABC): ...
