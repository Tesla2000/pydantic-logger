from unittest import TestCase


class TestImport(TestCase):
    def test_import(self):
        import pydantic_logger  # ignore

        _ = pydantic_logger
