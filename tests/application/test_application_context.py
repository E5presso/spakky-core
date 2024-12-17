# pylint: disable=too-many-lines, line-too-long


from abc import abstractmethod
from uuid import UUID, uuid4
from typing import Any, Protocol
from dataclasses import dataclass

import pytest

from spakky.application.application_context import (
    ApplicationContext,
    CannotRegisterNonPodObjectError,
    CircularDependencyGraphDetectedError,
    NoSuchPodError,
    NoUniquePodError,
)
from spakky.application.interfaces.container import IContainer
from spakky.application.interfaces.plugin import IPlugin
from spakky.core.annotation import ClassAnnotation
from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, ICommandUseCase
from spakky.pod.lazy import Lazy
from spakky.pod.pod import Pod
from spakky.pod.primary import Primary
from tests.dummy import dummy_package, second_dummy_package
from tests.dummy.dummy_package import module_a
from tests.dummy.dummy_package.module_a import DummyA, PodA
from tests.dummy.dummy_package.module_b import DummyB, PodB, UnmanagedB
from tests.dummy.dummy_package.module_c import DummyC, PodC
from tests.dummy.second_dummy_package import second_module_a
from tests.dummy.second_dummy_package.second_module_a import SecondDummyA, SecondPodA
from tests.dummy.second_dummy_package.second_module_b import SecondDummyB, SecondPodB
from tests.dummy.second_dummy_package.second_module_c import SecondDummyC, SecondPodC


def test_application_context_register_expect_success() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Pod()
    class SecondSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)
    context.register(SecondSamplePod)


def test_application_context_register_expect_error() -> None:
    class NonPod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonPodObjectError):
        context.register(NonPod)


def test_application_context_get_by_type_singleton_expect_success() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Pod()
    class SecondSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)
    context.register(SecondSamplePod)

    assert context.get(type_=FirstSamplePod).id == context.get(type_=FirstSamplePod).id
    assert context.get(type_=SecondSamplePod).id == context.get(type_=SecondSamplePod).id


def test_application_context_get_by_type_expect_no_such_error() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class SecondSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)

    assert context.get(type_=FirstSamplePod).id == context.get(type_=FirstSamplePod).id
    with pytest.raises(NoSuchPodError):
        assert (
            context.get(type_=SecondSamplePod).id == context.get(type_=SecondSamplePod).id
        )


def test_application_context_get_by_name_expect_success() -> None:
    @Pod()
    class SamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(SamplePod)

    assert isinstance(context.get(SamplePod, "sample_pod"), SamplePod)


def test_application_context_get_by_name_expect_no_such_error() -> None:
    @Pod()
    class SamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class WrongPod: ...

    context: ApplicationContext = ApplicationContext()
    context.register(SamplePod)

    with pytest.raises(NoSuchPodError):
        context.get(type_=WrongPod)


def test_application_context_contains_by_type_expect_true() -> None:
    @Pod()
    class SamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(SamplePod)

    assert context.contains(type_=SamplePod) is True


def test_application_context_contains_by_type_expect_false() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Pod()
    class SecondSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)

    assert context.contains(type_=FirstSamplePod) is True
    assert context.contains(type_=SecondSamplePod) is False


def test_application_context_contains_by_name_expect_true() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)

    assert context.contains(FirstSamplePod, "first_sample_pod") is True


def test_application_context_contains_by_name_expect_false() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class WrongPod: ...

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)

    assert context.contains(FirstSamplePod) is True
    assert context.contains(WrongPod) is False


def test_application_context_get_primary_expect_success() -> None:
    class ISamplePod(Protocol):
        @abstractmethod
        def do(self) -> None: ...

    @Primary()
    @Pod()
    class FirstSamplePod(ISamplePod):
        def do(self) -> None:
            return

    @Pod()
    class SecondSamplePod(ISamplePod):
        def do(self) -> None:
            return

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)
    context.register(SecondSamplePod)

    assert isinstance(context.get(type_=ISamplePod), FirstSamplePod)


def test_application_context_get_primary_expect_no_unique_error() -> None:
    class ISamplePod(Protocol):
        @abstractmethod
        def do(self) -> None: ...

    @Primary()
    @Pod()
    class FirstSamplePod(ISamplePod):
        def do(self) -> None:
            return

    @Primary()
    @Pod()
    class SecondSamplePod(ISamplePod):
        def do(self) -> None:
            return

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSamplePod)
    context.register(SecondSamplePod)

    with pytest.raises(NoUniquePodError):
        context.get(type_=ISamplePod)


def test_application_context_get_dependency_recursive_by_type() -> None:
    @Pod()
    class A:
        def a(self) -> str:
            return "a"

    @Pod()
    class B:
        def b(self) -> str:
            return "b"

    @Pod()
    class C:
        __a: A
        __b: B

        def __init__(self, b: A, a: B) -> None:
            self.__a = b
            self.__b = a

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(B)
    context.register(C)

    assert context.get(type_=C).c() == "ab"


def test_application_context_find() -> None:
    @dataclass
    class Customized(ClassAnnotation): ...

    @Pod()
    class FirstSampleClassMarked: ...

    @Pod()
    @Customized()
    class SecondSampleClass: ...

    @Pod()
    @Customized()
    class ThirdSampleClassMarked: ...

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSampleClassMarked)
    context.register(SecondSampleClass)
    context.register(ThirdSampleClassMarked)

    queried: list[object] = list(
        context.find(lambda x: x.target.__name__.endswith("Marked")).values()
    )
    assert any(isinstance(x, FirstSampleClassMarked) for x in queried)
    assert any(isinstance(x, ThirdSampleClassMarked) for x in queried)

    queried = list(context.find(lambda x: Customized.exists(x.target)).values())
    assert any(isinstance(x, SecondSampleClass) for x in queried)
    assert any(isinstance(x, ThirdSampleClassMarked) for x in queried)


def test_application_context_scan() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package)

    assert context.contains(type_=PodA) is True
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is True


def test_application_context_initialize_with_pacakge() -> None:
    context: ApplicationContext = ApplicationContext(package=dummy_package)

    assert context.contains(type_=PodA) is True
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False


def test_application_context_initialize_with_module() -> None:
    context: ApplicationContext = ApplicationContext(package=module_a)

    assert context.contains(type_=PodA) is True
    assert context.contains(type_=DummyA) is False


def test_application_context_initialize_with_multiple_pacakges() -> None:
    context: ApplicationContext = ApplicationContext(
        package={
            dummy_package,
            second_dummy_package,
        }
    )

    assert context.contains(type_=PodA) is True
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False

    assert context.contains(type_=SecondPodA) is True
    assert context.contains(type_=SecondPodB) is True
    assert context.contains(type_=SecondPodC) is True
    assert context.contains(type_=SecondDummyA) is False
    assert context.contains(type_=SecondDummyB) is False
    assert context.contains(type_=SecondDummyC) is False


def test_application_context_initialize_with_multiple_pacakges_and_modules() -> None:
    context: ApplicationContext = ApplicationContext(
        package={
            dummy_package,
            second_module_a,
        }
    )

    assert context.contains(type_=PodA) is True
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True

    assert context.contains(type_=SecondPodA) is True


def test_application_context_register_unmanaged_factory() -> None:
    class A:
        def a(self) -> str:
            return "A"

    @Pod()
    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    context.register(get_a)

    assert context.contains(A, "get_a") is True
    a: A = context.get(A, "get_a")
    assert isinstance(a, A)
    assert a.a() == "A"


def test_application_context_register_unmanaged_factory_expect_error() -> None:
    class A:
        def a(self) -> str:
            return "A"

    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonPodObjectError):
        context.register(get_a)


def test_application_context_register_plugin() -> None:
    class DummyPlugin(IPlugin):
        def register(self, container: IContainer) -> None:
            container.register(PodA)

    context: ApplicationContext = ApplicationContext()
    context.register_plugin(DummyPlugin())

    assert context.contains(type_=PodA) is True
    assert context.contains(type_=PodB) is False


def test_application_lazy_loading() -> None:
    initialized: bool = False

    @Pod()
    class A:
        def a(self) -> str:
            return "a"

    @Pod()
    class B:
        def b(self) -> str:
            return "b"

    @Pod()
    @Lazy()
    class C:
        __a: A
        __b: B

        def __init__(self, b: A, a: B) -> None:
            self.__a = b
            self.__b = a

            nonlocal initialized
            initialized = True

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(B)
    context.register(C)
    context.start()

    assert initialized is False


def test_application_factory_loading() -> None:
    initialized_count: int = 0

    @Pod()
    class A:
        def a(self) -> str:
            return "a"

    @Pod()
    class B:
        def b(self) -> str:
            return "b"

    @Pod(scope=Pod.Scope.PROTOTYPE)
    class C:
        __a: A
        __b: B

        def __init__(self, b: A, a: B) -> None:
            self.__a = b
            self.__b = a
            nonlocal initialized_count
            initialized_count += 1

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(B)
    context.register(C)

    context.get(C)
    context.get(C)
    context.get(C)

    assert initialized_count == 3


def test_application_raise_error_with_circular_dependency() -> None:
    @Pod()
    class A:
        __b: "B"  # pylint: disable=unused-private-member

        def __init__(self, b: "B") -> None:
            self.__b = b  # pylint: disable=unused-private-member

    @Pod()
    class B:
        __a: "A"  # pylint: disable=unused-private-member

        def __init__(self, a: "A") -> None:
            self.__a = a  # pylint: disable=unused-private-member

    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(B)

    with pytest.raises(CircularDependencyGraphDetectedError):
        context.start()


def test_application_context_scan_with_exclude_packages() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package, exclude={dummy_package})

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is False
    assert context.contains(type_=PodC) is False
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is False


def test_application_context_scan_with_exclude_wildcard() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package, exclude={"tests.dummy.dummy_package.*"})

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is False
    assert context.contains(type_=PodC) is False
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is False


def test_application_context_scan_with_exclude() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package, exclude={module_a})

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is True


def test_application_context_scan_with_exclude_names() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package, exclude={"tests.dummy.dummy_package.module_a"})

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is True


def test_application_context_initialize_with_exclude_packages() -> None:
    context: ApplicationContext = ApplicationContext(
        dummy_package, exclude={dummy_package}
    )

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is False
    assert context.contains(type_=PodC) is False
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is False


def test_application_context_initialize_with_exclude_wildcard() -> None:
    context: ApplicationContext = ApplicationContext(
        dummy_package, exclude={"tests.dummy.dummy_package.*"}
    )

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is False
    assert context.contains(type_=PodC) is False
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is False


def test_application_context_initialize_with_exclude() -> None:
    context: ApplicationContext = ApplicationContext(dummy_package, exclude={module_a})

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is True


def test_application_context_initialize_with_exclude_names() -> None:
    context: ApplicationContext = ApplicationContext(
        dummy_package, exclude={"tests.dummy.dummy_package.module_a"}
    )

    assert context.contains(type_=PodA) is False
    assert context.contains(type_=PodB) is True
    assert context.contains(type_=PodC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is True


def test_application_context_with_optional_argument_type() -> None:
    @Pod()
    class A:
        def a(self) -> str:
            return "a"

    class B:
        def b(self) -> str:
            return "b"

    @Pod()
    class C:
        __a: A
        __b: B | None

        def __init__(self, a: A, b: B | None) -> None:
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + (self.__b.b() if self.__b is not None else "")

    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(C)

    assert context.get(type_=C).c() == "a"


def test_application_context_with_default_argument() -> None:
    @Pod()
    class A:
        def a(self) -> str:
            return "a"

    class B:
        def b(self) -> str:
            return "b"

    @Pod()
    class C:
        __a: A
        __b: B

        def __init__(self, a: A, b: B = B()) -> None:
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(C)

    assert context.get(type_=C).c() == "ab"


def test_application_context_with_generic_collections() -> None:
    @Pod()
    def get_a() -> list[int]:
        return [1, 2, 3]

    @Pod()
    def get_b() -> dict[str, int]:
        return {"a": 1, "b": 2, "c": 3}

    @Pod()
    def get_c() -> set[int]:
        return {1, 2, 3}

    context: ApplicationContext = ApplicationContext()
    context.register(get_a)
    context.register(get_b)
    context.register(get_c)
    context.start()

    assert context.get(list[int]) == [1, 2, 3]
    assert context.get(dict[str, int]) == {"a": 1, "b": 2, "c": 3}
    assert context.get(set[int]) == {1, 2, 3}


def test_application_context_with_no_unique_generic_collections() -> None:
    @Pod()
    def get_a() -> list[int]:
        return [1, 2, 3]

    @Pod()
    def get_b() -> dict[str, int]:
        return {"a": 1, "b": 2, "c": 3}

    @Pod()
    def get_c() -> set[int]:
        return {1, 2, 3}

    @Pod()
    def get_d() -> list[int]:
        return [1, 2, 3, 4]

    context: ApplicationContext = ApplicationContext()
    context.register(get_a)
    context.register(get_b)
    context.register(get_c)
    context.register(get_d)
    context.start()

    assert context.get(list[int], "get_a") == [1, 2, 3]
    assert context.get(dict[str, int]) == {"a": 1, "b": 2, "c": 3}
    assert context.get(set[int]) == {1, 2, 3}
    assert context.get(list[int], "get_d") == [1, 2, 3, 4]


def test_application_context_with_generic_interface() -> None:
    @immutable
    class SignupCommand(Command):
        username: str
        password: str

    class ISignupCommandUseCase(ICommandUseCase[SignupCommand, None], Protocol): ...

    @immutable
    class SigninCommand(Command):
        username: str
        password: str

    class ISigninCommandUseCase(ICommandUseCase[SigninCommand, None], Protocol): ...

    @Pod()
    class SignupCommandUseCase(ISignupCommandUseCase):
        users: dict[str, SignupCommand]

        def __init__(self) -> None:
            self.users = {}

        def execute(self, command: SignupCommand) -> None:
            self.users[command.username] = command

    @Pod()
    class SigninCommandUseCase(ISigninCommandUseCase):
        logs: list[SigninCommand]

        def __init__(self) -> None:
            self.logs = []

        def execute(self, command: SigninCommand) -> None:
            self.logs.append(command)

    context: ApplicationContext = ApplicationContext()
    context.register(SignupCommandUseCase)
    context.register(SigninCommandUseCase)
    context.start()

    signup = context.get(ICommandUseCase[SignupCommand, None])
    signup.execute(SignupCommand(username="user", password="password"))
    signup = context.get(SignupCommandUseCase)
    assert "user" in signup.users

    signin = context.get(ICommandUseCase[SigninCommand, None])
    signin.execute(SigninCommand(username="user", password="password"))
    signin = context.get(SigninCommandUseCase)
    assert len(signin.logs) == 1


def test_application_context_with_multiple_children_list() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class FirstSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SecondSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class ThirdSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SampleService:
        __repositories: list[IRepository]

        def __init__(self, repositories: list[IRepository]) -> None:
            self.__repositories = repositories

        def get(self, id: str) -> list[dict[str, Any]]:
            return [repository.get(id) for repository in self.__repositories]

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSampleRepository)
    context.register(SecondSampleRepository)
    context.register(ThirdSampleRepository)
    context.register(SampleService)
    context.start()

    service = context.get(SampleService)
    assert service.get("1") == [
        {"id": "1"},
        {"id": "1"},
        {"id": "1"},
    ]


def test_application_context_with_multiple_children_set() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class FirstSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SecondSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class ThirdSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SampleService:
        __repositories: set[IRepository]

        def __init__(self, repositories: set[IRepository]) -> None:
            self.__repositories = repositories

        def get(self, id: str) -> list[dict[str, Any]]:
            return [repository.get(id) for repository in self.__repositories]

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSampleRepository)
    context.register(SecondSampleRepository)
    context.register(ThirdSampleRepository)
    context.register(SampleService)
    context.start()

    service = context.get(SampleService)
    assert service.get("1") == [
        {"id": "1"},
        {"id": "1"},
        {"id": "1"},
    ]


def test_application_context_with_multiple_children_dict() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class FirstSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SecondSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class ThirdSampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SampleService:
        __repositories: dict[str, IRepository]

        def __init__(self, repositories: dict[str, IRepository]) -> None:
            self.__repositories = repositories

        def get(self, id: str) -> dict[str, dict[str, Any]]:
            return {
                name: repository.get(id)
                for name, repository in self.__repositories.items()
            }

    context: ApplicationContext = ApplicationContext()
    context.register(FirstSampleRepository)
    context.register(SecondSampleRepository)
    context.register(ThirdSampleRepository)
    context.register(SampleService)
    context.start()

    service = context.get(SampleService)
    assert service.get("1") == {
        "first_sample_repository": {"id": "1"},
        "second_sample_repository": {"id": "1"},
        "third_sample_repository": {"id": "1"},
    }


def test_application_context_with_optional() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    class INoneService(Protocol):
        @abstractmethod
        def none(self) -> None: ...

    @Pod()
    class SampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class NoneService(INoneService):
        def none(self) -> None:
            return

    @Pod()
    class SampleService:
        __repository: IRepository
        __none_service: INoneService | None

        def __init__(
            self,
            repositories: IRepository,
            none_service: INoneService | None,
        ) -> None:
            self.__repository = repositories
            self.__none_service = none_service

        def get(self, id: str) -> dict[str, Any]:
            if self.__none_service is not None:
                self.__none_service.none()
            return self.__repository.get(id)

    context: ApplicationContext = ApplicationContext()
    context.register(SampleRepository)
    context.register(NoneService)
    context.register(SampleService)
    context.start()

    service = context.get(SampleService)
    assert service.get("1") == {"id": "1"}


def test_application_context_with_default() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class SampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SampleService:
        __repository: IRepository

        def __init__(self, repositories: IRepository = SampleRepository()) -> None:
            self.__repository = repositories

        def get(self, id: str) -> dict[str, Any]:
            return self.__repository.get(id)

    context: ApplicationContext = ApplicationContext()
    context.register(SampleService)
    context.start()

    service = context.get(SampleService)
    assert service.get("1") == {"id": "1"}


def test_application_context_with_non_existance_type_or_none() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class SampleRepository(IRepository):
        def get(self, id: str) -> dict[str, Any]:
            return {"id": id}

    @Pod()
    class SampleService:
        __repository: IRepository
        __number: int | None

        def __init__(self, repositories: IRepository, number: int | None) -> None:
            self.__repository = repositories
            self.__number = number

        def get(self, id: str) -> tuple[dict[str, Any], int | None]:
            return self.__repository.get(id), self.__number

    context: ApplicationContext = ApplicationContext()
    context.register(SampleRepository)
    context.register(SampleService)
    context.start()

    service = context.get(SampleService)
    assert service.get("1") == ({"id": "1"}, None)


def test_application_context_with_multiple_children_list_not_exists() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class SampleService:
        __repositories: list[IRepository]

        def __init__(self, repositories: list[IRepository]) -> None:
            self.__repositories = repositories

        def get(self, id: str) -> list[dict[str, Any]]:
            return [repository.get(id) for repository in self.__repositories]

    context: ApplicationContext = ApplicationContext()
    context.register(SampleService)
    with pytest.raises(NoSuchPodError):
        context.start()


def test_application_context_with_multiple_children_set_not_exists() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class SampleService:
        __repositories: set[IRepository]

        def __init__(self, repositories: set[IRepository]) -> None:
            self.__repositories = repositories

        def get(self, id: str) -> list[dict[str, Any]]:
            return [repository.get(id) for repository in self.__repositories]

    context: ApplicationContext = ApplicationContext()
    context.register(SampleService)
    with pytest.raises(NoSuchPodError):
        context.start()


def test_application_context_with_multiple_children_dict_not_exists() -> None:
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

    @Pod()
    class SampleService:
        __repositories: dict[str, IRepository]

        def __init__(self, repositories: dict[str, IRepository]) -> None:
            self.__repositories = repositories

        def get(self, id: str) -> dict[str, dict[str, Any]]:
            return {name: repository.get(id) for name, repository in self.__repositories.items()}

    context: ApplicationContext = ApplicationContext()
    context.register(SampleService)
    with pytest.raises(NoSuchPodError):
        context.start()
