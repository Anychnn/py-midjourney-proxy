
from support.mj_config import MjConfig
import redis
from wss.mj_wss_proxy import MjWssSercice
from service.mj_data_service import MjDataService
from service.notify_service import NotifyService
from support.mj_account import MjAccount
from typing import List

class MjWssManager:
    def __init__(self, mj_config: MjConfig, redis_client: redis.Redis, mj_data_service: MjDataService, notify_service: NotifyService) -> None:
        self.mj_config = mj_config
        self.redis_client = redis_client
        self.mj_data_service = mj_data_service
        self.notify_service = notify_service
        self.wss_list:List[MjWssSercice] = []
        self.init_wss_list()

    def init_wss_list(self):
        mj_accounts = self.mj_config.get_accounts()
        for account in mj_accounts:
            mj_account = MjAccount(account)
            self.wss_list.append(MjWssSercice(
                self.mj_config.mj_config, self.redis_client, self.mj_data_service, self.notify_service, mj_account))

    def start_all(self):
        for wss in self.wss_list:
            wss.start()