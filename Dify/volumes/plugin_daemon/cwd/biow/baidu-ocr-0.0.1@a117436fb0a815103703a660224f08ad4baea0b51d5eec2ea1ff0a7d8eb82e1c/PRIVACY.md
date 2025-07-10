### baidu-ocr 插件隐私政策准则 Plugin Privacy Policy Guidelines

#### 中文版本

##### 1. 数据收集声明
本插件作为百度OCR服务的中间件，**不收集、存储或保留任何用户数据**。所有图像处理请求通过百度OCR API实时传输，处理完成后结果直接返回用户，插件系统不保留任何信息。

##### 2. 第三方数据处理
- 插件调用百度OCR服务时，用户图像数据将传输至百度服务器
- 百度OCR可能涉及的数据类型（根据使用场景）：
  - 📄 证件类：身份证/护照/驾驶证等包含的个人信息
  - 📑 文档类：票据/合同中的文字内容
  - 🖼️ 图像元数据：图片基础属性信息
- 百度OCR数据处理遵守其[隐私政策](https://ai.baidu.com/ai-doc/REFERENCE/Jky9l49bk)
- 百度OCR[合规指南](https://cloud.baidu.com/doc/OCR/s/3lr4w181z)要求：
  - 🔐 SDK初始化需在用户授权后进行
  - ⚠️ 需明确申请相机/相册权限（适用时）

##### 3. 数据安全措施
| 环节        | 保障方式                     |
|-------------|------------------------------|
| 传输安全    | HTTPS加密传输                |
| 数据处理    | 百度OCR服务器端即时处理       |
| 数据留存    | 插件系统零留存               |
| 权限控制    | 仅请求必要的OCR功能权限       |

##### 4. 用户权利保障
用户可通过以下方式控制数据：
1. 🚫 拒绝授予相机/相册权限
2. 📵 不在插件中提交敏感文件
3. 🗑️ 通过[百度OCR控制台](https://console.bce.baidu.com/ai/#/ai/ocr/overview/index)申请数据删除

---

#### English Version

##### 1. Data Collection Statement
This plugin acts as middleware for Baidu OCR services and **does not collect, store, or retain any user data**. All image processing requests are transmitted in real-time via Baidu OCR API, with results returned directly to users without retention.

##### 2. Third-party Data Processing
- When invoking Baidu OCR services, user image data is transmitted to Baidu servers
- Potential data types processed by Baidu OCR (scenario-dependent):
  - 📄 Identification documents: Personal information from IDs/passports/driver licenses
  - 📑 Documents: Text content from invoices/contracts
  - 🖼️ Image metadata: Basic image attributes
- Baidu OCR complies with its [Privacy Policy](https://ai.baidu.com/ai-doc/REFERENCE/Jky9l49bk)
- Requirements from Baidu OCR [Compliance Guide](https://cloud.baidu.com/doc/OCR/s/3lr4w181z):
  - 🔐 SDK initialization must occur after user authorization
  - ⚠️ Explicit camera/album permission requests (when applicable)

##### 3. Security Measures
| Phase         | Safeguards                         |
|---------------|-------------------------------------|
| Transmission  | HTTPS encrypted transfer            |
| Processing    | Real-time server-side processing    |
| Data Retention| Zero data persistence in plugin     |
| Access Control| Minimal necessary OCR permissions   |

##### 4. User Rights
Users maintain control through:
1. 🚫 Denying camera/album permissions
2. 📵 Avoiding submission of sensitive documents
3. 🗑️ Requesting data deletion via [Baidu OCR Console](https://console.bce.baidu.com/ai/#/ai/ocr/overview/index)

---

#### Manifest 文件配置示例
```json
{
  "schema_version": "v1",
  "name_for_human": "OCR处理器",
  "name_for_model": "ocr_processor",
  "description_for_human": "通过百度OCR实现图像文字提取",
  "description_for_model": "Extracts text from images using Baidu OCR technology",
  "privacy_policy_url": "https://your-domain.com/ocr-privacy-policy",
  "apis": [
    {
      "endpoint": "/ocr",
      "method": "POST"
    }
  ],
  "auth": {
    "type": "none"
  }
}