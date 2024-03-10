from types import ModuleType
from itertools import chain

import pytest

from spakky.bean.bean import Bean, BeanFactory
from spakky.core.annotation import ClassAnnotation
from spakky.core.importing import (
    CannotScanNonPackageModuleError,
    list_classes,
    list_functions,
    list_modules,
)
from tests import dummy_package
from tests.dummy_package import module_a, module_b, module_c


def test_list_modules_expect_success() -> None:
    assert list_modules(dummy_package) == {module_a, module_b, module_c}
    assert list_modules("tests.dummy_package") == {module_a, module_b, module_c}


def test_list_modules_expect_fail() -> None:
    with pytest.raises(CannotScanNonPackageModuleError):
        assert list_modules(module_a)


def test_list_classes_expect_success() -> None:
    assert list_classes(module_a) == {Bean, module_a.DummyA, module_a.ComponentA}


def test_list_classes_with_selector_expect_success() -> None:
    assert list_classes(module_a, lambda x: x.__name__ == "DummyA") == {module_a.DummyA}
    modules: set[ModuleType] = list_modules(dummy_package)
    assert set(chain(*(list_classes(module) for module in modules))) == {
        ClassAnnotation,
        Bean,
        BeanFactory,
        module_a.DummyA,
        module_a.ComponentA,
        module_b.DummyB,
        module_b.ComponentB,
        module_b.UnmanagedB,
        module_c.DummyC,
        module_c.ComponentC,
    }
    assert set(
        chain(*(list_classes(module, ClassAnnotation.contains) for module in modules))
    ) == {
        module_b.DummyB,
        module_a.ComponentA,
        module_b.ComponentB,
        module_c.ComponentC,
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
        chain(*(list_functions(module, BeanFactory.contains) for module in modules))
    ) == {module_b.unmanaged_b}
