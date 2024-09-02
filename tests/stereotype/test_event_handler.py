from spakky.core.mutability import immutable
from spakky.domain.models.domain_event import DomainEvent
from spakky.stereotype.event_handler import EventHandler, EventRoute, on_event


def test_event_handler() -> None:
    @EventHandler()
    class SampleEventHandler: ...

    class NonAnnotated: ...

    assert EventHandler.get_or_none(SampleEventHandler) is not None
    assert EventHandler.get_or_none(NonAnnotated) is None


def test_event_handler_with_callback() -> None:
    @immutable
    class SampleEvent(DomainEvent): ...

    @EventHandler()
    class SampleEventHandler:
        @on_event(SampleEvent)
        async def handle(self, event: SampleEvent) -> None:
            print(event)

    class NonAnnotated: ...

    assert EventHandler.get_or_none(SampleEventHandler) is not None
    assert EventRoute.get_or_none(SampleEventHandler.handle) is not None
    assert EventRoute.get_or_none(SampleEventHandler().handle) is not None
    assert EventHandler.get_or_none(NonAnnotated) is None
