from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable
from spakky.extensions.transactional import (
    AsyncTransactionalAdvisor,
    TransactionalAdvisor,
)
from spakky.plugins.transaction import TransactionPlugin


def test_transaction_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = TransactionPlugin()
    plugin.register(context)

    assert context.beans == {TransactionalAdvisor, AsyncTransactionalAdvisor}
