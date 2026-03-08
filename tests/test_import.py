from unittest import TestCase


class TestImport(TestCase):
    @staticmethod
    def test_import():
        import pydantic_logger  # ignore

        _ = pydantic_logger
