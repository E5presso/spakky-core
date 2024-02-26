from typing import Any
from inspect import getmembers

from spakky.aop.advice import (
    AbstractAdvice,
    AbstractAsyncAdvice,
    AsyncPointcut,
    Pointcut,
)
from spakky.bean.bean import Bean
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.post_processor import IBeanPostProcessor


@Bean()
class AspectBeanPostPrecessor(IBeanPostProcessor):
    def post_process_bean(self, container: IBeanContainer, bean: Any) -> Any:
        for name, member in getmembers(bean):
            if Pointcut.contains(member):
                pointcuts: list[Pointcut] = Pointcut.all(member)
                for pointcut in pointcuts:
                    advice: AbstractAdvice = container.get(required_type=pointcut.advice)
                    member = advice(pointcut, member)
                setattr(bean, name, member)
            if AsyncPointcut.contains(member):
                async_pointcuts: list[AsyncPointcut] = AsyncPointcut.all(member)
                for async_pointcut in async_pointcuts:
                    async_advice: AbstractAsyncAdvice = container.get(
                        required_type=async_pointcut.advice
                    )
                    member = async_advice(async_pointcut, member)
                setattr(bean, name, member)
        return bean
