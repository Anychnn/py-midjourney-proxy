import threading
import websocket
import json
import ssl
import time
import asyncio
from utils.logger_util import get_logger
import logging
from typing import List
from wss.handler.base_message_handler import MessageHandler
from wss.handler.upscale_handler import UpscaleHandler
from wss.handler.imagine_hanlder import ImagineHandler
from wss.handler.upscale_handler import UpscaleHandler
from wss.handler.describe_success_handler import DescribeSuccessHandler
from wss.handler.variation_handler import VariationHandler
import redis
from service.mj_data_service import MjDataService
from service.notify_service import NotifyService
from support.mj_account import MjAccount

logger = get_logger(__name__)


class MjWssSercice:
    def __init__(self, config, redis_client: redis.Redis, mj_data_service: MjDataService, notify_service: NotifyService, account: MjAccount):
        self.config = config
        self.account = account
        self.sequence = 1
        self.redis_client = redis_client
        self.mj_data_service = mj_data_service
        self.notify_service = notify_service
        # Discord WebSocket 地址
        self.ws_url = config['ng']['discord_ws']
        self.bot_token = account.get_bot_token()
        self.ws = None

        self.message_handlers: List[MessageHandler] = []
        self.init_handlers()

    def init_handlers(self):
        self.message_handlers.append(UpscaleHandler(
            self.redis_client, self.mj_data_service, self.notify_service))
        self.message_handlers.append(ImagineHandler(
            self.redis_client, self.mj_data_service, self.notify_service))
        self.message_handlers.append(UpscaleHandler(
            self.redis_client, self.mj_data_service, self.notify_service))
        self.message_handlers.append(VariationHandler(
            self.redis_client, self.mj_data_service, self.notify_service))
        self.message_handlers.append(DescribeSuccessHandler(
            self.redis_client, self.mj_data_service, self.notify_service))

    # 登录
    def on_open(self, ws):
        logger.info("### opened ###")
        self.ws.send(json.dumps({
            'op': 2,
            'd': {
                'token': self.bot_token,
                'intents': 513,
                'properties': {
                    '$os': 'linux',
                    '$browser': 'my_library_name',
                    '$device': 'my_library_name'
                }
            }
        }))

    # 监听消息
    def on_message(self, ws, message):
        # print(message)
        data = json.loads(message)
        # print(data)
        if data['t'] not in ['MESSAGE_CREATE', 'MESSAGE_UPDATE', 'MESSAGE_DELETE']:
            return
        if self.ignoreMessage(data):
            return

        # ACK
        if 'op' in data and data['op'] == 11:
            return
        else:
            if 'op' in data and data['op'] == 10:
                # 心跳包
                logger.info("receive heart from message")
                heartbeat_interval = data['d']['heartbeat_interval']
                self.ws.send(json.dumps({'op': 1, 'd': self.sequence}))
                self.sequence += 1
            elif 'op' in data and data['op'] == 0:
                pass
                # event_type = data['t']
                # if event_type == 'MESSAGE_CREATE':
                #     message_content = data['d']['content']
                #     message_author = data['d']['author']['username']
                #     logger.info(f'{message_author}: {message_content}')

        if 'op' in data and data['op'] == 0:
            for handler in self.message_handlers:
                if "mj_proxy_handled" in data['d'] and data['d']['mj_proxy_handled']:
                    break
                handler.handle(data)

    def ignoreMessage(self, data: dict):
        channel_id = data.get('d').get('channel_id')
        if not channel_id:
            return True
        if channel_id != self.account.get_channel_id():
            return True
        op = data.get('op')
        if op in [0, 10]:
            self.remove_extra_info(data)
            logger.info(json.dumps(data))
            return False

    # 在打印的时候去除掉多余的信息
    def remove_extra_info(self, data: dict):
        if 'd' in data:
            if "author" in data['d']:
                del data['d']['author']
            if "mentions" in data['d']:
                del data['d']['mentions']
            if "member" in data['d']:
                del data['d']['member']
            if "interaction_metadata" in data['d']:
                del data['d']['interaction_metadata']
            if "interaction" in data['d']:
                del data['d']['interaction']
            if "referenced_message" in data['d']:
                del data['d']['referenced_message']

    def on_error(self, ws, error):
        logger.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        logger.info("### closed ###")

    def run_heart(self):
        while True:
            heartbeat = {"op": 1, "d": self.sequence}
            # logger.info("send heart")
            time.sleep(30)
            self.ws.send(json.dumps(heartbeat))
            self.sequence += 1

    def websocket_start_inner(self):

        self.ws = websocket.WebSocketApp(
            self.ws_url, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        # 断线重连
        while True:
            try:
                self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            except Exception as e:
                logger.error(e)
                time.sleep(5)
                continue

    def start(self):
        # websocket.enableTrace(True)
        thread_hi = threading.Thread(target=self.run_heart)
        thread_hi.start()

        thread_websocket = threading.Thread(target=self.websocket_start_inner)
        thread_websocket.start()


if __name__ == "__main__":
    pass
