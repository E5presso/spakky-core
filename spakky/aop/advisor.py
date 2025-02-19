from typing import Any

from spakky.aop.interfaces.aspect import IAspect, IAsyncAspect
from spakky.core.types import AsyncFunc, Func


class Advisor:
    instance: IAspect
    next: Func

    def __init__(self, instance: IAspect, next: Func) -> None:
        self.instance = instance
        self.next = next

    def __getattr__(self, name: str) -> Any:
        return getattr(self.next, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.instance.before(*args, **kwargs)
        try:
            result = self.instance.around(self.next, *args, **kwargs)
            self.instance.after_returning(result)
            return result
        except Exception as e:
            self.instance.after_raising(e)
            raise
        finally:
            self.instance.after()


class AsyncAdvisor:
    instance: IAsyncAspect
    next: AsyncFunc

    def __init__(self, instance: IAsyncAspect, next: AsyncFunc) -> None:
        self.instance = instance
        self.next = next

    def __getattr__(self, name: str) -> Any:
        return getattr(self.next, name)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        await self.instance.before_async(*args, **kwargs)
        try:
            result = await self.instance.around_async(self.next, *args, **kwargs)
            await self.instance.after_returning_async(result)
            return result
        except Exception as e:
            await self.instance.after_raising_async(e)
            raise
        finally:
            await self.instance.after_async()
