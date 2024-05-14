import json

class TemplateController:
    def __init__(self) -> None:
        blend_file = "./resources/api_params/blend.json"
        self.blend_template = json.load(open(blend_file, "r", encoding="utf-8"))
        describe_file = "./resources/api_params/describe.json"
        self.describe_template = json.load(open(describe_file, "r", encoding="utf-8"))
        variation_file = "./resources/api_params/variation.json"
        self.variation_template = json.load(open(variation_file, "r", encoding="utf-8"))
        upscale_file = "./resources/api_params/upscale.json"
        self.upscale_template = json.load(open(upscale_file, "r", encoding="utf-8"))
        self.imagine_template = json.load(open("./resources/api_params/imagine.json", "r", encoding="utf-8"))
        self.shorten_template = json.load(open("./resources/api_params/shorten.json", "r", encoding="utf-8"))
        self.message_template = json.load(open("./resources/api_params/message.json", "r", encoding="utf-8"))
        

    # 将tempalte中的${key}$替换为template_map中的值
    def replace_template(self, template, template_map):
        for key, value in template_map.items():
            if "$"+key+"$" not in template:
                continue
            template = template.replace("$"+key+"$", value)
        return template
            
    def get_imagine(self, template_map):
        imagine_template_dumps=json.dumps(self.imagine_template)
        imagine_template_dumps = self.replace_template(imagine_template_dumps, template_map)
        return json.loads(imagine_template_dumps)
    
    def get_blend(self, template_map):
        blend_template_dumps=json.dumps(self.blend_template)
        blend_template_dumps = self.replace_template(blend_template_dumps, template_map)
        return json.loads(blend_template_dumps)
    
    def get_describe(self, template_map):
        describe_template_dumps=json.dumps(self.describe_template)
        describe_template_dumps = self.replace_template(describe_template_dumps, template_map)
        return json.loads(describe_template_dumps)
    
    def get_variation(self, template_map):
        variation_template_dumps=json.dumps(self.variation_template)
        variation_template_dumps = self.replace_template(variation_template_dumps, template_map)
        return json.loads(variation_template_dumps)
    
    def get_upscale(self, template_map):
        upscale_template_dumps=json.dumps(self.upscale_template)
        upscale_template_dumps = self.replace_template(upscale_template_dumps, template_map)
        return json.loads(upscale_template_dumps)
    
    def get_shorten(self, template_map):
        shorten_template_dumps=json.dumps(self.shorten_template)
        shorten_template_dumps = self.replace_template(shorten_template_dumps, template_map)
        return json.loads(shorten_template_dumps)
    
    
    def get_message(self, template_map):
        message_template_dumps = json.dumps(self.message_template)
        message_template_dumps = self.replace_template(message_template_dumps, template_map)
        return json.loads(message_template_dumps)