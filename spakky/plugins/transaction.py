from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IPodRegistry
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect


class TransactionPlugin(IPluggable):
    def register(self, registry: IPodRegistry) -> None:
        registry.register(TransactionalAspect)
        registry.register(AsyncTransactionalAspect)
