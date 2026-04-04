from unittest import TestCase


class TestImport(TestCase):
    def test_import(self) -> None:
        import pydantic_logger  # ignore

        _ = pydantic_logger
