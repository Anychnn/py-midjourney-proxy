from support.mj_config import MjConfig
import redis
import requests
import json
import datetime
from support.task_controller import MjTask
from service.template_controller import TemplateController
from service.mj_data_service import MjDataService
import logging
logger = logging.getLogger(__name__)


class NotifyService:
    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis_client = redis_client

    def notify_task_change(self, task: MjTask):
        if not task:
            return
        
        notify_hook = task.notify_hook
        if not notify_hook:
            return

        if not notify_hook.startswith("http"):
            return
        logger.info(
            f"notify_task_change, task_id: {task.task_id}, hook: {notify_hook}")

        try:
            req = {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "task_status": task.task_status,
                "image_url": task.image_url,
                "progress": task.progress,
                "action_index": task.upscale_index,
                "description": task.description,
                "buttons": task.buttons,
                "fail_reason":task.fail_reason
            }
            res = requests.post(notify_hook, json=req)
            # 如果为2xx
            if res.status_code // 100 == 2:
                logger.info(f"notify_task_change res 2xx, task_id: {task.task_id}, hook: {notify_hook}, res: {res.text}")
                return
            else:
                logger.error(
                    f"notify_task_change res not 2xx, task_id: {task.task_id}, hook: {notify_hook}, res: {res.text}")

        except Exception as e:
            logger.error(f"notify_task_change, task_id: {task.task_id}, hook: {notify_hook}, error: {e}")
            return