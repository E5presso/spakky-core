from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.plugin import IPlugin
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect
from spakky.plugins.transaction import TransactionPlugin


def test_transaction_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPlugin = TransactionPlugin()
    plugin.register(context)

    assert context.pods == {TransactionalAspect, AsyncTransactionalAspect}
