import json
import os
import asyncio
import random
import time
import uuid
import yaml
from .logger_util import get_logger
import consul
import consul.base
import consul.callback
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, start_http_server

class Bootstrap():
    def __init__(self, file_yaml='config.yaml') -> None:
        config_yaml: dict = self.read_config(file_yaml)
        env_dict = os.environ
        # main
        self.RUN_NAME =     config_yaml.get('RUN_NAME')
        self.LOG_PATH =     config_yaml.get('LOG_PATH')
        self.ENV_IP =       config_yaml.get('ENV_IP', env_dict.get('ENV_IP'))
        self.ENV_PORT =     config_yaml.get('ENV_PORT', env_dict.get('ENV_PORT'))
        self.ENV_PORTS =    config_yaml.get('ENV_PORTS', env_dict.get('ENV_PORTS'))
        self.DWONSTREAMS =  config_yaml.get('DWONSTREAMS')

        # consul
        self.CONSUL_IP =            config_yaml.get('CONSUL_IP')
        self.CONSUL_PORT =          config_yaml.get('CONSUL_PORT')
        self.CONSUL_TOKEN =         config_yaml.get('CONSUL_TOKEN')
        self.CONSUL_CHECK_IP =      config_yaml.get('CONSUL_CHECK_IP')
        self.CONSUL_CHECK_TICK =    config_yaml.get('CONSUL_CHECK_TICK', 5)
        self.CONSUL_CHECK_TIMEOUT = config_yaml.get('CONSUL_CHECK_TIMEOUT', 30)
        self.CONSUL_CHECK_DEREG =   config_yaml.get('CONSUL_CHECK_DEREG', 30)

        # metrics
        self.METRICS_IP =           config_yaml.get('METRICS_IP')
        self.METRICS_PORT =         config_yaml.get('METRICS_PORT')
        self.METRICS_TOKEN =        config_yaml.get('METRICS_TOKEN')
        self.METRICS_CHECK_TICK =   config_yaml.get('METRICS_CHECK_TICK', 5)

    def lifespan(self, _):
        print("startup")
        self.background_start()
        yield
        print(f"shutdown wait {self.CONSUL_CHECK_DEREG}s for consul dereg")
        self.deregister_consul()
        # time.sleep(self.CONSUL_CHECK_DEREG)

    def init(self):
        self.logger = get_logger(self.RUN_NAME, self.LOG_PATH)
        self.consul_cli = consul.Consul(self.CONSUL_IP, self.CONSUL_PORT, self.CONSUL_TOKEN)
        self.register_consul()
        self.metrics_registry = CollectorRegistry()
        self.metrics_reg_base()
        self.metrics_reg()
        self.service_dict = {k: [] for k in self.DWONSTREAMS}
        self.background_service_update()
        self.not_shutdown = True

    def background_start(self):
        if self.service_dict:
            asyncio.create_task(self.background_service_update())
        asyncio.create_task(self.background_metrics_update())

    def read_config(self, file_yaml):
        with open(file=file_yaml, mode='r', encoding='utf-8') as f:
            return yaml.load(stream=f.read(), Loader=yaml.FullLoader)

    def register_consul(self):
        # 健康检查ip端口，检查时间：5,超时时间：30，注销时间：30s
        # curl --request PUT http://127.0.0.1:6011/v1/agent/service/register/test_service_down?token=6df8babf-1061-2469-79f0-4488640cba81
        # curl --request PUT http://127.0.0.1:6011/v1/agent/service/deregister/test_service_down?token=6df8babf-1061-2469-79f0-4488640cba81
        # curl --request GET http://127.0.0.1:6011/v1/agent/checks?token=6df8babf-1061-2469-79f0-4488640cba81
        # curl --request GET http://127.0.0.1:6011/v1/agent/check/test_service_up?token=6df8babf-1061-2469-79f0-4488640cba81

        self.consul_id = uuid.uuid4().hex
        checker = consul.Check().tcp(self.CONSUL_CHECK_IP, self.ENV_PORT,
                                        self.CONSUL_CHECK_TICK * 1000 * 1000,
                                        self.CONSUL_CHECK_TIMEOUT * 1000 * 1000,
                                        self.CONSUL_CHECK_DEREG * 1000 * 1000)
        # checker = consul.Check().http(f'http://127.0.0.1:8531/health',
        #                                 1 * 1000 * 1000, 2 * 1000 * 1000, 3 * 1000 * 1000)
        # res = self.consul_cli.catalog.register(
        #     self.RUN_NAME,
        #     self.ENV_IP,
        #     {
        #         "Service": self.RUN_NAME,
        #         "ID": self.consul_id,
        #         "Tags": [],
        #         "Port": self.ENV_PORT,
        #     },
        #     check=checker,
        #     token=self.CONSUL_TOKEN,
        # )
        res = self.consul_cli.agent.service.register(
            self.RUN_NAME,
            service_id=self.consul_id,
            address=self.ENV_IP,
            port=self.ENV_PORT,
            token=self.CONSUL_TOKEN,
            check=checker)
        if not res:
            raise RuntimeError('register_consul fail!')

    def consul_token_param(self):
        params = []
        if self.CONSUL_TOKEN:
            params.append(('token', self.CONSUL_TOKEN))
        return params

    def deregister_consul(self):
        # curl --request PUT http://127.0.0.1:6011/v1/agent/service/deregister/test_service_down
        # curl --request PUT http://101.43.141.18:6011/v1/agent/service/register/test_service_down?token=6df8babf-1061-2469-79f0-4488640cba81
        # curl --request PUT http://101.43.141.18:6011/v1/agent/service/deregister/test_service_down?token=6df8babf-1061-2469-79f0-4488640cba81
        # curl --request GET http://101.43.141.18:6011/v1/agent/services?token=6df8babf-1061-2469-79f0-4488640cba81
        # curl --request GET http://101.43.141.18:6011/v1/agent/service/test_service_down?token=6df8babf-1061-2469-79f0-4488640cba81

        res = self.consul_cli.agent.service.deregister(self.consul_id, token=self.CONSUL_TOKEN)
        # res = self.consul_cli.catalog.deregister()
        # res = self.consul_cli.agent.agent.http.put(consul.callback.CB.bool(), '/v1/agent/service/deregister/%s' % self.RUN_NAME, params=self.consul_token_param())
        if not res:
            self.logger.error('deregister_consul fail!')

    def get_server(self, service_name):
        service_list = self.service_dict[service_name]
        if not service_list:
            return None
        return random.choice(service_list)

    async def background_service_update(self):
        def cb(response):
            consul.callback.CB._status(response)
            if response.code == 404:
                return None
            return json.loads(response.body)
        while self.not_shutdown:
            for service_name in self.service_dict:
                filter = ('filter', f'Service == "{service_name}"')
                service_info = self.consul_cli.agent.agent.http.get(cb, '/v1/agent/services', params=(*self.consul_token_param(), filter))
                if isinstance(service_info, dict):
                    self.service_dict[service_name] = [{'ip': item.get('Address'), 'port': item.get('Port')} for item in service_info.values()]
                    self.metrics_downstream.labels(src=self.RUN_NAME, dst=service_name).set(len(service_info))
                else:
                    self.logger.error('service_dict[%s] parse error! parsed to: %s', service_name, self.service_dict)
                    self.metrics_downstream.labels(src=self.RUN_NAME, dst=service_name).set(-1)
            await asyncio.sleep(self.CONSUL_CHECK_TICK)

    async def background_metrics_update(self):
        while self.not_shutdown:
            push_to_gateway(f'{self.METRICS_IP}:{self.METRICS_PORT}', job=self.RUN_NAME, registry=self.metrics_registry)
            self.logger.info('push_to_gateway')
            await asyncio.sleep(self.METRICS_CHECK_TICK)

    def metrics_reg_base(self):
        self.metrics_downstream = Gauge('service_downstream', 'downstream service num', ['src', 'dst'], registry=self.metrics_registry)

    def metrics_reg(self):
        raise NotImplementedError()

        # c = Counter('my_requests_total', 'HTTP requests total', ['method', 'endpoint'], registry=self.metrics_registry)
        # c.labels(method='get', endpoint='/').inc()
        # c.labels(method='post', endpoint='/submit').inc()
