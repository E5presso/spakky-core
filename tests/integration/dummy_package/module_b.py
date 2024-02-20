from spakky.core.annotation import ClassAnnotation
from spakky.dependency.component import Component


@ClassAnnotation()
class DummyB:
    ...


@Component()
class ComponentB:
    ...
