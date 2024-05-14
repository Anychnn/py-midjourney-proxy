import requests
import redis
import uuid
from support.mj_config import MjConfig
from service.discord_http_service import DiscordHttpService
import json
import io
from PIL import Image
import hashlib
import base64

class ImageController:
    def __init__(self, mj_config: MjConfig, redis_client: redis.Redis, discord_http_service: DiscordHttpService) -> None:
        self.redis_client = redis_client
        self.mj_config = mj_config.mj_config
        self.discord_http_service = discord_http_service
        
        self.discord_upload_server = self.mj_config['ng']['discord_upload_server']
        self.CHANNEL_ID = self.mj_config['account']['channel_id']
        self.USER_TOKEN = self.mj_config['account']['user_token']

    def upload_img_if_bs64(self, img: str):
        # return self.upload2fastapi(img)
        return self.upload2discord(img)

    def upload2discord(self, img: str):
        if not img:
            return
        if img.startswith("data:image/"):

            discord_upload_attachment_url = self.discord_http_service.get_discord_upload_attachment_url()
            
            base64_data = img.split(",")[-1]
            image_data = base64.b64decode(base64_data)
            # 将字节数据转换为BytesIO对象
            image_stream = io.BytesIO(image_data)
            
            # 将image_streamg转为bytes
            image_bytes = image_stream.read()
            file_size = len(image_bytes)
            hash_value = hashlib.md5(image_data).hexdigest()
            file_name=f"{hash_value}.png"
            
            HEADERS = {"Content-Type": "application/json", "Authorization": self.USER_TOKEN}
            payload = {
                "files": [{"filename": file_name, "file_size": file_size, "id": "0"}]}
            res = requests.post(discord_upload_attachment_url, headers=HEADERS, data= json.dumps(payload))
            if res.status_code == 200:
                res_data=json.loads(res.text)
                attach = res_data['attachments'][0]
                upload_url = attach['upload_url']
                upload_filename = attach['upload_filename']
                print("upload_url",upload_url)
                print("upload_filename",upload_filename)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(file_size),
                }
                res = requests.put(upload_url, data=image_data, headers = headers)
                print(res.status_code)
                if res.status_code == 200:
                    image_url= self.discord_http_service.message(upload_filename)
                    return image_url
                else:
                    raise Exception("上传图片失败")
                
            else:
                raise Exception("上传图片失败")
            
            
           
        elif img.startswith("http"):
            return img

    
    def upload2fastapi(self, img: str):
        if not img:
            return
        if img.startswith("data:image/"):
            url = self.mj_config['common']['img_upload_url']
            data = {
                "bs64": img
            }
            res = requests.post(url, data=json.dumps(data))
            res_data = json.loads(res.text)
            filename = res_data["data"]["filename"]
            image_url = f"http://43.153.103.254/images/{filename}"
            return image_url
        elif img.startswith("http"):
            return img