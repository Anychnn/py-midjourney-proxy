<div align="center">

<h1 align="center">py-midjourney-proxy</h1>

English | [中文](./README_CN.md)

An unofficial python implementation of the Discord proxy for MidJourney.

One command to build your own MidJourney proxy server.
</div>


## Main Functions

- [x] Supports Imagine instructions and related actions
- [x] Supports adding image base64 as a placeholder when using the Imagine command
- [x] Supports Blend (image blending) and Describe (image to text) commands
- [x] Supports real-time progress tracking of tasks
- [x] Prompt sensitive word pre-detection, supports override adjustment
- [x] User-token connects to WSS (WebSocket Secure), allowing access to error messages and full functionality
- [x] Supports multi-account configuration, with each account able to set up corresponding task queues

## Prerequisites for use

1. Register and subscribe to MidJourney, create `your own server and channel`, refer
   to https://docs.midjourney.com/docs/quick-start
2. Obtain user Token, server ID, channel ID: [Method of acquisition](./docs/discord-params.md)

## Quick Start

1. `Railway`: Based on the Railway platform, no need for your own server: [Deployment method](./docs/railway-start.md) ;
   If Railway is not available, you can start using Zeabur instead.
2. `Zeabur`: Based on the Zeabur platform, no need for your own server: [Deployment method](./docs/zeabur-start.md)
3. `Docker`: Start using Docker on a server or locally: [Deployment method](./docs/docker-start.md)

## Local development

- Depends on python and fastapi
- Change configuration items: Edit resources/config/prod_mj_config.yaml
- Project execution: Start the main.py

## Configuration items

- mj.accounts: Refer
  to [Account pool configuration](./docs/config.md#%E8%B4%A6%E5%8F%B7%E6%B1%A0%E9%85%8D%E7%BD%AE%E5%8F%82%E8%80%83)
- mj.task-store.type: Task storage method, default is in_memory (in memory, lost after restart), Redis is an alternative
  option.
- mj.task-store.timeout: Task storage expiration time, tasks are deleted after expiration, default is 30 days.
- mj.api-secret: API key, if left empty, authentication is not enabled; when calling the API, you need to add the
  request header 'mj-api-secret'.
- mj.translate-way: The method for translating Chinese prompts into English, options include null (default), Baidu, or
  GPT.
- For more configuration options, see [Configuration items](./docs/config.md)

## Related documentation

1. [API Interface Description](./docs/api.md)
2. [Version Update Log](https://github.com/novicezk/midjourney-proxy/wiki/%E6%9B%B4%E6%96%B0%E8%AE%B0%E5%BD%95)

## Precautions

1. Frequent image generation and similar behaviors may trigger warnings on your Midjourney account. Please use with
   caution.
2. For common issues and solutions, see [Wiki / FAQ](https://github.com/novicezk/midjourney-proxy/wiki/FAQ)
3. Interested friends are also welcome to join the discussion group. If the group is full from scanning the code, you
   can add the administrator’s WeChat to be invited into the group. Please remark: mj join group.

 <img src="https://raw.githubusercontent.com/novicezk/midjourney-proxy/main/docs/manager-qrcode.png" width="220" alt="微信二维码"/>

## Application Project

If you have a project that depends on this one and is open source, feel free to contact the author to be added here for
display.

- [wechat-midjourney](https://github.com/novicezk/wechat-midjourney) : A proxy WeChat client that connects to
  MidJourney, intended only as an example application scenario, will no longer be updated.
- [chatgpt-web-midjourney-proxy](https://github.com/Dooy/chatgpt-web-midjourney-proxy) : chatgpt web, midjourney,
  gpts,tts, whisper A complete UI solution
- [chatnio](https://github.com/Deeptrain-Community/chatnio) : The next-generation AI one-stop solution for B/C end, an aggregated model platform with exquisite UI and powerful functions
- [new-api](https://github.com/Calcium-Ion/new-api) : An API interface management and distribution system compatible with the Midjourney Proxy
- [stable-diffusion-mobileui](https://github.com/yuanyuekeji/stable-diffusion-mobileui) : SDUI, based on this interface
  and SD (System Design), can be packaged with one click to generate H5 and mini-programs.
- [MidJourney-Web](https://github.com/ConnectAI-E/MidJourney-Web) : 🍎 Supercharged Experience For MidJourney On Web UI

## Open API

Provides unofficial MJ/SD open API, add administrator WeChat for inquiries, please remark: api

## Others

If you find this project helpful, please consider giving it a star.

[![Star History Chart](https://github.com/Anychnn/py-midjourney-proxy/svg?repos=Anychnn/py-midjourney-proxy&type=Date)](https://star-history.com/#Anychnn/py-midjourney-proxy&Date)
