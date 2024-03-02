from types import MethodType
from typing import Any, Sequence, cast
from logging import Logger

from spakky.aop.advisor import IAdvisor, IAsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.post_processor import IBeanPostProcessor
from spakky.core.proxy import Enhancer, IMethodInterceptor
from spakky.core.types import AsyncFunc, Func


class _Runnable:
    instance: IAdvisor
    next: Func

    def __init__(self, instance: IAdvisor, next: Func) -> None:
        self.instance = instance
        self.next = next

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


class _AsyncRunnable:
    instance: IAsyncAdvisor
    next: AsyncFunc

    def __init__(self, instance: IAsyncAdvisor, next: AsyncFunc) -> None:
        self.instance = instance
        self.next = next

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


class AspectMethodInterceptor(IMethodInterceptor):
    __advisors: Sequence[IAdvisor | IAsyncAdvisor]

    def __init__(self, advisors: Sequence[IAdvisor | IAsyncAdvisor]) -> None:
        super().__init__()
        self.__advisors = advisors

    def intercept(self, method: MethodType, *args: Any, **kwargs: Any) -> Any:
        runnable: Func = method
        for advisor in self.__advisors:
            if not isinstance(advisor, IAdvisor):  # pragma: no cover
                continue
            runnable = _Runnable(advisor, runnable)
        return runnable(*args, **kwargs)

    async def intercept_async(self, method: MethodType, *args: Any, **kwargs: Any) -> Any:
        runnable: AsyncFunc = method
        for advisor in self.__advisors:
            if not isinstance(advisor, IAsyncAdvisor):  # pragma: no cover
                continue
            runnable = _AsyncRunnable(advisor, runnable)
        return await runnable(*args, **kwargs)


class AspectBeanPostProcessor(IBeanPostProcessor):
    __logger: Logger

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    def post_process_bean(self, container: IBeanContainer, bean: object) -> object:
        if Aspect.contains(bean) or AsyncAspect.contains(bean):
            return bean
        advisors: Sequence[object] = container.where(
            lambda x: Aspect.contains(x) or AsyncAspect.contains(x)
        )
        matched_advisors: Sequence[IAdvisor | IAsyncAdvisor] = []
        for advisor in advisors:
            aspect: Aspect | None = Aspect.single_or_none(advisor)
            async_aspect: AsyncAspect | None = AsyncAspect.single_or_none(advisor)
            if aspect is not None and aspect.matches(bean):
                self.__logger.info(
                    f"[{type(self).__name__}] {type(advisor).__name__} -> {type(bean).__name__}"
                )
                matched_advisors.append(cast(IAdvisor, advisor))
                break
            if async_aspect is not None and async_aspect.matches(bean):
                self.__logger.info(
                    f"[{type(self).__name__}] {type(advisor).__name__} -> {type(bean).__name__}"
                )
                matched_advisors.append(cast(IAsyncAdvisor, advisor))
                break
        if not any(matched_advisors):
            return bean
        return Enhancer(
            superclass=type(bean),
            callback=AspectMethodInterceptor(advisors=matched_advisors),
        ).create()
