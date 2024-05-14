from service.discord_http_service import DiscordHttpService
import redis
from support.mj_config import MjConfig
from service.template_controller import TemplateController
from support.mj_account import MjAccount
import random

class LoadBalancer:
    def __init__(self, mj_config: MjConfig, redis_client: redis.Redis, template_controller: TemplateController):
             
        self.mj_config = mj_config.mj_config
        self.redis_client = redis_client
        self.template_controller = template_controller

        self.discord_http_services = []
        self.init_discord_http_services()

    def init_discord_http_services(self):
        discord_http_services = []
        for i in range(len(self.mj_config['accounts'])):
            account = self.mj_config['accounts'][i]
            mj_account = MjAccount(account)
            discord_http_services.append(DiscordHttpService(
                self.mj_config, self.redis_client, self.template_controller,mj_account))

        self.discord_http_services = discord_http_services

    def get_discord_http_service(self) -> DiscordHttpService:
        index = random.randint(0, len(self.discord_http_services)-1)
        return self.discord_http_services[index]
