from typing import Any, Self
from itertools import chain
from dataclasses import dataclass

from spakky.core.generics import ClassT, FuncT, ObjectT

__ANNOTATION_METADATA__ = "__SPAKKY_ANNOTATION_METADATA__"
__ANNOTATION_TYPEMAP__ = "__SPAKKY_ANNOTATION_TYPEMAP__"


@dataclass
class Annotation:
    def __call__(self, obj: ObjectT) -> ObjectT:
        return self.__set_annotation(obj)

    def __set_annotation(self, obj: ObjectT) -> ObjectT:
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

    @classmethod
    def all(cls, obj: Any) -> list[Self]:
        typemap: dict[type, set[type[Self]]] = cls.__get_typemap(obj)
        metadata: dict[type[Self], list[Self]] = cls.__get_metadata(obj)
        if cls not in typemap:
            return []
        types: set[type[Self]] = typemap[cls]
        annotations: list[Self] = list(chain(*(metadata.get(t) or [] for t in types)))
        return annotations

    @classmethod
    def single(cls, obj: Any) -> Self:
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            raise AnnotationNotFoundError(cls, obj)
        return annotations[0]

    @classmethod
    def single_or_none(cls, obj: Any) -> Self | None:
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            return None
        return annotations[0]

    @classmethod
    def exists(cls, obj: Any) -> bool:
        annotations: list[Self] = cls.all(obj)
        return len(annotations) > 0

    @classmethod
    def __get_typemap(cls, obj: Any) -> dict[type, set[type[Self]]]:
        typemap: dict[type, set[type[Self]]] = getattr(obj, __ANNOTATION_TYPEMAP__, {})
        return typemap

    @classmethod
    def __get_metadata(cls, obj: Any) -> dict[type[Self], list[Self]]:
        metadata: dict[type[Self], list[Self]] = getattr(obj, __ANNOTATION_METADATA__, {})
        return metadata


@dataclass
class ClassAnnotation(Annotation):
    def __call__(self, obj: ClassT) -> ClassT:
        return super().__call__(obj)


@dataclass
class FunctionAnnotation(Annotation):
    def __call__(self, obj: FuncT) -> FuncT:
        return super().__call__(obj)


class AnnotationNotFoundError(Exception):
    __annotation: type[Annotation]
    __obj: Any

    def __init__(self, annotation: type[Annotation], obj: Any) -> None:
        self.__annotation = annotation
        self.__obj = obj

    def __repr__(self) -> str:
        return f"'{self.__obj.__name__}' has no annotation '{self.__annotation.__name__}'"


class MultipleAnnotationFoundError(Exception):
    __annotation: type[Annotation]
    __obj: Any

    def __init__(self, annotation: type[Annotation], obj: Any) -> None:
        self.__annotation = annotation
        self.__obj = obj

    def __repr__(self) -> str:
        return (
            f"Multiple '{self.__annotation.__name__}' "
            + f"annotation found in '{self.__obj.__name__}'."
        )
