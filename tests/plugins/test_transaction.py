from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect
from spakky.plugins.transaction import TransactionPlugin


def test_transaction_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = TransactionPlugin()
    plugin.register(context)

    assert context.pods == {TransactionalAspect, AsyncTransactionalAspect}
