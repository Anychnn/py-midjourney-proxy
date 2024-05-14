
from service.mj_data_service import MjTask
from queue import Queue
import time
import threading
import redis
from service.discord_http_service import DiscordHttpService
from service.mj_data_service import MjDataService
from support.load_balancer import LoadBalancer
import uuid


def consume_tasks(mj_data_service: MjDataService, load_balancer: LoadBalancer):
    while True:
        task_queue = mj_data_service.get_tasks_queue()
        task: MjTask = task_queue.get()
        if task is None:
            continue
        
        # comsume任务
        if task.task_type is None:
            continue
        
        discord_http_service = load_balancer.get_discord_http_service()
        
        if task.task_type == "imagine":
            discord_http_service.imageine(task)
        elif task.task_type == "upscale":
            discord_http_service.upscale(task)
        elif task.task_type == "variation":
            discord_http_service.variation(task)
        elif task.task_type == "describe":
            discord_http_service.describe(task)
        elif task.task_type == "blend":
            discord_http_service.blend(task)
        elif task.task_type == "action":
            discord_http_service.action(task)
        elif task.task_type == "shorten":
            discord_http_service.shorten(task)
        else:
            print("unknown task type: " + task.task_type)

class TaskController:
    def __init__(self, redis_client: redis.Redis,load_balancer: LoadBalancer, mj_data_service: MjDataService) -> None:
        self.mj_data_service: MjDataService = mj_data_service
        
        # discord_http_service: DiscordHttpService
        consume_thread = threading.Thread(
            target = consume_tasks, args=(self.mj_data_service, load_balancer))
        consume_thread.daemon = True
        consume_thread.start()

    def submit_imagine(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def submit_upscale(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def submit_describe(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def submit_blend(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def submit_variation(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def submit_action(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def submit_shorten(self, task_data: MjTask):
        self.base_submit(task_data)
        return task_data.task_id

    def base_submit(self, task_data: MjTask):
        task_data.task_id = str(uuid.uuid4())
        self.mj_data_service.add_task(task_data)
        return task_data.task_id
