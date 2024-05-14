from support.mj_config import MjConfig
import redis
import requests
import json
from support.task_controller import MjTask
from service.template_controller import TemplateController
import base64
import io
import hashlib
from support.mj_account import MjAccount

class DiscordHttpService:
    def __init__(self, mj_config: MjConfig, redis_client: redis.Redis, template_controller: TemplateController, mj_account: MjAccount) -> None:
        self.redis_client = redis_client
        self.mj_config = mj_config
        self.mj_account = mj_account
        self.template_controller = template_controller
        
    def get_interaction_url(self):
        host = self.mj_config['ng']['discord_server']
        return f"{host}/api/v9/interactions"
    
    def get_messages_url(self):
        host=self.mj_config['ng']['discord_server']
        CHANNEL_ID = self.mj_account.get_channel_id()
        return f"{host}/api/v9/channels/{CHANNEL_ID}/messages"
    def get_discord_upload_attachment_url(self):
        host=self.mj_config['ng']['discord_server']
        CHANNEL_ID = self.mj_account.get_channel_id()
        upload_attachment_url = f"{host}/api/v9/channels/{CHANNEL_ID}/attachments"
        return upload_attachment_url
    

    
    def imageine(self, task: MjTask):
        url = self.get_interaction_url()

        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()

        advanced_prompt = ""

        if task.image_prompt:
            advanced_prompt = task.image_prompt+" "+task.prompt
        else:
            advanced_prompt = task.prompt

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "prompt": advanced_prompt,
            "nonce": task.nonce
        }

        imagine_template = self.template_controller.get_imagine(template_map)

        boundary = "----WebKitFormBoundaryqznUd46iGT62TY0s"
        fields = {"payload_json": (None, json.dumps(imagine_template))}
        from requests_toolbelt.multipart.encoder import MultipartEncoder
        form_data = MultipartEncoder(fields=fields, boundary=boundary)

        HEADERS = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=form_data, headers=HEADERS)

        if res.status_code not in [200, 204]:
            raise Exception(json.loads(res.text))

        print("res.content", res.content)

    def upscale(self, task: MjTask):
        url = self.get_interaction_url()

        
        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()
        

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "nonce": task.nonce,
            "message_id": task.message_id,
            "custom_id": task.custom_upscale_id
        }

        upscale_template = self.template_controller.get_upscale(template_map)
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=json.dumps(
            upscale_template), headers=HEADERS)
        print(res)

    def variation(self, task: MjTask):
        url = self.get_interaction_url()
        
        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "nonce": task.nonce,
            "message_id": task.message_id,
            "custom_id": task.custom_variation_id
        }

        upscale_template = self.template_controller.get_upscale(template_map)
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=json.dumps(
            upscale_template), headers=HEADERS)
        print(res)

    def describe(self, task: MjTask):
        url = self.get_interaction_url()

        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "nonce": task.nonce,
            "message_id": task.message_id,
            "custom_id": task.custom_variation_id,
            "prompt": task.image_prompt
        }

        upscale_template = self.template_controller.get_describe(template_map)
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=json.dumps(
            upscale_template), headers=HEADERS)
        print(res)

    def blend(self, task: MjTask):
        url = self.get_interaction_url()

        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()

        advanced_prompt = ""

        if not task.blend_imgs:
            raise Exception("blend_imgs is empty")

        advanced_prompt = " ".join(task.blend_imgs)

        if task.dimensions:
            dimentsion_prompt = ""
            if task.dimensions == 'Square':
                dimentsion_prompt = "--ar 1:1"
            elif task.dimensions == 'Landscape':
                dimentsion_prompt = "--ar 3:2"
            elif task.dimensions == 'Portrait':
                dimentsion_prompt = "--ar 2:3"
            else:
                dimentsion_prompt = ""

            advanced_prompt = advanced_prompt + " " + dimentsion_prompt

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "prompt": advanced_prompt,
            "nonce": task.nonce
        }

        imagine_template = self.template_controller.get_imagine(template_map)

        boundary = "----WebKitFormBoundaryqznUd46iGT62TY0s"
        fields = {"payload_json": (None, json.dumps(imagine_template))}
        from requests_toolbelt.multipart.encoder import MultipartEncoder
        form_data = MultipartEncoder(fields=fields, boundary=boundary)

        HEADERS = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=form_data, headers=HEADERS)

        if res.status_code not in [200, 204]:
            raise Exception(json.loads(res.text))

        print("res.content", res.content)

    
    def action(self, task: MjTask):
        url = self.get_interaction_url()

        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "nonce": task.nonce,
            "message_id": task.reference_message_id,
            "custom_id": task.custom_id
        }

        upscale_template = self.template_controller.get_upscale(template_map)
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=json.dumps(
            upscale_template), headers=HEADERS)
        print(res)
        
    def shorten(self, task: MjTask):
        url = self.get_interaction_url()

        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "nonce": task.nonce,
            "prompt": task.prompt
        }

        upscale_template = self.template_controller.get_shorten(template_map)
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=json.dumps(
            upscale_template), headers=HEADERS)
        print(res)

    
    def message(self, final_file_name):
        url = self.get_messages_url()

        app_id = self.mj_account.get_app_id()
        guild_id = self.mj_account.get_gulid_id()
        channel_id = self.mj_account.get_channel_id()
        session_id = self.mj_account.get_session_id()
        user_token = self.mj_account.get_user_token()
        
        file_name = final_file_name.split("/")[-1]

        template_map = {
            "app_id": app_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "session_id": session_id,
            "final_file_name": final_file_name,
            "file_name": file_name
        }
        
        message_template = self.template_controller.get_message(template_map)
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": user_token
        }
        res = requests.post(url=url, data=json.dumps(
            message_template), headers=HEADERS)
        print(res)
        if res.status_code==200:
            upload_resp = json.loads(res.text)
            image_url = upload_resp['attachments'][0]['url']
            return image_url
        else:
            raise Exception("message upload failed")
        
    def upload_img_if_bs64(self, img: str):
        return self.upload2discord(img)

    def upload2discord(self, img: str):
        if not img:
            return
        if img.startswith("data:image/"):

            discord_upload_attachment_url = self.get_discord_upload_attachment_url()
            
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