from types import ModuleType
from itertools import chain

import pytest

from spakky.core.annotation import Annotation, ClassAnnotation
from spakky.core.importing import (
    CannotScanNonPackageModuleError,
    is_package,
    list_classes,
    list_functions,
    list_modules,
    resolve_module,
)
from spakky.injectable.injectable import Injectable
from tests.dummy import dummy_package
from tests.dummy.dummy_package import module_a, module_b, module_c


def test_list_modules_expect_success() -> None:
    assert list_modules(dummy_package) == {module_a, module_b, module_c}
    assert list_modules("tests.dummy.dummy_package") == {module_a, module_b, module_c}


def test_list_modules_expect_fail() -> None:
    with pytest.raises(CannotScanNonPackageModuleError):
        assert list_modules(module_a)


def test_list_classes_expect_success() -> None:
    assert list_classes(module_a) == {Injectable, module_a.DummyA, module_a.InjectableA}


def test_list_classes_with_selector_expect_success() -> None:
    assert list_classes(module_a, lambda x: x.__name__ == "DummyA") == {module_a.DummyA}
    modules: set[ModuleType] = list_modules(dummy_package)
    assert set(chain(*(list_classes(module) for module in modules))) == {
        ClassAnnotation,
        Injectable,
        Injectable,
        module_a.DummyA,
        module_a.InjectableA,
        module_b.DummyB,
        module_b.InjectableB,
        module_b.UnmanagedB,
        module_c.DummyC,
        module_c.InjectableC,
    }
    assert set(
        chain(*(list_classes(module, Annotation.contains) for module in modules))
    ) == {
        module_b.DummyB,
        module_a.InjectableA,
        module_b.InjectableB,
        module_c.InjectableC,
    }


def test_list_functions_expect_success() -> None:
    assert list_functions(module_b) == {module_b.unmanaged_b, module_b.hello_world}


def test_list_functions_with_selector_expect_success() -> None:
    assert list_functions(module_b, lambda x: x.__name__ == "unmanaged_b") == {
        module_b.unmanaged_b
    }
    modules: set[ModuleType] = list_modules(dummy_package)
    assert set(chain(*(list_functions(module) for module in modules))) == {
        module_b.unmanaged_b,
        module_b.hello_world,
    }
    assert set(
        chain(*(list_functions(module, Injectable.contains) for module in modules))
    ) == {module_b.unmanaged_b}


def test_resolve_module() -> None:
    module_path: str = "tests.dummy.dummy_package.module_a"
    assert resolve_module(module_path) == module_a
    assert resolve_module(module_a) == module_a


def test_is_package() -> None:
    assert is_package("tests.dummy.dummy_package") is True
    assert is_package("tests.dummy.dummy_package.module_a") is False

    assert is_package(dummy_package) is True
    assert is_package(module_a) is False
