### 项目介绍

Dify一键离线安装包，集成安装了全部插件、模板，并集成了dify全部插件所需的依赖组件。方便你在内网、安可环境等离线状态下使用。

Dify是一个开源的LLM应用开发平台。其直观的界面结合了AI工作流、RAG管道、Agent、模型管理、可观测性功能等，让您可以快速从原型到生产。

### 对应Dify版本

Dify v1.5.1

### Dify离线安装包仓库

国外：[https://github.com/dengcao/dify](https://github.com/dengcao/dify)

国内：[https://gitee.com/dengzhenhua/dify](https://gitee.com/dengzhenhua/dify)

### Dify官方仓库

仓库：[https://github.com/langgenius/dify](https://github.com/langgenius/dify)

中文文档：[https://github.com/langgenius/dify/blob/main/README_CN.md](https://github.com/langgenius/dify/blob/main/README_CN.md)

### Docker安装方法（内网离线安装）

 **1、下载整个Dify离线安装包项目到本地：** git clone https://github.com/dengcao/dify.git

 **2、将./Docker-image/目录下全部镜像文件（.tar）导入到docker。
 
 其中，文件“dify-plugin-daemon-0.1.3-local-20250710.7z”需要先解压，得到文件“dify-plugin-daemon-0.1.3-local-20250710.tar”。
 
 导入到docker的具体代码如下：** 

```
cd ./Docker-image/
docker load -i dify-api_1.5.1.tar
docker load -i dify-plugin-daemon-0.1.3-local-20250710.tar
docker load -i dify-sandbox_0.2.12.tar
docker load -i dify-web_1.5.1.tar
docker load -i nginx.tar
docker load -i postgres_15-alpine.tar
docker load -i redis_6-alpine.tar
docker load -i squid.tar
```

 **3、创建容器，执行命令：** 

```
cd ./dify/
docker compose up -d
```

### Docker安装方法（联网安装）

 **1、下载整个Dify离线安装包项目到本地：** git clone https://github.com/dengcao/dify.git
 
 注意：联网安装时，可以不下载镜像包。docker镜像包目录：./Docker-image/

 **2、执行命令：** 

```
cd ./dify/
docker compose up -d
```

### 登录地址和账号

访问：http://localhost:8062/

邮箱：dzh188@qq.com  密码：admin@85u2x

用户名：admin
