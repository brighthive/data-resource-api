from data_resource_api.api.v1_0_0 import ResourceHandler
from expects import expect, be_an, raise_error, have_property, equal, be_empty, be
import json


class TestComputeOffset(object):
    def test_compute_offset(self):
        handler = ResourceHandler()

        expect(handler.compute_offset(1, 20)).to(equal(0))
        # expect(handler.compute_offset(53, 19)).to(equal(0))
        # expect(handler.compute_offset(0, 20)).to(equal(0))

    # def test_build_links(self):
    #     handler = ResourceHandler()

    #     items = [
    #         handler.build_links('test', 0, 20, 5),
    #         handler.build_links('test', 1, 20, 55),
    #         handler.build_links('test', 1, -20, 55)
    #     ]

    #     for item in items:
    #         print(json.dumps(item, indent=4))

    def test_compute_page(self):
        handler = ResourceHandler()

        items = [
            handler.compute_page(0, 20),
            handler.compute_page(1, 20),
            handler.compute_page(20, 20),
            handler.compute_page(21, 20),
            handler.compute_page(25, 20)
        ]

        for item in items:
            print(item)

        expect(handler.compute_page(0, 20)).to(equal(1))
        expect(handler.compute_page(1, 20)).to(equal(1))
        expect(handler.compute_page(19, 20)).to(equal(1))
        expect(handler.compute_page(20, 20)).to(equal(2))
        expect(handler.compute_page(99, 20)).to(equal(5))
