from injector import Injector, Module, provider, singleton
import redis
import yaml
from support.task_controller import TaskController
from support.mj_config import MjConfig
from wss.mj_wss_proxy import MjWssSercice
from service.discord_http_service import DiscordHttpService
from service.mj_data_service import MjDataService
from service.template_controller import TemplateController
from service.notify_service import NotifyService
from support.load_balancer import LoadBalancer
from wss.mj_wss_manager import MjWssManager


class SupportModule(Module):

    @provider
    @singleton
    def provide_mj_config(self) -> MjConfig:
        mj_config = MjConfig()
        return mj_config

    @provider
    @singleton
    def provide_redis(self, mj_config: MjConfig) -> redis.Redis:
        config = mj_config.mj_config
        redis_client = redis.Redis(host=config['redis']['host'],
                                   port=config['redis']['port'],
                                   db=config['redis']['db'],
                                   password=config['redis']['password'])
        return redis_client

    @provider
    @singleton
    def provide_task_controller(self, redis_client: redis.Redis, load_balancer: LoadBalancer, mj_data_service: MjDataService) -> TaskController:
        task_controller = TaskController(
            redis_client, load_balancer, mj_data_service)
        return task_controller

    @provider
    @singleton
    def provide_mj_data_service(self, redis_client: redis.Redis) -> MjDataService:
        mj_data_service = MjDataService(redis_client)
        return mj_data_service

    @provider
    @singleton
    def provide_template_controller(self,) -> TemplateController:
        template_controller = TemplateController()
        return template_controller

    
    @provider
    @singleton
    def provide_notify_service(self, redis_client: redis.Redis) -> NotifyService:
        notify_service = NotifyService(redis_client)
        return notify_service
    
    @provider
    @singleton
    def provide_load_balancer(self, mj_config: MjConfig, redis_client: redis.Redis, template_controller: TemplateController) -> LoadBalancer:
        load_balancer = LoadBalancer(mj_config, redis_client, template_controller)
        return load_balancer
    
    @provider
    @singleton
    def provide_mj_wss_manager(self, mj_config: MjConfig, redis_client: redis.Redis, mj_data_service: MjDataService, notify_service: NotifyService) -> MjWssManager:
        mj_wss_manager = MjWssManager(mj_config, redis_client, mj_data_service, notify_service)
        return mj_wss_manager

# 创建注入器
injector = Injector([SupportModule()])
