from dataclasses import dataclass

from spakky.core.annotation import ClassAnnotation


@dataclass
class Primary(ClassAnnotation):
    """`Primary` annotation make component as primary component\n
    If you implement some classes from parent class and get component by parent type\n
    Context will raises `NoUniqueComponentError`\n
    Then you can mark some child class as Primary,
    context will return that primary component.
    """

    ...
