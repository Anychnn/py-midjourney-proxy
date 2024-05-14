
from queue import Queue
import json
from dataclasses import dataclass,field
from datetime import datetime
from typing import Optional
import redis
from typing import List

def default_custom_ids():
    return []

@dataclass(init=False)
class MjTask:
    # 任务类型
    task_type: Optional[str] = None
    # 任务状态
    task_status: Optional[str] = None
    # task_id
    task_id: Optional[str] = None
    # 提示词
    prompt: Optional[str] = None
    # 提示词-英文
    promptEn: Optional[str] = None
    # 任务描述
    description: Optional[str] = None
    # 提交时间
    create_time: Optional[datetime] = None
    # 开始执行时间
    start_time: Optional[datetime] = None
    # 结束时间
    end_time: Optional[datetime] = None
    # 图片url
    image_url: Optional[str] = None
    # 进度
    progress: Optional[str] = None
    # 失败原因
    fail_reason: Optional[str] = None
    # 回调地址
    notify_hook: Optional[str] = None

    nonce: Optional[str] = None
    
    image_prompt: Optional[str] = None
    
    # mj返回的任务创建的prompt
    submit_prompt: Optional[str] = None
    
    # 之前对应的message_id
    message_id: Optional[str] = None
    reference_message_id: Optional[str] = None
    
    
    finished_message_id: Optional[str] = None
    
    buttons: Optional[List[str]] = None
    
    # action
    custom_id: Optional[str] = None
    
    # upscale
    upscale_custom_ids: List[str] = field(default_factory=default_custom_ids)
    custom_upscale_id: Optional[str] = None
    upscale_index: Optional[int] = None
    
    # variation
    variation_custom_ids: List[str] = field(default_factory=default_custom_ids)
    custom_variation_id: Optional[str] = None
    variation_index: Optional[int] = None
    
    
    # description
    description: Optional[str] = None
    
    # blend
    blend_imgs: Optional[List[str]] = None
    dimensions: Optional[str]

class MjDataService:
    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis_client = redis_client
        self.mj_tasks = Queue()
        self.mj_tasks_list = []
        self.task_id_map = {}
        self.nonce_map = {}
        self.message_id_map = {}

    def next_nonce(self):
        nonce = self.redis_client.get("mj.nonce")
        if nonce is None:
            nonce = 1
            self.redis_client.set("mj.nonce", nonce)
        # 将redis中的nonce加1
        nonce = self.redis_client.incr("mj.nonce")
        return nonce
    def get_tasks_queue(self) -> Queue:
        return self.mj_tasks
    
    def get_tasks_list(self) -> list:
        return self.mj_tasks_list
    def add_task(self, task: MjTask) -> None:
        self.mj_tasks.put(task)
        self.task_id_map[task.task_id] = task
        self.nonce_map[task.nonce] = task
        self.mj_tasks_list.append(task)

    def get_task_by_nonce(self, nonce: str) -> Optional[MjTask]:
        return self.nonce_map.get(nonce)
    
    def get_task_by_task_id(self, task_id: str) -> Optional[MjTask]:
        return self.task_id_map.get(task_id)
    
    def get_task_by_message_id(self, message_id: str) -> Optional[MjTask]:
        return self.message_id_map.get(message_id)

    def update_task_nonce(self, task: MjTask, nonce):
        task.nonce = nonce

    def update_task_message_id(self, task: MjTask, message_id):
        task.message_id = message_id

    def update_task_progress(self, task: MjTask, progress: str) -> None:
        task.progress = progress
        
    def update_task_status(self, task: MjTask, status: str) -> None:
        task.task_status = status
        
    def update_task_image_url(self, task: MjTask, image_url: str) -> None:
        task.image_url = image_url
        
    def update_message_id_map(self,task:MjTask):
        self.message_id_map[task.message_id] = task
        
        
    def update_upsacle_custom_ids(self, task: MjTask, custom_ids: List[str]) -> None:
        task.upscale_custom_ids = custom_ids
    
    def update_variation_custom_ids(self, task: MjTask, custom_ids: List[str]) -> None:
        task.variation_custom_ids = custom_ids
        
    def update_finished_message_id(self, task: MjTask, finished_message_id: str) -> None:
        task.finished_message_id = finished_message_id
        
    def update_task_description(self, task: MjTask, description: str) -> None:
        task.description = description
        
    def update_buttons(self, task: MjTask, buttons: List[str]) -> None:
        task.buttons = buttons