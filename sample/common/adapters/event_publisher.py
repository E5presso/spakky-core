from sample.common.aspects.logging import AsyncLogging
from spakky.core.interfaces.equatable import EquatableT
from spakky.dependency.autowired import autowired
from spakky.dependency.component import Component
from spakky.domain.interfaces.event_publisher import IAsyncEventPublisher
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


@Component()
class AsyncInMemoryEventPublisher(IAsyncEventPublisher):
    events: list[DomainEvent]

    @autowired
    def __init__(self) -> None:
        super().__init__()
        self.events = []

    @AsyncLogging()
    async def publish(self, aggregate: AggregateRoot[EquatableT]) -> None:
        self.events.extend(aggregate.events)
        aggregate.clear_events()
