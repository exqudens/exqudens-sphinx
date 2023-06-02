import logging


def test_1():
    """Function test_1."""
    logging.getLogger(__name__).info('AAA: {}', 111)


class TestMath:

    def test_1(self):
        """Method TestMath::test_1."""
        logging.getLogger(__name__).info('AAA: {}', 111)
