from spakky.application.interfaces.container import IContainer
from spakky.application.interfaces.plugin import IPlugin
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect


class TransactionPlugin(IPlugin):
    def register(self, container: IContainer) -> None:
        container.register(TransactionalAspect)
        container.register(AsyncTransactionalAspect)
