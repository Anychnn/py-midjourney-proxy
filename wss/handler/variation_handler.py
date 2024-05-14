from wss.handler.base_message_handler import MessageHandler
import redis
import re
import json
from service.mj_data_service import MjDataService,MjTask
from service.notify_service import NotifyService

class VariationHandler(MessageHandler):
    def __init__(self, redis_client: redis.Redis, mj_data_service: MjDataService, notify_service: NotifyService) -> None:
        self.redis_client = redis_client
        self.mj_data_service = mj_data_service
        self.notify_service = notify_service
        self.prompt_pattern = re.compile("\*\*(.*?)\*\* - <@\d+> \((.*?)\)")
        # "**a white haired boy --niji 5** - Image #1 <@1233674918630264866>"
        self.upscale_pattern = re.compile("\*\*(.*?)\*\* - Image #(\d) <@\d+>")
        # \*\*(.*?)\*\* - Variations \(.*?\) by <@\d+> \((.*?)\)
        self.variation_pattern = re.compile("\*\*(.*?)\*\* - Variations \(.*?\) by <@\d+> \((.*?)\)")
    def get_reference_message_id(self,d):
        return d['message_reference']['message_id']
    
    def get_buttons(self,d):
        buttons=[]
        for i in range(len(d['components'])):
            buttons.extend(d['components'][i]['components'])
        return buttons
    
    def handle(self, message):
        op = message['op']
        t = message['t']
        if t == 'MESSAGE_CREATE':
            d = message['d']
            message_id = d['id']
            d_type = d['type']
            channel_id = d['channel_id']
            content = d['content']
            attachments = d['attachments']
            matched = self.prompt_pattern.findall(content)
            prompt = matched[0][0] if matched else None
            progress = matched[0][1] if matched else None

            if d_type == 19:
                if 'Variations' in content:
                    reference_message_id = self.get_reference_message_id(d)
                    
                    target_task = None
                    task_list: list[MjTask] = self.mj_data_service.get_tasks_list()
                    matched = self.variation_pattern.findall(content)
                    upscale_index= matched[0][1] if matched else None
                    
                    for task in task_list:
                        if task.task_status == 'pending' and task.reference_message_id == reference_message_id and task.task_type == 'action':
                            target_task = task
                            break
                    if target_task and len(attachments) > 0:
                        
                        buttons = self.get_buttons(d)
                        self.mj_data_service.update_buttons(target_task, buttons)

                        self.mj_data_service.update_task_message_id(
                            target_task, message_id)
                        self.mj_data_service.update_task_status(
                            target_task, "success")
                        self.mj_data_service.update_task_image_url(
                            target_task, attachments[0]['url'])
                        self.mj_data_service.update_task_progress(
                            target_task, "100%")
                        
                        self.notify_service.notify_task_change(target_task)
                    d['mj_proxy_handled'] = True

