from typing import Generic, TypeVar, Protocol, runtime_checkable

import pytest

from spakky.core.mro import generic_mro


def test_generic_mro_normal_inheritance() -> None:
    class A: ...

    class B(A): ...

    class C: ...

    class D: ...

    class E(B): ...

    class F(C): ...

    class G(D, E, F): ...

    class H(E, F): ...

    class I(G): ...

    class J: ...

    class K(G): ...

    class L(H): ...

    class M(I): ...

    class N(J, K): ...

    class O(L): ...

    assert generic_mro(M) == [M, I, G, D, E, B, A, F, C, object]
    assert generic_mro(N) == [N, J, K, G, D, E, B, A, F, C, object]
    assert generic_mro(O) == [O, L, H, E, B, A, F, C, object]


def test_generic_mro_with_generic_inheritance() -> None:
    T_co = TypeVar("T_co", covariant=True)

    class A: ...

    class B(A): ...

    @runtime_checkable
    class IC(Protocol, Generic[T_co]): ...

    class D: ...

    class E(B): ...

    class F(IC[T_co], Generic[T_co]): ...

    class G(D, E, F[int]): ...

    class H(E, F[str]): ...

    class I(G): ...

    class J: ...

    class K(G): ...

    class L(H): ...

    class M(I): ...

    class N(J, K): ...

    class O(L): ...

    assert generic_mro(M) == [
        M,
        I,
        G,
        D,
        E,
        B,
        A,
        F[int],
        IC[int],
        Protocol,
        Generic,
        object,
    ]
    assert generic_mro(N) == [
        N,
        J,
        K,
        G,
        D,
        E,
        B,
        A,
        F[int],
        IC[int],
        Protocol,
        Generic,
        object,
    ]
    assert generic_mro(O) == [
        O,
        L,
        H,
        E,
        B,
        A,
        F[str],
        IC[str],
        Protocol,
        Generic,
        object,
    ]


def test_generic_mro_with_non_class_object() -> None:
    def a(x: int) -> int:
        return x

    with pytest.raises(TypeError):
        generic_mro(a)
