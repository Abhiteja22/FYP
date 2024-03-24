from django.test import TestCase
from .utils import *
from unittest.mock import patch

# Create your tests here.
class TickerTestCase(TestCase):
    @patch('app.utils.yf.Ticker')
    def test_get_long_name(self, mock_ticker):
        """
        Test that the get_long_name function returns the correct asset name
        """
        expected_long_name = 'Apple Inc.'
        mock_ticker.return_value.info.get.return_value = expected_long_name

        ticker = 'AAPL'
        actual_long_name = get_long_name(ticker)

        self.assertEqual(actual_long_name, expected_long_name)