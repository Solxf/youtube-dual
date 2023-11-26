import json
import os
import sys
import shutil
import time
import datetime
import subprocess
import cv2

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from selenium import webdriver
from translate import Translator
from conf import conf as cf


# 根据不同的系统调用subprocess命令
def execute_command(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    """
    如果subprocess.run()中不传递或者传递stdout和stderr为None，则效果类似于os.system()函数，会将执行命令的info信息输出到控制台
    如果subprocess.run()中传递stdout和stderr为subprocess.PIPE，则不会在控制台输出命令执行的中间信息
    :param stdout: 默认为subprocess.PIPE，即不输出中间信息
    :param stderr: 默认为subprocess.PIPE，即不输出错误信息
    :param cmd: 命令字符串或者命令列表，命令列表是完整命令按空格拆分后的列表，例如['ls', '-l']
    :return:返回命令执行结果，如果是0则表示执行成功，其他为失败
    linux系统下的capture_output=True等效于将stdout和stderr都设置为subprocess.PIPE
    """
    if type(cmd) is list:
        if sys.platform == 'win32':
            res = subprocess.run(["cmd", "/c"] + cmd, stdout=stdout, stderr=stderr)
            return_code = res.returncode
        else:
            res = subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')
            return_code = res.returncode
    else:
        try:
            res = subprocess.run(cmd, stdout=stdout, stderr=stderr, shell=True)
            return_code = res.returncode
        except Exception:
            res = os.system(cmd)
            return_code = res
    return return_code


# 定义chrome浏览器的driver
def get_chrom_driver():
    driver_path = cf.CHROME_DRIVER_PATH
    # 指定用户信息路径，避免每次都要进行登录
    user_data_path = r'C:\Users\13126\AppData\Local\Google\Chrome\User Data\Default'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('-ignore -ssl-errors')
    chrome_options.add_argument("user-data-dir={}".format(user_data_path))
    chrome_options.add_argument('profile-directory=Profile 1')
    # 隐藏浏览器提示被程序控制
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # window.navigator.webdriver设置为False,否则会被拦截
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.binary_location = driver_path
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    # 人为操作该参数默认为undefined,不添加会被拦截,导致验证失败
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
    })
    return driver


# 获取视频分辨率（宽，高）
def get_video_resolution(file_path):
    video = cv2.VideoCapture(file_path)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return width, height


# 获取当前时间戳的字符串
def get_str_timestamp():
    return str(time.time()*1000).split('.')[0]


# 获取当前时间(%Y%m%d)
def get_str_date():
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d")


# 创建目录
def create_path_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


# 移动文件
def move(source_file_path, tag_file_path):
    shutil.move(source_file_path, tag_file_path)


# 读取json文件
def read_json(json_file):
    with open(json_file, "r", encoding='utf-8') as jf:
        uploads = jf.read()
    return json.loads(uploads)


# 写入json文件
def write_json(json_file, content):
    with open(json_file, "w", encoding='utf-8') as jf:
        uploads = json.dumps(content)
        jf.write(uploads)


# 中文检测
def check_chinese(text):
    for ch in text:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


# 给封面添加文字
def cover_add_text(cover_file, output_cover_file, title, font_path, font_size):
    # 读取封面
    img = cv2.imread(cover_file)
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size)
    text_border(draw, title, 100, 600, font, (0, 0, 0), (0, 255, 255))
    retext = np.array(img_pil)
    cv2.imwrite(output_cover_file, retext)


# 添加文字的位置
def text_border(draw, text, x, y, font, shadow_color, fillcolor):
    draw.text((x - 2, y), text, font=font, fill=shadow_color)
    draw.text((x + 2, y), text, font=font, fill=shadow_color)
    draw.text((x, y - 2), text, font=font, fill=shadow_color)
    draw.text((x, y + 2), text, font=font, fill=shadow_color)
    draw.text((x - 2, y - 2), text, font=font, fill=shadow_color)
    draw.text((x + 2, y - 2), text, font=font, fill=shadow_color)
    draw.text((x - 2, y + 2), text, font=font, fill=shadow_color)
    draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fillcolor)


# 将title翻译为中文
def translate_to_chinese(text, channel_name, from_lang, to_lang="zh"):
    try:
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        res = translator.translate(text)
    except Exception as e:
        print("翻译出错，放弃使用title,改为使用频道名称:{}！".format(channel_name))
        print("注：如果想修改分类名称，请修改uploads.json文件中对应频道的category属性！")
        res = channel_name
    return res


# 获取output目录下的所有不重名的文件,要确保准备上传的封面和视频文件以及保存视频信息的json文件都在
def get_distinct_files(dir_path):
    lst1 = os.listdir(dir_path)
    lst2 = [i.split("_")[0] for i in lst1]
    lst3 = sorted(set(lst2))
    lst4 = [i for i in lst3
            if (i + '_cover_with_title.jpeg') in lst1 and (i + '_output.mp4') in lst1 and (i + '.json') in lst1]
    return lst4


# 将下载文件的信息写入到与下载的视频同名的json文件中供后面上传文件时使用
def write_video_info_to_json(title, author, video_json_file,
                             channel_url, channel_name, channel_category, channel_language,
                             video_id, video_url):
    """
    将下载视频的相关信息写入json文件供后面使用
    """
    info = {
        "title": title,
        "author": author,
        "channel_url": channel_url,
        "channel_name": channel_name,
        "channel_category": channel_category,
        "channel_language": channel_language,
        "video_id": video_id,
        "video_url": video_url
    }
    write_json(video_json_file, info)


# 遍历下载目录，获取所有文件
def get_download_files(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    return all_files


# 遍历所有文件，获取同时具有.mp4和.webm以及.json的文件
def get_valid_files(file_list):
    lst1 = [os.path.basename(i) for i in file_list]
    lst2 = sorted(set([i.split(".")[0] for i in lst1]))
    lst3 = [i for i in lst2 if (str(i) + '.webm') in lst1 and (str(i) + '.mp4') in lst1 and (str(i) + '.json') in lst1]
    lst4 = []
    for i in file_list:
        for j in lst3:
            if j in i:
                lst4.append(i)
    return lst4


# def get_file_info(file_name):
#     """
#
#     :param file_name: 不带后缀的文件名，例如1699779970007
#     :return: 返回视频的绝对路径， title的
#     """
#
#     video_file = os.path.join(cf.OUTPUT_PATH, file_name + '_output.mp4')
#     fm_file = os.path.join(cf.OUTPUT_PATH, file_name + '_cover_with_title.jpeg')
#     json_file = os.path.join(cf.OUTPUT_PATH, file_name + '.json')
#     print(video_file, fm_file, json_file)


if __name__ == '__main__':
    f = r'E:\pycharm\python_workspace\youTuBeCraw\conf\uploads_bak.json'