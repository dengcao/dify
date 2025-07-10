# 📦 File Tools - A collection of various tools for handling file object

- **Plugin ID** : kurokobo/file_tools
- **Author** : kurokobo
- **Type** : tool
- **Repository** : https://github.com/kurokobo/dify-plugin-collection
- **Marketplace** : https://marketplace.dify.ai/plugins/kurokobo/file_tools

## ✨ Overview

A collection of various tools for handling file objects:

- **Dump to JSON**
  - Dump a file object as a JSON string for debugging
- **Embed as Base64**
  - Convert a file to data URI format (Base64 encoded), optionally in markdown format
- **Get Download URL**
  - Get a download URL for a file object, optionally as a markdown link
- **Save as File**
  - Save input text or base64 encoded binary data as a file with specified file name and MIME type

## 🛠️ Bundled Tools

### ✅ Dump to JSON

This is a tool to dump a file object as a JSON string for debugging purposes. This is an example of the output:

```json
{
  "dify_model_identity": "__dify__file__",
  "url": "https://upload.dify.ai/files/tools/62edee2e-ac72-43fc-aa6a-c8b82ba2f0d3.md?timestamp=...&nonce=...&sign=...",
  "mime_type": "text/markdown",
  "filename": "sample.md",
  "extension": ".md",
  "size": 861,
  "type": "document",
  "blob": "IyBBIHNhbXBsZSBv...RWxGVGtTdVFtQ0Mp"
}
```

This tool is useful for inspecting a file object.

You can choose whether to include the base64 encoded binary data in the `blob` field, by `include_blob` option.

### ✅ Embed as Base64

This is a tool to convert a file to data URI format (Base64 encoded) such as:

```markdown
# Converted PNG image, in "plain" format
data:image/png;base64,iVBORw0KGgoAAAAN...AAAAAElFTkSuQmCC

# Converted PNG image, in "markdown" format
![Awesome Image](data:image/png;base64,iVBORw0KGgoAAAAN...AAAAAElFTkSuQmCC)

# Converted text file, in "plain" format
data:text/plain;base64,SGVsbG8sIHdvcmxkIQ==

# Converted text file, in "markdown" format
[Click to View Text](data:text/plain;base64,SGVsbG8sIHdvcmxkIQ==)
```

This tool is useful for embedding files or images directly into markdown documents, HTML pages, or any other formats that support data URIs.

If you select the `plain` format (default), the output will be a plain data URI string.
If you select the `markdown` format, the output will be an image (`![text](...)`) or a link (`[text](...)`) depending on whether the file is an image or not.  
You can customize the link text (or alt text for images) by using the `link_text` option. If the `link_text` is not provided, it will default to the file name.

The MIME type will be automatically determined based on the file name, but you can also pass a MIME type explicitly using the `mime_type` option.

### ✅ Get Download URL

This is a tool to generate a download link for a file object, either as a plain URL or in markdown format:

```markdown
# In "plain" format
https://upload.dify.ai/files/tools/62edee2e-ac72-43fc-aa6a-c8b82ba2f0d3.md?timestamp=...&nonce=...&sign=...

# In "markdown" format
[Click to Download](https://upload.dify.ai/files/tools/62edee2e-ac72-43fc-aa6a-c8b82ba2f0d3.md?timestamp=...&nonce=...&sign=...)
```

This tool is useful when you want to pass a file download link to another node, or when you want to embed a file download link as part of a nicely formatted chatbot response.

If you select the `plain` format (default), the output will be a plain URL string.
If you select the `markdown` format, the output will be a link (`[text](...)`) with the file name or a custom text (by `link_text`).

### ✅ Save as File

This is a tool to save input text or base64 encoded binary data as a file. You can specify the file name, MIME type, and the format of the content:

- To save plain text as a file:
  - `content`: `Hello, world!`
  - `filename`: `hello.txt`
  - `format`: `text`

- To save base64 encoded data as a file:
  - `content`: `SGVsbG8sIHdvcmxkIQ==`
  - `filename`: `hello.txt`
  - `format`: `base64`

This tool is useful for saving generated content or decoded binary data as a downloadable file.

If you leave the MIME type empty, it will be automatically determined based on the file name. Of course, you can also specify a MIME type explicitly using the `mime_type` option.

## Related Links

- **Icon**: [Heroicons](https://heroicons.com/)
