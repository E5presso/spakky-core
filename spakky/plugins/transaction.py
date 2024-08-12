from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect


class TransactionPlugin(IPluggable):
    def register(self, registry: IRegistry) -> None:
        registry.register_injectable(TransactionalAspect)
        registry.register_injectable(AsyncTransactionalAspect)
