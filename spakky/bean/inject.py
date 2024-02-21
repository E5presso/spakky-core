from typing import overload

from spakky.bean.application_context import ApplicationContext
from spakky.core.generics import AnyT


@overload
def inject(context: ApplicationContext, *, required_type: type[AnyT]) -> AnyT:
    """Inject bean from context by given condition\n

    Example:
        ```python
        def do_something(a: IA = inject(context, required_type=IA)) -> str:
            return a.do_a()
        ```

    Args:
        context (Context): Context instance to get bean
        required_type (type[ObjectT] | None, optional): Required type to get bean.
        Defaults to None.

    Returns:
        ObjectT: Retrieved bean by given condition
    """
    ...


@overload
def inject(context: ApplicationContext, *, name: str) -> object:
    """Inject bean from context by given condition\n

    Example:
        ```python
        def do_something(a: IA = inject(context, name="i_a)) -> str:
            return a.do_a()
        ```

    Args:
        context (Context): Context instance to get bean
        name (str | None, optional): Name to get bean. Defaults to None.

    Returns:
        object: Retrieved bean by given condition
    """
    ...


def inject(
    context: ApplicationContext,
    required_type: type[AnyT] | None = None,
    name: str | None = None,
) -> AnyT | object:
    """Inject bean from context by given condition\n

    Example:
        ```python
        def do_something(a: IA = inject(context, required_type=IA)) -> str:
            return a.do_a()
        ```

    Args:
        context (Context): Context instance to get bean
        required_type (type[ObjectT] | None, optional): Required type to get bean.
        Defaults to None.
        name (str | None, optional): Name to get bean. Defaults to None.

    Returns:
        ObjectT | object: Retrieved bean by given condition
    """
    if name is not None:
        return context.get(name=name)
    if required_type is None:  # pragma: no cover
        raise ValueError("'name' and 'required_type' both cannot be None")
    return context.get(required_type=required_type)
