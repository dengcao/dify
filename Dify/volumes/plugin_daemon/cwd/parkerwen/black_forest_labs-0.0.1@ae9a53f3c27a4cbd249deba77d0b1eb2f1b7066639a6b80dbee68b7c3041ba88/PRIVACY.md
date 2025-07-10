# Privacy Policy for Black Forest Labs Plugin

_Last updated: 2025-06-27_

This plugin ("Black Forest Labs Plugin") interacts with the Black Forest Labs (BFL) image generation API. This privacy policy outlines the data handled by the plugin and its behavior when processing requests.

## 1. Data Collected

The plugin collects and transmits the following data to the BFL API servers for the purpose of generating images:

- **Text prompts** (`prompt`)
- **Optional images** provided by the user (e.g., `image_prompt`, `control_image`, `mask`, `image`)
- **Optional parameters** such as `seed`, `guidance`, `steps`, `width`, `height`, etc.
- **API Key** for authenticating with the BFL API

No personally identifiable information (PII) is required or intentionally collected by the plugin itself. However, users should avoid including sensitive or personal data in text or image prompts.

## 2. Data Transmission and Storage

- All data is transmitted to the BFL API over HTTPS using secure connections.
- The plugin does **not store any data** locally or externally. Data is held temporarily in memory for the duration of a single API request.
- The BFL API may log or process prompts and images according to its own privacy policy. Please refer to [https://bfl.ai](https://bfl.ai) or contact Black Forest Labs directly for details about their data handling.

## 3. Third-Party Services

This plugin relies entirely on the following third-party service:

- **Black Forest Labs API** (https://api.bfl.ml and https://api.us1.bfl.ai)

The service provider may process the content provided to the plugin, including prompts and images. Please consult their own privacy documentation for further details.

## 4. User Control

- The plugin includes options to adjust or omit image inputs, prompts, and related parameters.

## 5. Data Retention

The plugin does not retain any data after image generation is complete. All intermediate data (e.g., base64-encoded images, responses) is discarded from memory after processing.

## 6. Security Measures

- Data is sent only to trusted, predefined BFL API endpoints over HTTPS.
- API keys are loaded securely from user input.
- Base64 encoding is used for transmitting images and masks in a format accepted by the BFL API.

## 7. Contact

If you have questions or concerns regarding the privacy practices of this plugin, please contact the developer or the plugin maintainer.

---

**Disclaimer**: The use of this plugin and the BFL API is subject to each platform's respective privacy and terms of use policies. This plugin does not guarantee full compliance with any data protection regulation (e.g., GDPR, CCPA) when used outside a controlled environment.