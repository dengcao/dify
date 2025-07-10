## baidu-ocr

**Author:** biow
**Version:** 0.0.1
**Type:** tool
**Conatact me:** fuduoster@gmail.com

### Description
Integrate directly with [Baidu OCR](https://cloud.baidu.com/doc/OCR/s/Ek3h7xypm), and you can conveniently call Baidu OCR to recognize images/PDF files.

### Usage
1. Install the plugin fullfill the APP ID, API KEY, SECRET KEY, the above information needs to be obtained through the official website of Baidu OCR after registration and application.
2. Use the plugin in the Dify plugin environment.
3. Currently supported recognition modes, **new modes will be updated continuously**
   1. General text recognition

### Notice
While your Dify as self-hosted with docker compose, ensure the configuration item `FILES_URL` in `.env` is correctly filled. More details can be found in the [Dify documentation](https://docs.dify.ai/en/getting-started/install-self-hosted/environments#files-url).

### 有什么用
直接和百度OCR集成，可以方便的调用[百度ocr](https://cloud.baidu.com/doc/OCR/s/Ek3h7xypm)实现图片/PDF文件的识别

### 如何使用
1. 安装插件，填入APP ID, API KEY, SECRET KEY,以上信息需要通过百度OCR官网申请注册后获得.
2. 在Dify插件环境中使用插件.
3. 当前支持的识别模式,后续将持续更新
   1. 通用文字识别

### 注意
如果你的Dify是自托管的docker compose，确保`.env`中的`FILES_URL`配置项正确填写.更多详情可以查看[Dify文档](https://docs.dify.ai/en/getting-started/install-self-hosted/environments#files-url).