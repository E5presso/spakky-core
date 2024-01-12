from abc import ABC
from typing import Any, Self, final
from itertools import chain
from dataclasses import dataclass

from spakky.core.generics import ClassT, FuncT, ObjectT

__ANNOTATION_METADATA__ = "__SPAKKY_ANNOTATION_METADATA__"
__ANNOTATION_TYPEMAP__ = "__SPAKKY_ANNOTATION_TYPEMAP__"


@dataclass
class Annotation(ABC):
    """`Annotation` is a class-based decorator to write custom metadata to Any objects.\n
    It is pretty much same with Java's Annotation.\n
    You have to inherit this class with @dataclass decorator.\n
    Here is a example.
    ```python
    @dataclass
    class CustomAnnotation(Annotation):
        name: str
        age: int

    @CustomAnnotation(name="John", age=30)
    def sample() -> None:
        ...

    @CustomAnnotation(name="John", age=30)
    class SampleClass:
        ...
    ```
    """

    def __call__(self, obj: ObjectT) -> ObjectT:
        """Annotate object

        Args:
            obj (ObjectT): Object to annotate

        Returns:
            ObjectT: Annotated object
        """
        return self.__set_annotation(obj)

    @final
    def __set_annotation(self, obj: ObjectT) -> ObjectT:
        """Allocate Annotation to object

        Args:
            obj (ObjectT): Object to allocate annotation

        Returns:
            ObjectT: Annotated object
        """
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
        """Get all annotations in object.
        ```python
        @dataclass
        class CustomAnnotation(Annotation):
            name: str
            age: int

        @CustomAnnotation(name="John", age=30)
        @CustomAnnotation(name="Sarah", age=28)
        def sample() -> None:
            ...

        annotations: list[CustomAnnotation] = CustomAnnotation.all(sample)
        assert annotations == [
            CustomAnnotation(name="Sarah", age=28),
            CustomAnnotation(name="John", age=30),
        ]
        ```

        Args:
            obj (Any): Object to get all annotations

        Returns:
            list[Self]: All annotations
        """
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
        """Get single annotation in object.
        ```python
        @dataclass
        class CustomAnnotation(Annotation):
            name: str
            age: int

        @CustomAnnotation(name="John", age=30)
        def sample() -> None:
            ...

        annotation: CustomAnnotation = CustomAnnotation.single(sample)
        ```

        Args:
            obj (Any): object to get single annotation

        Raises:
            MultipleAnnotationFoundError: When multiple annotations found in object.
            AnnotationNotFoundError: When annotation not found in object.

        Returns:
            Self: Single annotation found in object
        """
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            raise AnnotationNotFoundError(cls, obj)
        return annotations[0]

    @final
    @classmethod
    def single_or_none(cls, obj: Any) -> Self | None:
        """Get single annotation in object.
        Returns None when annotation not found in object.
        ```python
        @dataclass
        class CustomAnnotation(Annotation):
            name: str
            age: int

        @CustomAnnotation(name="John", age=30)
        def sample() -> None:
            ...

        annotation: CustomAnnotation | None = CustomAnnotation.single_or_none(sample)
        ```

        Args:
            obj (Any): object to get single annotation or None

        Raises:
            MultipleAnnotationFoundError: When multiple annotations found in object.

        Returns:
            Self | None: Single annotation or None
        """
        annotations: list[Self] = cls.all(obj)
        if len(annotations) > 1:
            raise MultipleAnnotationFoundError(cls, obj)
        if len(annotations) == 0:
            return None
        return annotations[0]

    @final
    @classmethod
    def exists(cls, obj: Any) -> bool:
        """Check if annotation exists in object
        ```python
        @dataclass
        class CustomAnnotation(Annotation):
            name: str
            age: int

        @CustomAnnotation(name="John", age=30)
        def sample() -> None:
            ...

        def not_annotated() -> None:
            ...

        assert CustomAnnotation.exists(sample) is True
        assert CustomAnnotation.exists(not_annotated) is False
        ```

        Args:
            obj (Any): object to check exists

        Returns:
            bool: True if annotation exists in object.
        """
        annotations: list[Self] = cls.all(obj)
        return len(annotations) > 0

    @final
    @classmethod
    def __get_typemap(cls, obj: Any) -> dict[type, set[type[Self]]]:
        """Get typemap from object to mimic liskov substitution for annotation.

        Args:
            obj (Any): Object to get typemap

        Returns:
            dict[type, set[type[Self]]]: Typemap from object
        """
        typemap: dict[type, set[type[Self]]] = getattr(obj, __ANNOTATION_TYPEMAP__, {})
        return typemap

    @final
    @classmethod
    def __get_metadata(cls, obj: Any) -> dict[type[Self], list[Self]]:
        """Get actual metadata from object.

        Args:
            obj (Any): Object to get actual metadata

        Returns:
            dict[type[Self], list[Self]]: Metadata from object
        """
        metadata: dict[type[Self], list[Self]] = getattr(obj, __ANNOTATION_METADATA__, {})
        return metadata


@dataclass
class ClassAnnotation(Annotation, ABC):
    """`ClassAnnotation` is a class-based decorator to write\n
    custom metadata to `type` objects.\n
    It is pretty much same with Java's Annotation.\n
    You have to inherit this class with @dataclass decorator.\n
    Here is a example.
    ```python
    @dataclass
    class CustomAnnotation(ClassAnnotation):
        name: str
        age: int

    @CustomAnnotation(name="John", age=30)
    class SampleClass:
        ...

    # @CustomAnnotation(name="John", age=30) <- Can't annotate with ClassAnnotation
    # def sample() -> None:
    #     ...
    ```
    """

    def __call__(self, obj: ClassT) -> ClassT:
        """Annotate class

        Args:
            obj (ClassT): Class to annotate

        Returns:
            ClassT: Annotated class
        """
        return super().__call__(obj)


@dataclass
class FunctionAnnotation(Annotation, ABC):
    """`FunctionAnnotation` is a class-based decorator to write\n
    custom metadata to `Callable` objects.\n
    It is pretty much same with Java's Annotation.\n
    You have to inherit this class with @dataclass decorator.\n
    Here is a example.
    ```python
    @dataclass
    class CustomAnnotation(FunctionAnnotation):
        name: str
        age: int

    @CustomAnnotation(name="John", age=30)
    def sample() -> None:
        ...

    # @CustomAnnotation(name="John", age=30) <- Can't annotate with FunctionAnnotation
    # class SampleClass:
    #     ...
    ```
    """

    def __call__(self, obj: FuncT) -> FuncT:
        """Annotate function

        Args:
            obj (FuncT): function to annotate

        Returns:
            FuncT: Annotated function
        """
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
