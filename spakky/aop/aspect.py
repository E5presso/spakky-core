from types import MethodType
from typing import Any
from inspect import getmembers
from dataclasses import field, dataclass

from spakky.aop.error import SpakkyAOPError
from spakky.aop.pointcut import (
    After,
    AfterRaising,
    AfterReturning,
    Around,
    AsyncAfter,
    AsyncAfterRaising,
    AsyncAfterReturning,
    AsyncAround,
    AsyncBefore,
    Before,
)
from spakky.bean.bean import Bean
from spakky.core.types import AsyncFunc, ClassT, Func


class CannotDeclareSamePointcutError(SpakkyAOPError):
    message = "Cannot declare same pointcut in aspect multiple times"


class RunnableAspect:
    instance: object
    before: Func | None
    after_returning: Func | None
    after_raising: Func | None
    after: Func | None
    around: Func | None
    next: Func

    def __init__(
        self,
        instance: object,
        before: Func | None,
        after_returning: Func | None,
        after_raising: Func | None,
        after: Func | None,
        around: Func | None,
        next: Func,
    ) -> None:
        self.instance = instance
        self.before = before
        self.after_returning = after_returning
        self.after_raising = after_raising
        self.after = after
        self.around = around
        self.next = next

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.before is not None:
            self.before(self.instance, *args, **kwargs)
        try:
            if self.around is not None:
                result: Any = self.around(self.instance, self.next, *args, **kwargs)
            else:
                result: Any = self.next(*args, **kwargs)
            if self.after_returning is not None:
                self.after_returning(self.instance, result)
            return result
        except Exception as e:
            if self.after_raising is not None:
                self.after_raising(self.instance, e)
            raise
        finally:
            if self.after is not None:
                self.after(self.instance)


class AsyncRunnableAspect:
    instance: object
    before: AsyncFunc | None
    after_returning: AsyncFunc | None
    after_raising: AsyncFunc | None
    after: AsyncFunc | None
    around: AsyncFunc | None
    next: AsyncFunc

    def __init__(
        self,
        instance: object,
        before: AsyncFunc | None,
        after_returning: AsyncFunc | None,
        after_raising: AsyncFunc | None,
        after: AsyncFunc | None,
        around: AsyncFunc | None,
        next: AsyncFunc,
    ) -> None:
        self.instance = instance
        self.before = before
        self.after_returning = after_returning
        self.after_raising = after_raising
        self.after = after
        self.around = around
        self.next = next

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.before is not None:
            await self.before(self.instance, *args, **kwargs)
        try:
            if self.around is not None:
                result = await self.around(self.instance, self.next, *args, **kwargs)
            else:
                result = await self.next(*args, **kwargs)
            if self.after_returning is not None:
                await self.after_returning(self.instance, result)
            return result
        except Exception as e:
            if self.after_raising is not None:
                await self.after_raising(self.instance, e)
            raise
        finally:
            if self.after is not None:
                await self.after(self.instance)


@dataclass
class Aspect(Bean):
    before: Func | None = field(init=False, default=None)
    after_returning: Func | None = field(init=False, default=None)
    after_raising: Func | None = field(init=False, default=None)
    after: Func | None = field(init=False, default=None)
    around: Func | None = field(init=False, default=None)

    def __call__(self, obj: ClassT) -> ClassT:
        for _, method in getmembers(obj):
            if Before.contains(method):
                if self.before is not None:
                    raise CannotDeclareSamePointcutError
                self.before = method
            if AfterReturning.contains(method):
                if self.after_returning is not None:
                    raise CannotDeclareSamePointcutError
                self.after_returning = method
            if AfterRaising.contains(method):
                if self.after_raising is not None:
                    raise CannotDeclareSamePointcutError
                self.after_raising = method
            if After.contains(method):
                if self.after is not None:
                    raise CannotDeclareSamePointcutError
                self.after = method
            if Around.contains(method):
                if self.around is not None:
                    raise CannotDeclareSamePointcutError
                self.around = method
        return super().__call__(obj)

    def is_matched(self, method: MethodType) -> bool:
        if Before.contains(self.before):
            if Before.single(self.before).is_matched(method):
                return True
        if AfterReturning.contains(self.after_returning):
            if AfterReturning.single(self.after_returning).is_matched(method):
                return True
        if AfterRaising.contains(self.after_raising):
            if AfterRaising.single(self.after_raising).is_matched(method):
                return True
        if After.contains(self.after):
            if After.single(self.after).is_matched(method):
                return True
        if Around.contains(self.around):
            if Around.single(self.around).is_matched(method):
                return True
        return False

    def to_runnable_aspect(self, instance: object, next: Func) -> RunnableAspect:
        return RunnableAspect(
            instance=instance,
            before=self.before,
            after_returning=self.after_returning,
            after_raising=self.after_raising,
            after=self.after,
            around=self.around,
            next=next,
        )


@dataclass
class AsyncAspect(Bean):
    before: AsyncFunc | None = field(init=False, default=None)
    after_returning: AsyncFunc | None = field(init=False, default=None)
    after_raising: AsyncFunc | None = field(init=False, default=None)
    after: AsyncFunc | None = field(init=False, default=None)
    around: AsyncFunc | None = field(init=False, default=None)

    def __call__(self, obj: ClassT) -> ClassT:
        for _, method in getmembers(obj):
            if AsyncBefore.contains(method):
                if self.before is not None:
                    raise CannotDeclareSamePointcutError
                self.before = method
            if AsyncAfterReturning.contains(method):
                if self.after_returning is not None:
                    raise CannotDeclareSamePointcutError
                self.after_returning = method
            if AsyncAfterRaising.contains(method):
                if self.after_raising is not None:
                    raise CannotDeclareSamePointcutError
                self.after_raising = method
            if AsyncAfter.contains(method):
                if self.after is not None:
                    raise CannotDeclareSamePointcutError
                self.after = method
            if AsyncAround.contains(method):
                if self.around is not None:
                    raise CannotDeclareSamePointcutError
                self.around = method
        return super().__call__(obj)

    def is_matched(self, method: MethodType) -> bool:
        if AsyncBefore.contains(self.before):
            if AsyncBefore.single(self.before).is_matched(method):
                return True
        if AsyncAfterReturning.contains(self.after_returning):
            if AsyncAfterReturning.single(self.after_returning).is_matched(method):
                return True
        if AsyncAfterRaising.contains(self.after_raising):
            if AsyncAfterRaising.single(self.after_raising).is_matched(method):
                return True
        if AsyncAfter.contains(self.after):
            if AsyncAfter.single(self.after).is_matched(method):
                return True
        if AsyncAround.contains(self.around):
            if AsyncAround.single(self.around).is_matched(method):
                return True
        return False

    def to_runnable_aspect(self, instance: object, next: Func) -> AsyncRunnableAspect:
        return AsyncRunnableAspect(
            instance=instance,
            before=self.before,
            after_returning=self.after_returning,
            after_raising=self.after_raising,
            after=self.after,
            around=self.around,
            next=next,
        )
