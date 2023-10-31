from spakky.framework.context.component_scan import ComponentScan


def test_component_scan_with_default_path() -> None:
    @ComponentScan()
    class A:
        ...

    assert ComponentScan.has_annotation(A)
