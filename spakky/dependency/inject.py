from typing import overload

from spakky.core.generics import ObjectT
from spakky.dependency.context import Context


@overload
def inject(context: Context, *, required_type: type[ObjectT]) -> ObjectT:
    """Inject component from context by given condition\n

    Example:
        ```python
        def do_something(a: IA = inject(context, required_type=IA)) -> str:
            return a.do_a()
        ```

    Args:
        context (Context): Context instance to get component
        required_type (type[ObjectT] | None, optional): Required type to get component.
        Defaults to None.

    Returns:
        ObjectT: Retrieved component by given condition
    """
    ...


@overload
def inject(context: Context, *, name: str) -> object:
    """Inject component from context by given condition\n

    Example:
        ```python
        def do_something(a: IA = inject(context, name="i_a)) -> str:
            return a.do_a()
        ```

    Args:
        context (Context): Context instance to get component
        name (str | None, optional): Name to get component. Defaults to None.

    Returns:
        object: Retrieved component by given condition
    """
    ...


def inject(
    context: Context,
    required_type: type[ObjectT] | None = None,
    name: str | None = None,
) -> ObjectT | object:
    """Inject component from context by given condition\n

    Example:
        ```python
        def do_something(a: IA = inject(context, required_type=IA)) -> str:
            return a.do_a()
        ```

    Args:
        context (Context): Context instance to get component
        required_type (type[ObjectT] | None, optional): Required type to get component.
        Defaults to None.
        name (str | None, optional): Name to get component. Defaults to None.

    Returns:
        ObjectT | object: Retrieved component by given condition
    """
    if required_type is not None:
        return context.get(required_type=required_type)
    if name is None:  # pragma: no cover
        raise ValueError("'required_type' and 'name' both cannot be None")
    return context.get(name=name)
