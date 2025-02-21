from spakky.aspects.transactional import AbstractTransaction
from spakky.pod.annotations.pod import Pod


@Pod()
class TestTransaction(AbstractTransaction):
    def __init__(self, autocommit: bool = True) -> None:
        super().__init__(autocommit=autocommit)

    def initialize(self) -> None:
        return

    def dispose(self) -> None:
        return

    def commit(self) -> None:
        return

    def rollback(self) -> None:
        return
