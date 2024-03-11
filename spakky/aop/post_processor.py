import sys
from typing import Any, Sequence, cast
from logging import Logger

from spakky.aop.advisor import IAdvisor, IAsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.order import Order
from spakky.bean.autowired import Unknown
from spakky.bean.bean import Bean
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.bean_processor import IBeanPostProcessor
from spakky.core.proxy import Enhancer, IMethodInterceptor
from spakky.core.types import AsyncFunc, Func


class _Runnable:
    instance: IAdvisor
    next: Func

    def __init__(self, instance: IAdvisor, next: Func) -> None:
        self.instance = instance
        self.next = next

    def __getattr__(self, name: str) -> Any:
        return getattr(self.next, name)

    def __dir__(self) -> list[str]:
        return dir(self.next)

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

    def __getattr__(self, name: str) -> Any:
        return getattr(self.next, name)

    def __dir__(self) -> list[str]:
        return dir(self.next)

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
    __container: IBeanContainer
    __advisors: Sequence[type[IAdvisor | IAsyncAdvisor]]

    def __init__(
        self,
        container: IBeanContainer,
        advisors: Sequence[type[IAdvisor | IAsyncAdvisor]],
    ) -> None:
        super().__init__()
        self.__container = container
        self.__advisors = advisors

    def intercept(self, method: Func, *args: Any, **kwargs: Any) -> Any:
        advisors: Sequence[type[IAdvisor]] = [
            x for x in self.__advisors if issubclass(x, IAdvisor)
        ]
        matched: Sequence[type[IAdvisor]] = [
            x for x in advisors if Aspect.single(x).matches(method)
        ]
        runnable: Func = method
        for advisor in matched:
            runnable = _Runnable(self.__container.single(required_type=advisor), runnable)
        return runnable(*args, **kwargs)

    async def intercept_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        advisors: Sequence[type[IAsyncAdvisor]] = [
            x for x in self.__advisors if issubclass(x, IAsyncAdvisor)
        ]
        matched: Sequence[type[IAsyncAdvisor]] = [
            x for x in advisors if AsyncAspect.single(x).matches(method)
        ]
        runnable: Func = method
        for advisor in matched:
            runnable = _AsyncRunnable(
                self.__container.single(required_type=advisor), runnable
            )
        return await runnable(*args, **kwargs)


class AspectBeanPostProcessor(IBeanPostProcessor):
    __logger: Logger
    __cache: dict[type, object]

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger
        self.__cache = {}

    def __set_cache(self, type_: type, bean: object) -> None:
        self.__cache[type_] = bean

    def __get_cache(self, type_: type) -> object | None:
        return self.__cache.get(type_, None)

    def post_process_bean(self, container: IBeanContainer, bean: object) -> object:
        if (cached := self.__get_cache(type(bean))) is not None:
            return cached
        if Aspect.contains(bean) or AsyncAspect.contains(bean):
            self.__set_cache(type(bean), bean)
            return bean
        annotation: Bean | None = Bean.single_or_none(bean)
        if annotation is None:
            self.__set_cache(type(bean), bean)
            return bean
        matched_advisors: Sequence[type[IAdvisor | IAsyncAdvisor]] = []
        advisors: Sequence[type] = container.filter_bean_types(
            lambda x: Aspect.contains(x) or AsyncAspect.contains(x)
        )
        for advisor in advisors:
            aspect: Aspect | None = Aspect.single_or_none(advisor)
            async_aspect: AsyncAspect | None = AsyncAspect.single_or_none(advisor)
            if aspect is not None and aspect.matches(bean):
                matched_advisors.append(cast(type[IAdvisor], advisor))
                continue
            if async_aspect is not None and async_aspect.matches(bean):
                matched_advisors.append(cast(type[IAsyncAdvisor], advisor))
                continue
        if not any(matched_advisors):
            self.__cache[type(bean)] = bean
            return bean
        matched_advisors.sort(
            key=lambda x: Order.single_or_default(x, Order(sys.maxsize)).order,
            reverse=True,
        )
        self.__logger.info(
            f"[{type(self).__name__}] {[f'{x.__name__}({Order.single_or_default(x, Order(sys.maxsize)).order})' for x in matched_advisors]!r} -> {type(bean).__name__}"
        )
        dependencies: dict[str, object] = {}
        for name, required_type in annotation.dependencies.items():
            if required_type == Unknown:
                dependencies[name] = container.single(name=name)
                continue
            dependencies[name] = container.single(required_type=required_type)
        proxy: object = Enhancer(
            superclass=type(bean),
            callback=AspectMethodInterceptor(container, matched_advisors),
        ).create(**dependencies)
        self.__set_cache(type(bean), proxy)
        return proxy
