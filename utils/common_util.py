# -*- ecoding: utf-8 -*-
import numpy as np
from typing import List
import os
import shutil
# import pickle
import json
import string
from PIL import Image
import math
import requests
import base64
from urllib.parse import urlparse
from io import BytesIO
import time
import dill as pickle


def data_generator(data, batch_size):
    assert batch_size > 0
    current_pos = 0
    index = 0
    total = len(data) // batch_size + 1
    while current_pos < len(data):
        yield index, total, data[current_pos: current_pos + batch_size]
        current_pos += batch_size
        index += 1


def write2file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def write2file_arr(filename, arr):
    init = True
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.system(f"mkdir -p {dirname}")
    with open(filename, "w", encoding="utf-8") as f:
        for a in arr:
            if not init:
                f.write("\n")
                f.write(a)
            else:
                f.write(a)
                init = False


def readfile2arr(filename, skip=None):
    with open(filename, "r", encoding="utf-8") as f:
        if skip == None:
            arr = [a.strip() for a in f]
        else:
            arr = [a.strip() for a in f][skip:]
    return arr


# 字符串最小编辑距离
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0 for i in range(n + 1)] for j in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i]
                               [j - 1] + 1, dp[i - 1][j - 1] + 1)

    return dp[m][n]


def get_words2ids_pad(texts, words2id, max_seq):
    lines = []
    for line in texts:
        lines.append(line.strip())

    pad_ids = []
    for line in lines:
        ids = [words2id[i] for i in line]
        ids = ids[0:max_seq]
        if len(ids) < max_seq:
            ids = ids + [0] * (max_seq - len(ids))
        pad_ids.append(ids)
    return np.array(pad_ids)


def remove_dir_and_files(root_dir):
    # 删除目录及文件
    shutil.rmtree(root_dir, True)


def remove_subdirs_and_files(root_dir):
    for filename in os.listdir(root_dir):
        file_path = os.path.join(root_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def copy_files(file_list, ori_dir, des_dir):
    for file_name in file_list:
        file_dir = os.path.join(ori_dir, file_name)
        shutil.copy(file_dir, des_dir)


def save_pickle(filename, obj):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(filename):
    if filename.endswith(".json"):
        return read_json(filename)
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj


def arr2str_tab(arr):
    result = []
    for i in arr:
        if isinstance(i, int):
            result.append(str(i))
        elif isinstance(i, float):
            result.append("%.3f" % i)
        elif isinstance(i, str):
            result.append(i)
    # arr = [str(i) if isinstance(i, int) elif  "%.3f" % i for i in arr]
    return "\t".join(result)


def to_torch(data, type=None, device="cpu"):
    import torch

    if type == None:
        return torch.from_numpy(np.array(data)).to(device)
    else:
        return torch.from_numpy(np.array(data, dtype=type)).to(device)


def read_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def cached_pkl(cache_path: str, load_from_cache: bool, gen_func, *args, **kargs):
    if os.path.exists(cache_path) and load_from_cache:
        print("gen from cached pkl")
        return load_pickle(cache_path)
    else:
        print("gen from origin file")
        out = gen_func(*args, **kargs)
        save_pickle(cache_path, out)
        return out


def alignment(arr: List, max_length: int, padding):
    arr_len = len(arr)
    mask = [1.0] * len(arr)
    if len(arr) >= max_length:
        arr = arr[0:max_length]
        mask = mask[0:max_length]
    else:
        arr += [padding] * (max_length - arr_len)
        mask += [0.0] * (max_length - arr_len)
    return arr, mask


def collate_fn_from_map(data, keys=None, device="cpu", ignore_keys=[]):
    assert data
    assert isinstance(data, list)
    result = {}
    import torch

    ignore_keys = set(ignore_keys)
    if isinstance(data[0], dict):
        for i in data:
            for k, v in i.items():
                if k not in ignore_keys:
                    if k not in result:
                        result[k] = []
                    result[k].append(v)
        if keys:
            for k, v in result.items():
                if k in keys:
                    result[k] = to_torch(v, type=keys[k], device=device)

    return result


def save_json_datas(file: str, datas):
    # if not os.path.exists("../evaluate/python_result/"+testset_name+"/"):
    # os.mkdir("../evaluate/python_result/"+testset_name+"/")
    # paths=file.split("/")
    # tmp_path=paths[0]+"/"
    beg_index = 0
    while True:
        try:
            index = file.index("/", beg_index)
        except Exception as e:
            break

        recur_dir_path = file[: index + 1]
        if not os.path.exists(recur_dir_path):
            os.mkdir(recur_dir_path)
        beg_index = index + 1

    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(datas, indent=4, ensure_ascii=False))


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= "\u4e00" and uchar <= "\u9fa5":
        return True
    else:
        return False


def save_huggface_json_datas(file, datas):
    line_datas = []
    for i in datas:
        line_datas.append(json.dumps(i, ensure_ascii=False))
    write2file_arr(file, line_datas)


def read_huggingface_json_datas(file):
    line_datas = []
    datas = readfile2arr(file)
    for i in datas:
        r = json.loads(i)
        line_datas.append(r)
    return line_datas


def get_punctuations():
    punctuations = set(list(string.punctuation + "。！？”’“‘…·《》【】—-,、，"))
    return punctuations


def random_select_unrepeat(items, size):
    # 不重复
    selected = np.random.choice(items, replace=False, size=size)
    return selected


# 将文档拆分成句子，根据max_len合并
def cut_to_sents(text, max_len=120, merge=False):
    import re

    sentences = re.split(r"(？|\?|。|！|\…\…|\r|\n)", text)

    clip_sents = []
    for i in sentences:
        left = i
        while len(left) > 0:
            clip_sents.append(left[:max_len])
            left = left[max_len:]
    return clip_sents

    for i in range(len(sentences)):
        if i % 2 == 1:
            _sentences.append(sentences[i - 1] + sentences[i])
        elif i == len(sentences) - 1:
            # 最后一个
            _sentences.append(sentences[i])

    clip_sents = []
    for i in _sentences:
        left = i
        while len(left) > 0:
            clip_sents.append(left[:max_len])
            left = left[max_len:]
    #  不拼接
    if not merge:
        return clip_sents

    l = ""
    merged_sents = []
    for index, i in enumerate(clip_sents):
        if len(l) + len(i) > max_len:
            merged_sents.append(l)
            l = ""
            l += i
        else:
            l += i

    if len(l) > 0:
        merged_sents.append(l)
    return merged_sents


def getImage(filename, bs64=False):
    if filename == None:
        return None

    if isinstance(filename, Image.Image):
        im = filename
    elif filename.startswith("data:image"):
        return filename
    elif is_url(filename):
        response = requests.get(filename, timeout=15)
        if response.ok:
            im = Image.open(BytesIO(response.content))
        else:
            print(f"error get img from url:{filename}")
            return None
    elif os.path.isfile(filename):
        im = Image.open(filename)
    elif isinstance(filename, Image.Image):
        im = filename
    else:
        im = base64_to_image(filename)

    if bs64:
        return image_to_base64(im)
    return im


def image_to_base64(image: Image.Image, fmt="png") -> str:
    from io import BytesIO
    import base64

    output_buffer = BytesIO()
    image.save(output_buffer, format=fmt)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    return f"data:image/{fmt};base64," + base64_str


def base64_to_image(image_base64):
    import base64
    from PIL import Image
    from io import BytesIO

    datas = image_base64.split(",")
    if len(datas) == 1:
        image_base64 = datas[0]
    else:
        image_base64 = datas[1]
    # data:image/jpeg;base64,iVBORw0K
    img_bs64 = base64.b64decode(image_base64)
    image = Image.open(BytesIO(img_bs64))
    return image


def url_to_base64(url):
    response = requests.get(url)
    image_data = response.content
    base64_data = base64.b64encode(image_data)
    base64_image = base64_data.decode("utf-8")
    return f"data:image/jpeg;base64,{base64_image}"


def image_to_np(image):
    return np.array(image)


def hash_lora_file(filename):
    import mmap
    import hashlib

    """Hashes a .safetensors file using the new hashing method.
    Only hashes the weights of the model."""
    hash_sha256 = hashlib.sha256()
    blksize = 1024 * 1024

    with open(filename, mode="r", encoding="utf8") as file_obj:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as m:
            header = m.read(8)
            n = int.from_bytes(header, "little")

    with open(filename, mode="rb") as file_obj:
        offset = n + 8
        file_obj.seek(offset)
        for chunk in iter(lambda: file_obj.read(blksize), b""):
            hash_sha256.update(chunk)
    file_hash = hash_sha256.hexdigest()
    legacy_hash = file_hash[:12]
    return file_hash, legacy_hash


def hash_sd_model(filename):
    """old hash that only looks at a small part of the file and is prone to collisions"""

    try:
        with open(filename, "rb") as file:
            import hashlib

            m = hashlib.sha256()

            file.seek(0x100000)
            m.update(file.read(0x10000))
            return m.hexdigest()
    except FileNotFoundError:
        return "NOFILE"


def hash_file(filename):
    """old hash that only looks at a small part of the file and is prone to collisions"""

    try:
        with open(filename, "rb") as file:
            import hashlib

            m = hashlib.sha256()
            m.update(file.read(0x10000))

            return m.hexdigest()[:10]
    except FileNotFoundError:
        return "NOFILE"


def file_walk(root_path, excludes=[]):
    file_list = []
    for dirPath, dirNames, fileNames in os.walk(root_path):
        for fileName in fileNames:
            if not fileName.split(".")[-1] in excludes:
                # if not fileName.lower().endswith('.png') and not fileName.lower().endswith('.jsonl'):
                # if not fileName.lower().endswith('.png') and not fileName.lower().endswith('.jsonl'):
                filePath = os.path.join(dirPath, fileName)
                file_list.append(filePath)
    return file_list


def get_latest_file(root_path):
    file_list = file_walk(root_path)
    latest_file = max(file_list, key=os.path.getctime)
    return latest_file


def webp2png(file_list):
    from PIL import Image, ImageOps

    for srcImagePath in file_list:
        image = Image.open(srcImagePath)
        image = ImageOps.exif_transpose(image)
        dstImagePath = os.path.splitext(srcImagePath)[0] + ".png"
        image.save(dstImagePath)
        print("%s ---> %s" % (srcImagePath, dstImagePath))


def get_file_prefix(fname):
    names = fname.split(".")[:-1]
    return ".".join(names)


def download_file(src, dest):
    # import wget
    # import ssl
    # # 取消ssl全局验证
    # ssl._create_default_https_context = ssl._create_unverified_context
    # wget.download(src, dest)
    import os

    os.system(f"wget -O {dest} {src}")


def img_compress(in_file, out_file, target_size=40):
    from PIL import Image, ImageFile

    def get_size(file):
        # 获取文件大小:KB
        size = os.path.getsize(file)
        return int(size / 1024)

    # 防止图片超过178956970 pixels 而报错
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None
    # 读取img文件
    im = Image.open(in_file)
    if im.mode == "RGBA":
        # print(in_file)
        im = im.convert("RGB")

    o_size = get_size(in_file)
    if o_size > target_size:
        # scale=im.width*im.height
        scale = math.sqrt(target_size / o_size)
        height = int(im.height * scale)
        width = int(im.width * scale)
        im = im.resize((width, height))
    im.save(out_file)


def img_compress_bs64(bs64_in, target_size=1000):
    if target_size == None:
        return bs64_in
    bytes_count = len(bs64_in)
    size = bytes_count / 1024
    # print("img_size", size)
    image = base64_to_image(bs64_in)

    if size > target_size:
        scale = math.sqrt(target_size / size)
        height = int(image.height * scale)
        width = int(image.width * scale)
        image = image.resize((width, height))
    output = image_to_base64(image)
    return output


def is_url(data):
    # 判断字符串是否是IP地址
    def is_ip_address(string):
        parts = string.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit() or int(part) < 0 or int(part) > 255:
                return False
        return True

    if not data:
        return False

    if data.startswith("http://") or data.startswith("https://"):
        return True
    elif is_ip_address(data):
        return True
    else:
        return False

    # return bool(parsed_url.scheme)


def fmt_data(time_obj):
    fmt_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_obj))

    return fmt_time


def get_self_ip():
    import socket
    try:
        # 创建一个UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 连接到公共的 DNS 服务器
        sock.connect(('8.8.8.8', 80))

        # 获取本地套接字的地址信息
        ip_address = sock.getsockname()[0]

        return ip_address
    except socket.error:
        return '无法获取IP地址'


def get_remote_ip():
    import requests
    res = requests.get("https://ipinfo.io/ip")
    return res.text


def get_osr_create_event_loop():
    import asyncio
    # 尝试获取当前线程的事件循环
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # 当前线程没有事件循环时会引发这个异常
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop

# 异地组网


def get_vnc_ip():
    import socket
    import fcntl
    import struct

    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip_address = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            return ip_address
        except IOError:
            return None

    # 获取所有网卡名称
    nic_names = socket.if_nameindex()

    # 遍历每个网卡，并获取对应的IP地址
    for nic in nic_names:
        name = nic[1]
        ip_address = get_ip_address(name)
        if ip_address:
            if name == "oray_vnc":
                return ip_address
    return None


def encode_base64(s):
    # 将字符串转换为字节
    byte_representation = s.encode('utf-8')
    # 使用base64库进行编码
    base64_bytes = base64.b64encode(byte_representation)
    # 将字节转换回字符串
    base64_string = base64_bytes.decode('utf-8')
    return base64_string



    
    
if __name__ == "__main__":
    # articles = readfile2arr("./datas/corpus/raw_articles.csv")
    # print(len(articles))
    # print(collate_fn_from_map(
    #     [{'a': 'texta', 'b': 'textb'}, {'a': 'texta2', 'b': 'textb2'}], keys=[]))
    # data = {"a_f": "a", "b_f": "b"}
    # datas = [data for i in range(10)]
    # # print(json.dumps(data, ensure_ascii=False))
    # # print(json.dumps(data, indent=4, ensure_ascii=False))
    # save_huggface_json_datas("./test.json", datas)

    from PIL import Image, ImageOps

    image = Image.open("/home/ubuntu/projects/imgs/origin/0f3335e556.jpg")
    bs64 = image_to_base64(image)
    out = img_compress_bs64(bs64, target_size=100)
    base64_to_image(out).save("a.png")
    # print(len(out))
