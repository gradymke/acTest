import pytest
from unittest.mock import patch
from app import get_provider


class TestGetProviderFlagd:
    """Tests for get_provider() flagd branch in app.py"""

    def test_flagd_provider_dev_port(self):
        """get_provider('flagd', 'dev') uses port 8013"""
        with patch("app.FlagdProvider") as mock_cls:
            get_provider("flagd", "dev")
            mock_cls.assert_called_once_with(host="localhost", port=8013)

    def test_flagd_provider_test_port(self):
        """get_provider('flagd', 'test') uses port 8023"""
        with patch("app.FlagdProvider") as mock_cls:
            get_provider("flagd", "test")
            mock_cls.assert_called_once_with(host="localhost", port=8023)

    def test_flagd_provider_prod_port(self):
        """get_provider('flagd', 'prod') uses port 8033"""
        with patch("app.FlagdProvider") as mock_cls:
            get_provider("flagd", "prod")
            mock_cls.assert_called_once_with(host="localhost", port=8033)

    def test_flagd_provider_unknown_env_falls_back_to_dev_port(self):
        """get_provider('flagd', 'unknown') falls back to port 8013"""
        with patch("app.FlagdProvider") as mock_cls:
            get_provider("flagd", "unknown")
            mock_cls.assert_called_once_with(host="localhost", port=8013)
