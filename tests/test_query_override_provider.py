from unittest.mock import MagicMock

from flask import Flask
import pytest
from openfeature.flag_evaluation import FlagResolutionDetails
from openfeature.provider import AbstractProvider
from query_override_provider import QueryParamOverrideProvider


@pytest.fixture
def flask_app():
    return Flask("test_app")


@pytest.fixture
def mock_delegate():
    mock = MagicMock(spec=AbstractProvider)
    mock.resolve_boolean_details.return_value = FlagResolutionDetails(
        value=False, variant="delegate-default"
    )
    mock.resolve_string_details.return_value = FlagResolutionDetails(
        value="delegate-string", variant="delegate-default"
    )
    mock.resolve_integer_details.return_value = FlagResolutionDetails(
        value=42, variant="delegate-default"
    )
    mock.resolve_float_details.return_value = FlagResolutionDetails(
        value=3.14, variant="delegate-default"
    )
    mock.resolve_object_details.return_value = FlagResolutionDetails(
        value={"key": "val"}, variant="delegate-default"
    )
    return mock


@pytest.fixture
def provider(mock_delegate):
    return QueryParamOverrideProvider(mock_delegate)


def test_no_request_context_falls_back(provider, mock_delegate):
    result = provider.resolve_boolean_details("feature1", False)
    assert result.value is False
    assert result.variant == "delegate-default"
    mock_delegate.resolve_boolean_details.assert_called_once_with(
        "feature1", False, None
    )


def test_missing_query_param_falls_back(provider, mock_delegate, flask_app):
    with flask_app.test_request_context("/?other_flag=true"):
        result = provider.resolve_boolean_details("feature1", False)
        assert result.value is False
        assert result.variant == "delegate-default"
        mock_delegate.resolve_boolean_details.assert_called_once_with(
            "feature1", False, None
        )


def test_case_insensitive_key_match(provider, flask_app):
    with flask_app.test_request_context("/?FEATURE1=true"):
        result = provider.resolve_boolean_details("feature1", False)
        assert result.value is True
        assert result.variant == "query-override"

    with flask_app.test_request_context("/?feature2=FALSE"):
        result = provider.resolve_boolean_details("FEATURE2", True)
        assert result.value is False
        assert result.variant == "query-override"


@pytest.mark.parametrize(
    "param_value,expected",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("t", True),
        ("y", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("f", False),
        ("n", False),
    ],
)
def test_boolean_parsing(provider, flask_app, param_value, expected):
    with flask_app.test_request_context(f"/?feature1={param_value}"):
        result = provider.resolve_boolean_details("feature1", not expected)
        assert result.value is expected
        assert result.variant == "query-override"


def test_invalid_boolean_falls_back(provider, mock_delegate, flask_app):
    with flask_app.test_request_context("/?feature1=not-a-boolean"):
        result = provider.resolve_boolean_details("feature1", False)
        assert result.value is False
        assert result.variant == "delegate-default"


def test_string_override(provider, flask_app):
    with flask_app.test_request_context("/?my_str=hello"):
        result = provider.resolve_string_details("my_str", "default")
        assert result.value == "hello"
        assert result.variant == "query-override"


def test_integer_override(provider, flask_app):
    with flask_app.test_request_context("/?my_int=123"):
        result = provider.resolve_integer_details("my_int", 0)
        assert result.value == 123
        assert result.variant == "query-override"


def test_invalid_integer_falls_back(provider, mock_delegate, flask_app):
    with flask_app.test_request_context("/?my_int=abc"):
        result = provider.resolve_integer_details("my_int", 0)
        assert result.value == 42
        assert result.variant == "delegate-default"


def test_float_override(provider, flask_app):
    with flask_app.test_request_context("/?my_float=1.23"):
        result = provider.resolve_float_details("my_float", 0.0)
        assert result.value == 1.23
        assert result.variant == "query-override"


def test_invalid_float_falls_back(provider, mock_delegate, flask_app):
    with flask_app.test_request_context("/?my_float=abc"):
        result = provider.resolve_float_details("my_float", 0.0)
        assert result.value == 3.14
        assert result.variant == "delegate-default"


def test_object_override(provider, flask_app):
    with flask_app.test_request_context('/?my_obj={"foo":"bar"}'):
        result = provider.resolve_object_details("my_obj", {})
        assert result.value == {"foo": "bar"}
        assert result.variant == "query-override"


def test_invalid_object_falls_back(provider, mock_delegate, flask_app):
    with flask_app.test_request_context("/?my_obj=invalid-json"):
        result = provider.resolve_object_details("my_obj", {})
        assert result.value == {"key": "val"}
        assert result.variant == "delegate-default"


def test_metadata_hooks_shutdown(provider, mock_delegate):
    mock_delegate.get_metadata.return_value = "metadata"
    mock_delegate.get_provider_hooks.return_value = ["hook1"]

    assert provider.get_metadata() == "metadata"
    assert provider.get_provider_hooks() == ["hook1"]

    provider.shutdown()
    mock_delegate.shutdown.assert_called_once()
