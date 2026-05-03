import json
import os
from typing import List, Optional, Union

import boto3
from openfeature.evaluation_context import EvaluationContext
from openfeature.flag_evaluation import FlagResolutionDetails
from openfeature.hook import Hook
from openfeature.provider import AbstractProvider
from openfeature.provider.metadata import Metadata


class AwsAppConfigProvider(AbstractProvider):
    """OpenFeature provider for AWS AppConfig using the AppConfig Data API."""

    def __init__(
        self,
        app_name: str = None,
        config_name: str = None,
        region: str = None,
        env: str = "dev",
    ):
        self.app_name = app_name or os.environ.get(
            "APP_CONFIG_APP", "acTestApplication"
        )
        self.config_name = config_name or os.environ.get(
            "APP_CONFIG_CONFIG", "acSimpleFeatureFlag"
        )
        self.region = region or os.environ.get("AWS_REGION", "us-west-2")
        self.env = env
        self._client = None
        self._session_token = None
        self._config = {}

    def get_metadata(self) -> Metadata:
        return Metadata(name="AWS AppConfig Provider")

    def get_provider_hooks(self) -> List[Hook]:
        return []

    def _get_client(self):
        """Lazily initialize and return the boto3 AppConfig Data client."""
        if self._client is None:
            self._client = boto3.client("appconfigdata", region_name=self.region)
        return self._client

    def _ensure_session(self):
        """Ensure we have a valid session token, starting one if needed."""
        if self._session_token is not None:
            return

        client = self._get_client()
        session_response = client.start_configuration_session(
            ApplicationIdentifier=self.app_name,
            EnvironmentIdentifier=self.env,
            ConfigurationProfileIdentifier=self.config_name,
        )
        self._session_token = session_response["InitialConfigurationToken"]

    def _fetch_config(self):
        """Fetch the latest configuration from AppConfig."""
        self._ensure_session()
        client = self._get_client()

        response = client.get_latest_configuration(
            ConfigurationToken=self._session_token
        )

        # Update session token for next request
        self._session_token = response.get("NextPollConfigurationToken", self._session_token)

        config_content = response["Configuration"]

        # Only parse if there's actual content (AppConfig returns empty when unchanged)
        if hasattr(config_content, "read"):
            config_content = config_content.read().decode("utf-8")
        elif config_content:
            pass  # Already a string
        else:
            # No content returned (unchanged), keep existing config
            return

        if config_content:
            self._config = json.loads(config_content)

    def resolve_boolean_details(
        self,
        flag_key: str,
        default_value: bool,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[bool]:
        try:
            self._fetch_config()
            # AppConfig structure: {"feature1": {"enabled": true}}
            flag_config = self._config.get(flag_key, {})
            value = flag_config.get("enabled", default_value)
            return FlagResolutionDetails(value=value)
        except Exception as e:
            print(f"Error resolving flag {flag_key}: {e}")
            return FlagResolutionDetails(
                value=default_value,
                error_code="PROVIDER_ERROR",
                error_message=str(e),
            )

    def resolve_string_details(
        self,
        flag_key: str,
        default_value: str,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[str]:
        return FlagResolutionDetails(value=default_value)

    def resolve_integer_details(
        self,
        flag_key: str,
        default_value: int,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[int]:
        return FlagResolutionDetails(value=default_value)

    def resolve_float_details(
        self,
        flag_key: str,
        default_value: float,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[float]:
        return FlagResolutionDetails(value=default_value)

    def resolve_object_details(
        self,
        flag_key: str,
        default_value: Union[dict, list],
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[Union[dict, list]]:
        return FlagResolutionDetails(value=default_value)
