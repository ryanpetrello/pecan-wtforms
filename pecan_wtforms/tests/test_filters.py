from unittest import TestCase


class TestDefaultFilter(TestCase):

    def test_default(self):
        from pecan_wtforms import default
        assert default('Test')(None) == 'Test'
        assert default('Test')('') == 'Test'

    def test_passthrough(self):
        from pecan_wtforms import default
        assert default('Test')(100) == 100
        assert default('Test')('Spam') == 'Spam'
        assert default('Test')(tuple()) == tuple()
        assert default('Test')(False) == False
