import sys
from abc import ABC
from typing import Any, final
from dataclasses import dataclass

from spakky.core.error import SpakkyCoreError
from spakky.core.types import AnyT, ClassT, FuncT

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


__ANNOTATION_METADATA__ = "__spakky_annotation_metadata__"


@dataclass
class Annotation(ABC):
    def __call__(self, obj: AnyT) -> AnyT:
        return self.__set_metadata(obj)

    @final
    def __set_metadata(self, obj: AnyT) -> AnyT:
        metadata: dict[type[Self], list[Self]] = self.__get_metadata(obj)
        for base_type in type(self).mro():
            if base_type not in metadata:
                metadata[base_type] = []
            metadata[base_type].append(self)
        setattr(obj, __ANNOTATION_METADATA__, metadata)
        return obj

    @final
    @classmethod
    def __get_metadata(cls, obj: Any) -> dict[type[Self], list[Self]]:
        metadata: dict[type[Self], list[Self]] = getattr(obj, __ANNOTATION_METADATA__, {})
        return metadata

    @final
    @classmethod
    def all(cls, obj: Any) -> list[Self]:
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        annotations: list[Self] = metadata.get(cls, [])
        return annotations

    @final
    @classmethod
    def get(cls, obj: Any) -> Self:
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        if cls not in metadata:
            raise AnnotationNotFoundError(cls, obj)
        annotations: list[Self] = metadata.get(cls, [])
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        return annotations[0]

    @final
    @classmethod
    def get_or_none(cls, obj: Any) -> Self | None:
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        if cls not in metadata:
            return None
        annotations: list[Self] = metadata.get(cls, [])
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        return annotations[0]

    @final
    @classmethod
    def get_or_default(cls, obj: Any, default: Self) -> Self:
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        if cls not in metadata:
            return default
        annotations: list[Self] = metadata.get(cls, [])
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        return annotations[0]

    @final
    @classmethod
    def exists(cls, obj: Any) -> bool:
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        return cls in metadata


@dataclass
class ClassAnnotation(Annotation, ABC):
    def __call__(self, obj: ClassT) -> ClassT:
        return super().__call__(obj)


@dataclass
class FunctionAnnotation(Annotation, ABC):
    def __call__(self, obj: FuncT) -> FuncT:
        return super().__call__(obj)


class AnnotationNotFoundError(SpakkyCoreError):
    message = "Object has no specified annotation"


class MultipleAnnotationFoundError(SpakkyCoreError):
    message = "Multiple annotation found in object"
