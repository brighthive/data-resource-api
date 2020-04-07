import pytest
from data_resource_api.api.v1_0_0 import ResourceHandler
from expects import equal, expect


@pytest.mark.unit
def test_compute_offset():
    handler = ResourceHandler()

    expect(handler.compute_offset(1, 20)).to(equal(0))


@pytest.mark.unit
def test_compute_page():
    handler = ResourceHandler()

    items = [
        handler.compute_page(0, 20),
        handler.compute_page(1, 20),
        handler.compute_page(20, 20),
        handler.compute_page(21, 20),
        handler.compute_page(25, 20),
    ]

    for item in items:
        print(item)

    expect(handler.compute_page(0, 20)).to(equal(1))
    expect(handler.compute_page(1, 20)).to(equal(1))
    expect(handler.compute_page(19, 20)).to(equal(1))
    expect(handler.compute_page(20, 20)).to(equal(2))
    expect(handler.compute_page(99, 20)).to(equal(5))
