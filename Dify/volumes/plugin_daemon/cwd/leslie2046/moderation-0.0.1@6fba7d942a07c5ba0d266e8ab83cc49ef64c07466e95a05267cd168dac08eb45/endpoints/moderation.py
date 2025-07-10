import json
from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint


class ModerationEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        body = r.get_json()
        point = body.get("point")
        params = body.get("params", {})
        auth_header = r.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response("Missing or invalid Authorization header", status=401)

        api_key = auth_header[len("Bearer "):].strip()
        expected_key = settings.get("api_key", "")

        if api_key != expected_key:
            return Response("Invalid API key", status=403)

        keywords_text = settings.get("keywords", "")
        input_preset_response = settings.get("input_preset_response", "The content contains illegal content")
        output_preset_response = settings.get("output_preset_response", "The content contains illegal content")
        input_strategy = settings.get("input_strategy", "direct_output")
        output_strategy = settings.get("output_strategy", "direct_output")
        separator = settings.get("separator", " ")

        keywords = [kw.strip() for kw in keywords_text.strip().split(separator) if kw.strip()]

        # 1. ping
        if point == "ping":
            return Response(json.dumps({"result": "pong"}), status=200, content_type="application/json")

        # 2. app.moderation.input
        elif point == "app.moderation.input":
            inputs = params.get("inputs", {})
            query = params.get("query", "")

            flagged = False
            new_inputs = {}

            for k, v in inputs.items():
                if any(kw in v for kw in keywords):
                    flagged = True
                    new_inputs[k] = self._mask_words(v, keywords) if input_strategy == "overridden" else v
                else:
                    new_inputs[k] = v

            query_flagged = any(kw in query for kw in keywords)
            if query_flagged:
                flagged = True
                query = self._mask_words(query, keywords) if input_strategy == "overridden" else query

            if flagged:
                if input_strategy == "direct_output":
                    return Response(json.dumps({
                        "flagged": True,
                        "action": input_strategy,
                        "preset_response": input_preset_response
                    }), status=200, content_type="application/json")
                else:
                    return Response(json.dumps({
                        "flagged": True,
                        "action": input_strategy,
                        "inputs": new_inputs,
                        "query": query
                    }), status=200, content_type="application/json")
            else:
                return Response(json.dumps({
                    "flagged": False,
                    "action": "direct_output"
                }), status=200, content_type="application/json")

        # 3. app.moderation.output
        elif point == "app.moderation.output":
            text = params.get("text", "")
            flagged = any(kw in text for kw in keywords)

            if flagged:
                if output_strategy == "direct_output":
                    return Response(json.dumps({
                        "flagged": True,
                        "action": output_strategy,
                        "preset_response": output_preset_response
                    }), status=200, content_type="application/json")
                else:
                    return Response(json.dumps({
                        "flagged": True,
                        "action": output_strategy,
                        "text": self._mask_words(text, keywords)
                    }), status=200, content_type="application/json")
            else:
                return Response(json.dumps({
                    "flagged": False,
                    "action": "direct_output"
                }), status=200, content_type="application/json")

        return Response(json.dumps({
            "flagged": False,
            "action": "direct_output"
        }), status=200, content_type="application/json")

    def _mask_words(self, text: str, keywords: list[str]) -> str:
        for kw in keywords:
            text = text.replace(kw, "***")
        return text
