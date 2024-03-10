import sys
from abc import ABC
from typing import Any, final
from itertools import chain
from dataclasses import dataclass

from spakky.core.error import SpakkyCoreError
from spakky.core.types import AnyT, ClassT, FuncT

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


__ANNOTATION_METADATA__ = "__SPAKKY_ANNOTATION_METADATA__"
__ANNOTATION_TYPEMAP__ = "__SPAKKY_ANNOTATION_TYPEMAP__"


@dataclass
class Annotation(ABC):
    def __call__(self, obj: AnyT) -> AnyT:
        return self.__set_annotation(obj)

    @final
    def __set_annotation(self, obj: AnyT) -> AnyT:
        typemap: dict[type, set[type[Self]]] = self.__get_typemap(obj)
        metadata: dict[type[Self], list[Self]] = self.__get_metadata(obj)
        for parent in type(self).mro():
            if parent not in typemap:
                typemap[parent] = set()
            typemap[parent].add(type(self))
        if type(self) not in metadata:
            metadata[type(self)] = []
        metadata[type(self)].append(self)
        setattr(obj, __ANNOTATION_TYPEMAP__, typemap)
        setattr(obj, __ANNOTATION_METADATA__, metadata)
        return obj

    @final
    @classmethod
    def all(cls, obj: Any) -> list[Self]:
        typemap: dict[type, set[type[Self]]] = cls.__get_typemap(obj)
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        if cls not in typemap:
            return []
        types: set[type[Self]] = typemap[cls]
        annotations: list[Self] = list(chain(*(metadata.get(t) or [] for t in types)))
        return annotations

    @final
    @classmethod
    def single(cls, obj: Any) -> Self:
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            raise AnnotationNotFoundError(cls, obj)
        return annotations[0]

    @final
    @classmethod
    def single_or_none(cls, obj: Any) -> Self | None:
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            return None
        return annotations[0]

    @final
    @classmethod
    def single_or_default(cls, obj: Any, default: Self) -> Self:
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            return default
        return annotations[0]

    @final
    @classmethod
    def contains(cls, obj: Any) -> bool:
        annotations: list[Self] = cls.all(obj)
        return len(annotations) > 0

    @final
    @classmethod
    def __get_typemap(cls, obj: Any) -> dict[type, set[type[Self]]]:
        typemap: dict[type, set[type[Self]]] = getattr(obj, __ANNOTATION_TYPEMAP__, {})
        return typemap

    @final
    @classmethod
    def __get_metadata(cls, obj: Any) -> dict[type[Self], list[Self]]:
        metadata: dict[type[Self], list[Self]] = getattr(obj, __ANNOTATION_METADATA__, {})
        return metadata


class AnnotationNotFoundError(SpakkyCoreError):
    message = "Object has no specified annotation"


class MultipleAnnotationFoundError(SpakkyCoreError):
    message = "Multiple annotation found in object"


@dataclass
class ClassAnnotation(Annotation, ABC):
    def __call__(self, obj: ClassT) -> ClassT:
        return super().__call__(obj)


@dataclass
class FunctionAnnotation(Annotation, ABC):
    def __call__(self, obj: FuncT) -> FuncT:
        return super().__call__(obj)
