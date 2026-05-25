import json
from typing import List, Optional, Union

from flask import has_request_context, request
from openfeature.evaluation_context import EvaluationContext
from openfeature.flag_evaluation import FlagResolutionDetails
from openfeature.hook import Hook
from openfeature.provider import AbstractProvider
from openfeature.provider.metadata import Metadata


class QueryParamOverrideProvider(AbstractProvider):
    """OpenFeature provider wrapper that allows overriding flags using URL query parameters in Flask."""

    def __init__(self, delegate: AbstractProvider):
        self.delegate = delegate

    def get_metadata(self) -> Metadata:
        return self.delegate.get_metadata()

    def get_provider_hooks(self) -> List[Hook]:
        return self.delegate.get_provider_hooks()

    def shutdown(self):
        if hasattr(self.delegate, "shutdown"):
            self.delegate.shutdown()

    def _get_override_value(self, flag_key: str, flag_type: type):
        if not has_request_context():
            return None

        # Look up key case-insensitively in request.args
        val = None
        for k, v in request.args.items():
            if k.lower() == flag_key.lower():
                val = v
                break

        if val is not None:
            if flag_type == bool:
                val_lower = val.lower()
                if val_lower in ("true", "1", "yes", "on", "t", "y"):
                    return True
                elif val_lower in ("false", "0", "no", "off", "f", "n"):
                    return False
            elif flag_type == str:
                return val
            elif flag_type == int:
                try:
                    return int(val)
                except ValueError:
                    pass
            elif flag_type == float:
                try:
                    return float(val)
                except ValueError:
                    pass
            elif flag_type == dict or flag_type == list or flag_type == (dict, list):
                try:
                    return json.loads(val)
                except (ValueError, TypeError):
                    pass
        return None

    def resolve_boolean_details(
        self,
        flag_key: str,
        default_value: bool,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[bool]:
        override = self._get_override_value(flag_key, bool)
        if override is not None:
            return FlagResolutionDetails(value=override, variant="query-override")
        return self.delegate.resolve_boolean_details(
            flag_key, default_value, evaluation_context
        )

    def resolve_string_details(
        self,
        flag_key: str,
        default_value: str,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[str]:
        override = self._get_override_value(flag_key, str)
        if override is not None:
            return FlagResolutionDetails(value=override, variant="query-override")
        return self.delegate.resolve_string_details(
            flag_key, default_value, evaluation_context
        )

    def resolve_integer_details(
        self,
        flag_key: str,
        default_value: int,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[int]:
        override = self._get_override_value(flag_key, int)
        if override is not None:
            return FlagResolutionDetails(value=override, variant="query-override")
        return self.delegate.resolve_integer_details(
            flag_key, default_value, evaluation_context
        )

    def resolve_float_details(
        self,
        flag_key: str,
        default_value: float,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[float]:
        override = self._get_override_value(flag_key, float)
        if override is not None:
            return FlagResolutionDetails(value=override, variant="query-override")
        return self.delegate.resolve_float_details(
            flag_key, default_value, evaluation_context
        )

    def resolve_object_details(
        self,
        flag_key: str,
        default_value: Union[dict, list],
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[Union[dict, list]]:
        override = self._get_override_value(flag_key, dict)
        if override is not None:
            return FlagResolutionDetails(value=override, variant="query-override")
        return self.delegate.resolve_object_details(
            flag_key, default_value, evaluation_context
        )
