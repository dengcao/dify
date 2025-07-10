import time
import base64
from io import BytesIO
from PIL import Image

import requests
from requests import Response
from requests.models import PreparedRequest

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class FluxProExpandTool(Tool):
    ROOT_API = "https://api.bfl.ml/"
    US1_API = "https://api.us1.bfl.ai/"
    API_ENDPOINT = "v1/flux-pro-1.0-expand"
    POLL_ENDPOINT = "v1/get_result"
    ACCEPT = "image/*"

    def _make_request(self, headers: dict, data: Any, region: str = "EU1") -> Response:
        req = PreparedRequest()
        req.prepare_method("POST")
        base_url = self.US1_API if region == "US1" else self.ROOT_API
        req.prepare_url(f"{base_url}{self.API_ENDPOINT}", None)
        req.prepare_headers(headers)
        req.prepare_body(data=None, files=None, json=data)
        return requests.Session().send(req)

    def _poll_for_result(self, id: str, headers: dict, region: str = "EU1") -> str:
        timeout, start_time = 240, time.time()
        retries = 0
        max_retries = 0
        base_url = self.US1_API if region == "US1" else self.ROOT_API
        while True:
            response = requests.get(
                f"{base_url}{self.POLL_ENDPOINT}", params={"id": id}, headers=headers
            )
            if response.status_code == 200:
                result = response.json()
                if result["status"] == "Ready":
                    image_url = result["result"]["sample"]
                    return image_url
                elif result["status"] in ["Request Moderated", "Content Moderated"]:
                    raise Exception(
                        f"BFL API Message: {result['status']}"
                    )
                elif result["status"] == "Error":
                    raise Exception(
                        f"BFL API Error: {result}"
                    )
            elif response.status_code == 404:
                if retries < max_retries:
                    retries += 1
                    time.sleep(5)
                    continue
                raise Exception(
                    f"BFL API Error: Task not found after {max_retries} retries"
                )

            elif response.status_code == 202:
                time.sleep(10)
            elif time.time() - start_time > timeout:
                raise Exception(
                    "BFL API Timeout: Request took too long to complete"
                )
            else:
                raise Exception(
                    f"BFL API Error: {response.json()}"
                )

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        region = tool_parameters.get("region", "EU1")

        data = {
            "image": None,
            "top": tool_parameters.get("top", 0),
            "bottom": tool_parameters.get("bottom", 0),
            "left": tool_parameters.get("left", 0),
            "right": tool_parameters.get("right", 0),
            "prompt": tool_parameters.get("prompt", ""),
            "steps": tool_parameters.get("steps", 50),
            "prompt_upsampling": tool_parameters.get("prompt_upsampling", False),
            "seed": tool_parameters.get("seed", None),
            "guidance": tool_parameters.get("guidance", 60),
            "safety_tolerance": tool_parameters.get("safety_tolerance", 2),
            "output_format": tool_parameters.get("output_format", "jpeg"),
            "webhook_url": tool_parameters.get("webhook_url", None),
            "webhook_secret": tool_parameters.get("webhook_secret", None)
        }

        image: File = tool_parameters.get("image", None)
        if image is not None:
            response = requests.get(image.url)
            if response.status_code == 200:
                input_image = Image.open(BytesIO(response.content))
                buffered = BytesIO()
                image_format: str = data["output_format"]
                input_image.save(buffered, format=image_format.upper())
                prompt = base64.b64encode(
                    buffered.getvalue()
                ).decode("utf-8")
                data["image"] = prompt
            else:
                raise Exception(
                    f"Failed to fetch image from URL: {image.url}"
                )
        else:
            raise Exception("No image provided for Flux Pro Fill Tool.")

        data = {k: v for k, v in data.items() if v is not None}
        headers = {
            "Accept": self.ACCEPT,
            "x-key": self.runtime.credentials.get("api_key", None),
        }
        if headers["x-key"] is None:
            raise Exception(
                "No Black Forest Labs API key set."
            )
        response = self._make_request(
            headers, data, region
        )

        if response.status_code == 200:
            id = response.json().get("id")
            image_url = self._poll_for_result(id, headers, region)
            yield self.create_image_message(image_url)
        else:
            try:
                error_info = response.json()
            except ValueError:
                error_info = response.text
            raise Exception(
                f"BFL API Message: {error_info}"
            )
