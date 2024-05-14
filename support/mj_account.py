

class MjAccount:
    def __init__(self, account_config: dict) -> None:
        self.account_config = account_config

    def get_user_token(self):
        return self.account_config['user_token']
    
    def get_bot_token(self):
        return self.account_config['bot_token']
    
    def get_channel_id(self):
        return self.account_config['channel_id']
    
    def get_gulid_id(self):
        return self.account_config['guild_id']
    
    def get_app_id(self):
        return self.account_config['app_id']
    
    def get_session_id(self):
        return self.account_config['session_id']
    