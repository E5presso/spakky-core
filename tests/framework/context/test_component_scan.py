from spakky.framework.context.component_scan import ComponentScan, IComponentScan


def test_component_scan_with_default_path() -> None:
    @ComponentScan()
    class A:
        ...

    assert issubclass(A, IComponentScan)
    assert isinstance(A(), IComponentScan)
