from uuid import UUID
from datetime import datetime

from spakky.architecture.model.domain_event import DomainEvent
from spakky.core.mutability import immutable


def test_domain_event_equals() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = SampleEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    assert event1 == event2


def test_domain_event_not_equals_with_wrong_type() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    @immutable
    class AnotherEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: AnotherEvent = AnotherEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    assert event1 != event2


def test_domain_event_copy() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = event1.copy()
    assert event1 == event2


def test_domain_event_hash() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = SampleEvent(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    assert hash(event1) == hash(event2)
