from wss.handler.base_message_handler import MessageHandler
import redis
import re
import json
from service.mj_data_service import MjDataService, MjTask
import logging
from service.notify_service import NotifyService

logger = logging.getLogger(__name__)

class ImagineHandler(MessageHandler):

    def __init__(self, redis_client: redis.Redis, mj_data_service: MjDataService, notify_service: NotifyService) -> None:
        self.redis_client = redis_client
        self.mj_data_service = mj_data_service
        self.notify_service = notify_service
        # "**a white haired boy --niji 5** - <@1233674918630264866> (Waiting to start)"
        self.prompt_pattern = re.compile("\*\*(.*?)\*\* - <@\d+> \((.*?)\)")
        
    def extract_prompt(self,prompt):
        prompt_pattern = re.compile("\*\*(.*?)\*\* - <@\d+> \((.*?)\)")
        matched = prompt_pattern.match(prompt)
        if matched:
            return matched.group(1)
        # if matched:
        #     inner_prompt = matched.group(1)

        #     image_pattern = re.compile("<(.*?)> (.*)")
        #     inner_mathed = image_pattern.match(inner_prompt)
        #     if inner_mathed:
        #         image_url = inner_mathed.group(1)
        #         prompt = inner_mathed.group(2)
        #         return image_url, prompt
        #     else:
        #         return None, inner_prompt
        else:
            raise Exception("prompt format error")

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

            # '<https://s.mj.run/8rzEv9vkgbg> a white haired boy --niji 5 --relax'
            
            if d_type == 0:
                # Imagine已经完成
                task_list: list[MjTask] = self.mj_data_service.get_tasks_list()
                # 查找条件：
                # 1. 任务状态为pending
                # 2. 任务的prompt相等
                # 3. task_type为imagine
                # print("finished")
                target_task = None
                for task in task_list:
                    
                    if task.task_status == 'pending' and task.submit_prompt == prompt:
                        target_task = task
                        break
                    # if img_promot:
                    #     if task.task_status == 'pending' and task.prompt == prompt and task.task_type == 'imagine' and task.image_prompt!=None:
                    #         target_task = task
                    #         break
                    # else:
                    #     if task.task_status == 'pending' and task.prompt == prompt and task.task_type == 'imagine':
                    #         target_task = task
                    #         break

                if target_task and len(attachments) > 0:
                    
                    buttons = self.get_buttons(d)
                    self.mj_data_service.update_buttons(target_task, buttons)
                    

                    self.mj_data_service.update_finished_message_id(
                        target_task, message_id)
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
                else:
                    raise Exception("no task found")

            elif d_type == 20:
                # Imagine创建成功
                nonce = d['nonce']
                
                task = self.mj_data_service.get_task_by_nonce(nonce)
                if not task:
                    logger.error(f"no task found, nonce: {nonce}")
                    return 
                
                task.submit_prompt = prompt
                self.mj_data_service.update_task_progress(
                        task, "0%")
                self.mj_data_service.update_task_nonce(task, nonce)
                self.mj_data_service.update_task_message_id(task, message_id)
                self.mj_data_service.update_message_id_map(task)
                self.notify_service.notify_task_change(task)
                
                d['mj_proxy_handled'] = True

        elif t == 'MESSAGE_UPDATE':
            d = message['d']
            # nonce = d['nonce']
            content = d['content']
            attachments = d['attachments']
            if not content:
                return
            message_id = d['id']
            d_type = d['type']
            if d_type == 20:
                # '**a white haired girl --niji 5** - <@1233674918630264866> (15%) (relaxed)'
                # 提取出content中的进度
                matched = self.prompt_pattern.findall(content)
                prompt = matched[0][0] if matched else None
                progress = matched[0][1] if matched else None
                channel_id = d['channel_id']
                task = self.mj_data_service.get_task_by_message_id(message_id)
                
                if not task:
                    logger.error(f"no task found, message_id: {message_id}")
                    return
                self.mj_data_service.update_task_progress(task, progress)
                if len(attachments):
                    self.mj_data_service.update_task_image_url(
                        task, attachments[0]['url'])
                    
                self.notify_service.notify_task_change(task)
                d['mj_proxy_handled'] = True
                print(
                    f'imagine message update :channel_id:{channel_id},content:{content}message_id:{message_id},progress:{progress}')
