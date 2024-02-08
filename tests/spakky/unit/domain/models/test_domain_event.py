from uuid import UUID
from datetime import datetime

from spakky.core.mutability import immutable
from spakky.domain.models.domain_event import DomainEvent


def test_domain_event_equals() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    assert event1 == event2


def test_domain_event_not_equals() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:31:00.000000+09:00"),
    )
    assert event1 != event2


def test_domain_event_not_equals_with_wrong_type() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    @immutable
    class AnotherEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: AnotherEvent = AnotherEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    assert event1 != event2


def test_domain_event_clone() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = event1.clone()
    assert event1 == event2


def test_domain_event_hash() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    event1: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    event2: SampleEvent = SampleEvent(
        event_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime.fromisoformat("2024-01-26T11:32:00.000000+09:00"),
    )
    assert hash(event1) == hash(event2)


def test_domain_event_compare() -> None:
    @immutable
    class SampleEvent(DomainEvent):
        ...

    events: list[SampleEvent] = [
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:30.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:01:00.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:40.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:50.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:20.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:10.00000+09:00"),
        ),
    ]
    events.sort()
    assert events == [
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:10.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:20.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:30.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:40.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:00:50.00000+09:00"),
        ),
        SampleEvent(
            event_id=UUID("12345678-1234-5678-1234-567812345678"),
            timestamp=datetime.fromisoformat("2024-01-01T00:01:00.00000+09:00"),
        ),
    ]

    assert SampleEvent(
        timestamp=datetime.fromisoformat("2024-01-01T00:00:10.00000+09:00")
    ) < SampleEvent(timestamp=datetime.fromisoformat("2024-01-01T00:00:20.00000+09:00"))
    assert SampleEvent(
        timestamp=datetime.fromisoformat("2024-01-01T00:00:10.00000+09:00")
    ) <= SampleEvent(timestamp=datetime.fromisoformat("2024-01-01T00:00:20.00000+09:00"))
    assert SampleEvent(
        timestamp=datetime.fromisoformat("2024-01-01T00:00:20.00000+09:00")
    ) > SampleEvent(timestamp=datetime.fromisoformat("2024-01-01T00:00:10.00000+09:00"))
    assert SampleEvent(
        timestamp=datetime.fromisoformat("2024-01-01T00:00:20.00000+09:00")
    ) >= SampleEvent(timestamp=datetime.fromisoformat("2024-01-01T00:00:10.00000+09:00"))
