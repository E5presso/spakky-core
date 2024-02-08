from spakky.core.interfaces.equatable import EquatableT
from spakky.dependency.component import Component
from spakky.domain.interfaces.event_publisher import IAsyncEventPublisher
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


@Component()
class AsyncMemoryEventPublisher(IAsyncEventPublisher):
    events: list[DomainEvent]

    def __init__(self) -> None:
        super().__init__()
        self.events = []

    async def publish(self, aggregate: AggregateRoot[EquatableT]) -> None:
        self.events.extend(aggregate.events)
        aggregate.clear_events()
