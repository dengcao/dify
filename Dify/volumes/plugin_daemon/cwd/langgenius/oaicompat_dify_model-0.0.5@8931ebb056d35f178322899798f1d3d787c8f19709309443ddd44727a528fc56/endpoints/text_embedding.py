import json
from typing import Mapping, Optional
from werkzeug import Request, Response
from dify_plugin import Endpoint
from dify_plugin.entities.model.text_embedding import (
    TextEmbeddingModelConfig,
)
from endpoints.auth import BaseAuth


class OaicompatDifyModelEndpoint(Endpoint, BaseAuth):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the text embedding endpoint with the given request.
        """
        if not self.verify(r, settings):
            return Response(
                json.dumps({"message": "Unauthorized"}),
                status=401,
                content_type="application/json",
            )

        model: Optional[dict] = settings.get("text_embedding", None)
        if not model:
            raise ValueError("Text embedding model is not set")

        data = r.get_json(force=True)
        if not data:
            raise ValueError("Request body is empty")

        texts: list[str] = []
        if isinstance(data.get("input"), str):
            texts.append(data.get("input"))
        elif isinstance(data.get("input"), list):
            texts = data.get("input")
        else:
            raise ValueError("Invalid input type")

        text_embedding_response = self.session.model.text_embedding.invoke(
            model_config=TextEmbeddingModelConfig(**model),
            texts=texts,
        )

        return Response(
            json.dumps(
                {
                    "object": "list",
                    "data": [
                        {
                            "object": "embedding",
                            "embedding": embedding,
                            "index": index,
                        }
                        for index, embedding in enumerate(text_embedding_response.embeddings)
                    ],
                    "usage": {
                        "prompt_tokens": text_embedding_response.usage.total_tokens,
                        "total_tokens": text_embedding_response.usage.total_tokens,
                    },
                    "model": text_embedding_response.model,
                }
            ),
            status=200,
            content_type="application/json",
        )
