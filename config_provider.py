import json
import os
from abc import ABC, abstractmethod

import boto3


class ConfigProvider(ABC):
    @abstractmethod
    def get_config(self, env: str) -> dict:
        pass


class AppConfigProvider(ConfigProvider):
    def __init__(
        self,
        app_name: str = None,
        config_name: str = None,
        region: str = None,
        config: json = {},
    ):
        self.app_name = app_name or os.environ.get(
            "APP_CONFIG_APP", "acTestApplication"
        )
        self.config_name = config_name or os.environ.get(
            "APP_CONFIG_CONFIG", "acSimpleFeatureFlag"
        )
        self.region = region or os.environ.get("AWS_REGION", "us-west-2")

    def get_config(self, env: str) -> dict:
        client = boto3.client("appconfigdata", region_name=self.region)

        session_response = client.start_configuration_session(
            ApplicationIdentifier=self.app_name,
            EnvironmentIdentifier=env,
            ConfigurationProfileIdentifier=self.config_name,
        )

        token = session_response["InitialConfigurationToken"]
        response = client.get_latest_configuration(ConfigurationToken=token)
        config_content = response["Configuration"]

        if hasattr(config_content, "read"):
            config_content = config_content.read().decode("utf-8")

        self.config = json.loads(config_content)
        print(f"Config: {self.config}")
        return self.config

    def get_flag_value(self, flagName: str) -> bool:
        return self.config[flagName]["enabled"]
