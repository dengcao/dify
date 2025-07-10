## Agora Conversational AI

**Author:** qz
**Version:** 0.0.9
**Type:** extension

### Description

#### Overview

This extension provides an endpoint to make Dify agents work with Agora’s Conversational AI Engine to easily turn your Dify agents into voice assistants.

#### Prerequisites

- **Agora Account**
    You need an Agora account to use the Agora Conversational AI service. You can sign up for a free account at [Agora](https://sso.agora.io/en/signup/).
- **Agora App ID / App Certificate / RESTful Customer ID / RESTful Customer Secret**
    You need to create an Agora project and get the App ID, App Certificate, RESTful Customer ID and RESTful Customer Secret from [Agora Console](https://console.agora.io/v2). Note to enable the Agora Conversational AI service in the Agora Console.
- **TTS Vendor Account**
    You need an account for the TTS vendor you choose. The TTS vendor provides the voice synthesis service for the voice assistant. 

#### Pre-requisites

- Agora account - Get it from [Agora Console](https://sso.agora.io/en/signup/).
- Agora App ID / App Certificate / RESTful Customer ID / RESTful Customer Secret - Get it from [Agora Console](https://console.agora.io/v2), and make sure the "Converstional AI Engine" service has been activated on Agora Console.
- TTS Vendor API Key - From [Microsoft Azure](https://portal.azure.com/) or [11labs](https://elevenlabs.io/app/settings/api-keys).

> Note: Currently this extension is not available to use with Shengwang account. If you are from Mainland China, please make sure you register an account from Agora.

#### Configuration

- **APP**
    To turn a Dify agent into a voice assistant, choose one from your agent library.
- **Agora App ID**
    The Agora App ID to use for RTC service. Get it from [Agora Console](https://console.agora.io/v2). Note to enable the Agora Conversational AI service in the Agora Console.
- **Agora RESTful Customer ID**
    The Agora RESTful Customer ID to use for RTC service. Get it from [Agora Console](https://console.agora.io/v2).
- **Agora RESTful Customer Secret**
    The Agora RESTful Customer Secret to use for RTC service. Get it from [Agora Console](https://console.agora.io/v2).
- **ASR Language**
    The language of the ASR (Automatic Speech Recognition) service. Choose one from the list below.
  - **English** (en-US)
  - **Chinese** (zh-CN)
  - **Japanese** (ja-JP)
- **TTS Vendor**
    The TTS vendor to use for voice synthesis. Choose one from the list below.
  - **Azure**
  - **ElevenLabs**
- **TTS Vendor Params**
    The parameters for the TTS vendor. The parameters are different for each vendor, please refer to the vendor's documentation for more information.
  - **Azure**

    ```json
    {
        "key": "<your api key>",
        "region": "eastasia",
        "voice_name": "en-US-AndrewMultilingualNeural"
    }
    ```

  - **11labs**

    ```json
    {
        "api_key": "<your api key>",
        "model_id": "eleven_flash_v2_5",
        "voice_id": "pNInz6obpgDQGcFmaJgB"
    }
    ```

- **Greeting Message**
    The message to greet the user when the conversation starts.
- **Failure Message**
    The message to tell the user when the conversation fails.
- **Agora App Certificate**
    The Agora App Certificate to use for RTC service. Get it from [Agora Console](https://console.agora.io/v2). Only needed when security token is enabled for your Agora project.
- **API Key**
    The API Key to protect your Dify endpoint.

#### Usage

Once you finish the configuration, you'll fnd the APl in the endpoint as follows:

`https://qv90***.ai-plugin.io/convoai-web/<file>`

Replace `<file>` with `index.html`,

Then you may navigate to the following URL to access the integrated Conversational Al web page.

`https://qv90***.ai-plugin.io/convoai-web/index.html`

#### Using API without Web Page

You can also use the API directly without the web page. The API endpoint is:

##### Start Conversation

API Endpoint: `https://qv90***.ai-plugin.io/convoai-start`

| key | value |
| --- | --- |
| base_url | The base url of the extension |
| channel | The channel id of the extension |

Example cURL:

```bash
curl 'https://qv90***.ai-plugin.io/convoai/convoai-start' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh,en;q=0.9,zh-CN;q=0.8' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  --data-raw '{"base_url":"https://qv90***.ai-plugin.io","channel":"jh0y8fgk7"}'
```

##### Stop Conversation

API Endpoint: `https://qv90***.ai-plugin.io/convoai-stop`

| key | value |
| --- | --- |
| agent_id | The agent id of the extension |

Example cURL:

```bash
curl 'https://qv90***.ai-plugin.io/convoai/convoai-stop' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh,en;q=0.9,zh-CN;q=0.8' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  --data-raw '{"agent_id":"1NT29X0ZX0JYPJ96CCL8F4Y4VUEGR566"}'
```
