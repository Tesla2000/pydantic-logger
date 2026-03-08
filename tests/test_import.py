from unittest import TestCase


class TestImport(TestCase):
    @staticmethod
    def test_import():
        import pydantic_logger

        _ = pydantic_logger
