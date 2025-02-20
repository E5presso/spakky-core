from abc import abstractmethod
from dataclasses import dataclass
from typing import Annotated, Any, Protocol, runtime_checkable
from uuid import UUID, uuid4

import pytest

from spakky.application.application_context import (
    ApplicationContext,
    CircularDependencyGraphDetectedError,
    NoSuchPodError,
    NoUniquePodError,
)
from spakky.core.annotation import ClassAnnotation
from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, ICommandUseCase
from spakky.pod.annotations.lazy import Lazy
from spakky.pod.annotations.pod import Pod, PodInstantiationFailedError
from spakky.pod.annotations.primary import Primary
from spakky.pod.annotations.qualifier import Qualifier
from spakky.pod.interfaces.container import CannotRegisterNonPodObjectError


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
    context.add(FirstSamplePod)
    context.add(SecondSamplePod)


def test_application_context_register_expect_error() -> None:
    class NonPod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonPodObjectError):
        context.add(NonPod)


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
    context.add(FirstSamplePod)
    context.add(SecondSamplePod)

    assert context.get(type_=FirstSamplePod).id == context.get(type_=FirstSamplePod).id
    assert (
        context.get(type_=SecondSamplePod).id == context.get(type_=SecondSamplePod).id
    )


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
    context.add(FirstSamplePod)

    assert context.get(type_=FirstSamplePod).id == context.get(type_=FirstSamplePod).id
    with pytest.raises(NoSuchPodError):
        assert (
            context.get(type_=SecondSamplePod).id
            == context.get(type_=SecondSamplePod).id
        )


def test_application_context_get_by_name_expect_success() -> None:
    @Pod()
    class SamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.add(SamplePod)

    assert isinstance(context.get(name="sample_pod", type_=SamplePod), SamplePod)


def test_application_context_get_by_name_expect_no_such_error() -> None:
    @Pod()
    class SamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class WrongPod: ...

    context: ApplicationContext = ApplicationContext()
    context.add(SamplePod)

    with pytest.raises(NoSuchPodError):
        context.get(type_=WrongPod)


def test_application_context_contains_by_type_expect_true() -> None:
    @Pod()
    class SamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.add(SamplePod)

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
    context.add(FirstSamplePod)

    assert context.contains(type_=FirstSamplePod) is True
    assert context.contains(type_=SecondSamplePod) is False


def test_application_context_contains_by_name_expect_false() -> None:
    @Pod()
    class FirstSamplePod:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class WrongPod: ...

    context: ApplicationContext = ApplicationContext()
    context.add(FirstSamplePod)

    assert context.contains(type_=FirstSamplePod) is True
    assert context.contains(type_=WrongPod) is False


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
    context.add(FirstSamplePod)
    context.add(SecondSamplePod)

    assert isinstance(context.get(type_=ISamplePod), FirstSamplePod)


def test_application_context_get_qualified_expect_success() -> None:
    class ISamplePod(Protocol):
        @abstractmethod
        def do(self) -> str: ...

    @Pod()
    class FirstSamplePod(ISamplePod):
        def do(self) -> str:
            return "first"

    @Pod()
    class SecondSamplePod(ISamplePod):
        def do(self) -> str:
            return "second"

    @Pod()
    class SampleService:
        __pod: ISamplePod

        def __init__(
            self,
            pod: Annotated[
                ISamplePod,
                Qualifier(lambda pod: pod.name.startswith("second")),
            ],
        ) -> None:
            self.__pod = pod

        def do(self) -> str:
            return self.__pod.do()

    context: ApplicationContext = ApplicationContext()
    context.add(FirstSamplePod)
    context.add(SecondSamplePod)
    context.add(SampleService)
    context.start()

    service = context.get(type_=SampleService)
    assert service.do() == "second"


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
    context.add(FirstSamplePod)
    context.add(SecondSamplePod)

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
    context.add(A)
    context.add(B)
    context.add(C)
    context.start()

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
    context.add(FirstSampleClassMarked)
    context.add(SecondSampleClass)
    context.add(ThirdSampleClassMarked)

    queried: list[object] = list(
        context.find(lambda x: x.target.__name__.endswith("Marked"))
    )
    assert any(isinstance(x, FirstSampleClassMarked) for x in queried)
    assert any(isinstance(x, ThirdSampleClassMarked) for x in queried)

    queried = list(context.find(lambda x: Customized.exists(x.target)))
    assert any(isinstance(x, SecondSampleClass) for x in queried)
    assert any(isinstance(x, ThirdSampleClassMarked) for x in queried)


def test_application_context_register_unmanaged_factory() -> None:
    class A:
        def a(self) -> str:
            return "A"

    @Pod()
    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    context.add(get_a)

    assert context.contains(type_=A) is True
    a: A = context.get(name="get_a", type_=A)
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
        context.add(get_a)


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
    context.add(A)
    context.add(B)
    context.add(C)
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
    context.add(A)
    context.add(B)
    context.add(C)

    context.get(type_=C)
    context.get(type_=C)
    context.get(type_=C)

    assert initialized_count == 3


def test_application_raise_error_with_circular_dependency() -> None:
    @runtime_checkable
    class IA(Protocol):
        def a(self) -> str: ...

    @runtime_checkable
    class IB(Protocol):
        def b(self) -> str: ...

    @Pod()
    class A(IA):
        __b: IB

        def __init__(self, b: IB) -> None:
            self.__b = b

        def a(self) -> str:
            return self.__b.b()

    @Pod()
    class B(IB):
        __a: IA

        def __init__(self, a: IA) -> None:
            self.__a = a

        def b(self) -> str:
            return self.__a.a()

    context: ApplicationContext = ApplicationContext()
    context.add(A)
    context.add(B)

    with pytest.raises(CircularDependencyGraphDetectedError):
        context.start()


def test_application_context_with_generic_interface() -> None:
    @immutable
    class SignupCommand(Command):
        username: str
        password: str

    class ISignupCommandUseCase(ICommandUseCase[SignupCommand, None], Protocol):
        pass

    @immutable
    class SigninCommand(Command):
        username: str
        password: str

    class ISigninCommandUseCase(ICommandUseCase[SigninCommand, None], Protocol):
        pass

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
    context.add(SignupCommandUseCase)
    context.add(SigninCommandUseCase)
    context.start()

    signup = context.get(type_=ICommandUseCase[SignupCommand, None])
    signup.execute(SignupCommand(username="user", password="password"))
    signup = context.get(type_=SignupCommandUseCase)
    assert "user" in signup.users

    signin = context.get(type_=ICommandUseCase[SigninCommand, None])
    signin.execute(SigninCommand(username="user", password="password"))
    signin = context.get(type_=SigninCommandUseCase)
    assert len(signin.logs) == 1


def test_application_context_with_multiple_children_list_not_exists() -> None:
    @runtime_checkable
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
    context.add(SampleService)
    with pytest.raises(PodInstantiationFailedError):
        context.start()


def test_application_context_with_multiple_children_set_not_exists() -> None:
    @runtime_checkable
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
    context.add(SampleService)
    with pytest.raises(PodInstantiationFailedError):
        context.start()


def test_application_context_with_multiple_children_dict_not_exists() -> None:
    @runtime_checkable
    class IRepository(Protocol):
        @abstractmethod
        def get(self, id: str) -> dict[str, Any]: ...

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
    context.add(SampleService)
    with pytest.raises(PodInstantiationFailedError):
        context.start()
