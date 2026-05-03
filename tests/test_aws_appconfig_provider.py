import pytest
from unittest.mock import patch, MagicMock
from openfeature.flag_evaluation import FlagResolutionDetails
from aws_appconfig_provider import AwsAppConfigProvider


class TestAwsAppConfigProvider:
    """Tests for AwsAppConfigProvider"""

    @pytest.fixture
    def provider(self):
        return AwsAppConfigProvider(
            app_name="test-app",
            config_name="test-config",
            region="us-west-2",
            env="dev",
        )

    @pytest.fixture
    def mock_boto3_client(self):
        with patch("aws_appconfig_provider.boto3.client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_get_metadata(self, provider):
        """Test provider metadata returns correct name"""
        metadata = provider.get_metadata()
        assert metadata.name == "AWS AppConfig Provider"

    def test_resolve_boolean_details_flag_enabled(self, provider, mock_boto3_client):
        """Test resolving a boolean flag that is enabled"""
        # Setup mock responses
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": true}}'
            )
        }

        result = provider.resolve_boolean_details(
            flag_key="feature1",
            default_value=False,
        )

        assert isinstance(result, FlagResolutionDetails)
        assert result.value is True
        assert result.error_code is None

    def test_resolve_boolean_details_flag_disabled(self, provider, mock_boto3_client):
        """Test resolving a boolean flag that is disabled"""
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": false}}'
            )
        }

        result = provider.resolve_boolean_details(
            flag_key="feature1",
            default_value=True,
        )

        assert result.value is False

    def test_resolve_boolean_details_missing_flag_returns_default(self, provider, mock_boto3_client):
        """Test that missing flags return the default value"""
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": true}}'
            )
        }

        result = provider.resolve_boolean_details(
            flag_key="nonexistent_flag",
            default_value=False,
        )

        assert result.value is False

    def test_resolve_boolean_details_api_error_returns_default(self, provider, mock_boto3_client):
        """Test that API errors return the default value"""
        mock_boto3_client.start_configuration_session.side_effect = Exception("API Error")

        result = provider.resolve_boolean_details(
            flag_key="feature1",
            default_value=True,
        )

        assert result.value is True  # Returns default
        assert result.error_code is not None

    def test_resolve_boolean_details_caches_session_token(self, provider, mock_boto3_client):
        """Test that session token is cached and reused"""
        mock_boto3_client.start_configuration_session.return_value = {
            "InitialConfigurationToken": "token123"
        }
        mock_boto3_client.get_latest_configuration.return_value = {
            "Configuration": MagicMock(
                read=lambda: b'{"feature1": {"enabled": true}}'
            )
        }

        # First call
        provider.resolve_boolean_details("feature1", False)
        # Second call should reuse the token
        provider.resolve_boolean_details("feature1", False)

        # Should only start session once
        assert mock_boto3_client.start_configuration_session.call_count == 1
        assert mock_boto3_client.get_latest_configuration.call_count == 2

    def test_resolve_string_details_returns_default(self, provider):
        """Test that string details returns default (not implemented for AppConfig)"""
        result = provider.resolve_string_details("feature1", "default")
        assert result.value == "default"

    def test_resolve_integer_details_returns_default(self, provider):
        """Test that integer details returns default (not implemented for AppConfig)"""
        result = provider.resolve_integer_details("feature1", 0)
        assert result.value == 0

    def test_resolve_float_details_returns_default(self, provider):
        """Test that float details returns default (not implemented for AppConfig)"""
        result = provider.resolve_float_details("feature1", 0.0)
        assert result.value == 0.0

    def test_resolve_object_details_returns_default(self, provider):
        """Test that object details returns default (not implemented for AppConfig)"""
        result = provider.resolve_object_details("feature1", {})
        assert result.value == {}
