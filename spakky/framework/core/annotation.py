from typing import Self, final
from dataclasses import dataclass
from abc import ABC, abstractmethod
from spakky.framework.core.generic import T_OBJ

ANNOTATION_DATA: str = "__ANNOTATION_DATA__"


@dataclass
class Annotation(ABC):
    @abstractmethod
    def __call__(self, obj: T_OBJ) -> T_OBJ:
        ...

    @final
    def set_annotation(self, obj: T_OBJ) -> T_OBJ:
        if not hasattr(obj, ANNOTATION_DATA):
            setattr(obj, ANNOTATION_DATA, {})
        annotation_data: dict[type, Self] = getattr(obj, ANNOTATION_DATA, {})
        cls: type[Self] = type(self)
        bases: tuple[type, ...] = cls.__bases__
        for base in bases:
            annotation_data[base] = self
        annotation_data[cls] = self
        setattr(obj, ANNOTATION_DATA, annotation_data)
        return obj

    @final
    @classmethod
    def get_annotation(cls, obj: type) -> Self | None:
        annotation_data: dict[type, Self] = getattr(obj, ANNOTATION_DATA, {})
        return annotation_data.get(cls)

    @final
    @classmethod
    def has_annotation(cls, obj: type) -> bool:
        annotation_data: dict[str, Self] = getattr(obj, ANNOTATION_DATA, {})
        return cls in annotation_data
