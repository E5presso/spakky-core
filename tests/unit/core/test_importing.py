from types import ModuleType
from itertools import chain

import pytest

from spakky.core.annotation import ClassAnnotation
from spakky.core.importing import (
    CannotScanNonPackageModuleError,
    list_classes,
    list_modules,
)
from tests.unit.core import dummy_package
from tests.unit.core.dummy_package import module_a, module_b, module_c


def test_list_modules_expect_success() -> None:
    assert list_modules(dummy_package) == {module_a, module_b, module_c}


def test_list_modules_expect_fail() -> None:
    with pytest.raises(CannotScanNonPackageModuleError):
        assert list_modules(module_a)


def test_list_classes_expect_success() -> None:
    assert list_classes(module_a) == {module_a.DummyA}


def test_list_classes_with_selector_expect_success() -> None:
    assert list_classes(module_a, lambda x: x.__name__ == "DummyA") == {module_a.DummyA}
    modules: set[ModuleType] = list_modules(dummy_package)
    assert set(chain(*(list_classes(module) for module in modules))) == {
        module_a.DummyA,
        ClassAnnotation,
        module_b.DummyB,
        module_c.DummyC,
    }
    assert set(
        chain(*(list_classes(module, ClassAnnotation.exists) for module in modules))
    ) == {module_b.DummyB}
