from typing import Mapping
import logging

from werkzeug import Request, Response
from dify_plugin import Endpoint
from dify_plugin.config.logger_format import plugin_logger_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class HTTPGetEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Streamable HTTP in dify is a lightweight design, it only support POST and don't support SSE.
        """
        logger.info(f"HTTPGetEndpoint request headers: {r.headers}")
        response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": "Method not allowed"},
        }

        return Response(response, status=405, content_type="application/json")
