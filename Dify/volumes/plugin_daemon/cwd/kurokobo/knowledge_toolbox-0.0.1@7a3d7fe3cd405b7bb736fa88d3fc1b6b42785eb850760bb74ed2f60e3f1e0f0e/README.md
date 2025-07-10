# 📦 Knowledge Toolbox - Small tools for working with Dify Knowledge API

- **Plugin ID** : kurokobo/knowledge_toolbox
- **Author** : kurokobo
- **Type** : tool
- **Repository** : https://github.com/kurokobo/dify-plugin-collection
- **Marketplace** : https://marketplace.dify.ai/plugins/kurokobo/knowledge_toolbox

## ✨ Overview

Small tools for working with Dify Knowledge API:

- ✅ **Download File**
  - Retrieve the uploaded file in Knowledge as a JSON, download URL, file object, or file content.
- ✅ **Get Full Doc**
  - Retrieve the full doc by concatenating all the chunks of the specified document in Knowledge.

## 🛠️ Bundled Tools

### ✅ Download File

This is a tool to retrieve the uploaded file in Knowledge.  
With this tool, you can use Knowledge like a simple file server. This is useful when you want to retrieve specific files or their contents within your workflow and use them as templates, for example.

If you want to retrieve the contents of a file that isn't plain text, the **✅ Get Full Doc** tool might be appropriate.

Required parameters:

- `api_base_url`
  - The base URL of the Knowledge API, with trailing `/v1`.
- `api_key`
  - The API key for the Knowledge API.
- `knowledge_id`
  - The ID of the Knowledge to retrieve the uploaded file from.
  - You can find this ID in the URL of each Knowledge page (`/datasets/<knowledge_id>`).
- `document_id`
  - The ID of the document that contains the uploaded file.
  - You can find this ID in the URL of each document page (`/datasets/<knowledge_id>/documents/<document_id>`).
- `format`
  - Format of the output. See following section for details.

You can choose the output format of the file:

- `json`
  - As `text` output variable.
  - Raw response from the Knowledge API: `/datasets/{dataset_id}/documents/{document_id}/upload-file` (`GET`).
- `url`
  - As `text` output variable.
  - Download URL of the file.
- `file`
  - As `files` output variable.
  - File object of the file.
- `content`
  - As `text` output variable.
  - Content of the file as a string.

### ✅ Get Full Doc

This is a tool to retrieve the full doc by concatenating all the chunks of the specified document in Knowledge.
With this tool, for example, you can force the LLM node to always refer to the entire content of a specific document, which is quite useful.

Required parameters:

- `api_base_url`
  - The base URL of the Knowledge API, with trailing `/v1`.
- `api_key`
  - The API key for the Knowledge API.
- `knowledge_id`
  - The ID of the Knowledge to retrieve the uploaded file from.
  - You can find this ID in the URL of each Knowledge page (`/datasets/<knowledge_id>`).
- `document_id`
  - The ID of the document that contains the uploaded file.
  - You can find this ID in the URL of each document page (`/datasets/<knowledge_id>/documents/<document_id>`).
- `delimiter`
  - The string inserted between each chunk while joining them together.

As `text` output variable, you can get the full doc of the specified document as a single (big, long) string by concatenating all of its chunks using the specified delimiter.

## Related Links

- **Icon**: [Heroicons](https://heroicons.com/)
