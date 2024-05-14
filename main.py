# -*- ecoding: utf-8 -*-
# @Author: anyang
# @Time: 2024/4/5

import asyncio
import uvicorn
from fastapi import FastAPI
from blueprints.blueprints_image_generation import image_router
import yaml
# from app.app import app
from support.mj_config import MjConfig
# from union_api_server.Injector import injector
from support.Injector import injector
import subprocess
from wss.mj_wss_proxy import MjWssSercice
from wss.mj_wss_manager import MjWssManager

router = FastAPI()
router.include_router(image_router, prefix="/image", tags=["图片生成"])

@router.on_event("startup")
async def startup_event():
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='union_api_server server.')
    parser.add_argument('--port', type=int, help='server port', default=6013)

    # 从injector获取mj_config
    mj_config = injector.get(MjConfig)
    
    # 启动 Celery worker
    # subprocess.Popen(['celery', '-A', 'celery_module.celery_app', 'worker', '--loglevel=INFO','-c',"1"])

    # 是否开启新的线程启动对discord_bot的wss监听
    # if mj_config.mj_config["common"]["launch_discord_bot"]:
    mj_wss_manager = injector.get(MjWssManager)
    mj_wss_manager.start_all()

    args = parser.parse_args()
    uvicorn.run(router, port=args.port, host="0.0.0.0")
