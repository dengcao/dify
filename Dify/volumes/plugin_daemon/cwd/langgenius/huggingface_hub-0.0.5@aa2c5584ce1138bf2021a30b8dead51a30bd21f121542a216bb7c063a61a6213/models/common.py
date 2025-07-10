from huggingface_hub.utils import BadRequestError, HfHubHTTPError  # type: ignore

from dify_plugin.errors.model import InvokeBadRequestError, InvokeError


class _CommonHuggingfaceHub:
    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        return {InvokeBadRequestError: [HfHubHTTPError, BadRequestError]}
