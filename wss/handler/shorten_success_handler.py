from wss.handler.base_message_handler import MessageHandler
import redis
import re
import json
from service.mj_data_service import MjDataService, MjTask
import logging
from service.notify_service import NotifyService

logger = logging.getLogger(__name__)

class DescribeSuccessHandler(MessageHandler):

    def __init__(self, redis_client: redis.Redis, mj_data_service: MjDataService, notify_service: NotifyService) -> None:
        self.redis_client = redis_client
        self.mj_data_service = mj_data_service
        self.notify_service = notify_service
        

    def handle(self, message):
        op = message['op']
        t = message['t']
        if t == 'MESSAGE_UPDATE':
            d = message['d']
            # nonce = d['nonce']
            content = d['content']
            message_id = d['id']
            d_type = d['type']
            if "embeds" not in d or len(d['embeds'])==0:
                return
            
            if d_type == 19:
                embed = d['embeds'][0]
                description = embed['description']
                image_url = embed['image']['url']
                
                target_task = None
                task_list: list[MjTask] = self.mj_data_service.get_tasks_list()
                
                for task in task_list:
                    if task.task_status == 'pending' and task.image_prompt == image_url and task.task_type == 'shorten':
                        target_task = task
                        break
                    
                if target_task:
                    self.mj_data_service.update_task_status(
                        target_task, "success")
                    self.mj_data_service.update_task_description(
                        target_task, description)
                    self.mj_data_service.update_task_progress(
                        target_task, "100%")
                    self.notify_service.notify_task_change(target_task)
                    d['mj_proxy_handled'] = True