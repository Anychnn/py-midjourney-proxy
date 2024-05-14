
import yaml
class MjConfig:
    def __init__(self) -> None:
        self.mj_config = yaml.load(open(
            "./resources/config/prod_mj_config.yaml", "r", encoding="utf-8"), Loader=yaml.FullLoader)

    
    def get_accounts(self):
        return self.mj_config['accounts']