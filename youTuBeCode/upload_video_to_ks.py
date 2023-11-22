import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.utils import get_chrom_driver
from conf import conf as cf

import time


class UpLoadVideoToKs:
    def __init__(self, video_file, fm_file, title, label):
        """
        :param video_file: 要上传的视频文件的绝对路径
        :param fm_file:要上传的视频文件的封面绝对路径
        :param title:视频名称
        :param label:视频分类标签
        """
        self.video_file = video_file
        self.fm_file = fm_file
        self.title = title
        self.label = label
        self.driver = get_chrom_driver()

    def driver_open(self, url):
        """
        使用浏览器驱动打开要上传的平台页面
        """
        self.driver.get(url)

    def driver_close(self):
        """
        关闭浏览器页面
        """
        self.driver.close()

    def upload_video(self, url):
        """
        上传视频
        :param url:平台上传视频的地址
        :param wait_time:上传视频时的等待时间，超出该时间会认为上传失败，则退出上传。默认为2分钟
        :return:
        """
        flag = True
        self.driver_open(url)
        # 上传视频(使用WebDriverWait，等待页面元素出现后获取元素)
        WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='SOCr7n1uoqI-']")))
        # 不需要点击，只需要将视频文件发送到input中
        search = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        search.send_keys(self.video_file)
        while True:
            count = 1
            if count > cf.WAIT_TIME_UPLOAD_VIDEO:
                print("视频上传超时，超时参数为conf中的WAIT_TIME_UPLOAD_VIDEO，默认超时时间为:{}秒".format(cf.WAIT_TIME_UPLOAD_VIDEO))
                flag = False
                break
            try:
                res = self.driver.find_element(By.CSS_SELECTOR, "span[class='DqNkLCyIyfQ-']").get_attribute("innerHTML")
                if res == '上传成功':
                    break
            except Exception as e:
                count += 3
                time.sleep(3)
        return flag

    def upload_fm(self):
        """
        上传封面
        :param wait_time:上传封面后的等待时间，默认为10秒
        :return:
        """
        # 上传封面
        WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='ant-btn ant-btn-primary']"))).click()
        WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[id='rc-tabs-1-tab-2']"))).click()
        search_list = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        search_list[1].send_keys(self.fm_file)
        WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='ant-btn ant-btn-primary Ofv3tgQIWeE-']"))).click()
        # 为了保证封面尽可能上传，在此处等待一段时间
        time.sleep(cf.WAIT_TIME_UPLOAD_COVER)

    def write_content(self, label=''):
        """
        编写视频说明
        :param label:使用"#美食 #国外美食达人"的方式为视频添加分类标签
        """
        title_input = WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='clGhv3UpdEo-']")))
        title_input.send_keys(self.title)
        title_input.send_keys(label)

    def upload(self):
        """
        点击上传按钮进行上传
        :param wait_time: 默认点击后等待10秒
        """
        WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='ant-btn ant-btn-primary GncXo-rrppc-']"))).click()
        time.sleep(cf.WAIT_TIME_UPLOAD_COVER)

    def run(self, url):
        flag = False
        try:
            # 上传视频
            print("开始上传视频！")
            res = self.upload_video(url)
            if res:
                # 上传封面
                print("开始上传封面！")
                self.upload_fm()
                # 编写说明
                print("开始上传视频分类标签！")
                self.write_content(self.label)
                # 点击上传
                self.upload()
                # 关闭浏览器
                self.driver_close()
                print("上传成功！")
                flag = True
            else:
                raise Exception("视频文件上传失败，后面步骤结束！")
        except Exception as e:
            self.driver_close()
            print("Error:{}".format(e))
            print("上传失败，视频路径为:{}".format(self.video_file))
        return flag


if __name__ == '__main__':
    url_path = cf.PLATFORM_KS
    video = r'D:\youtube_output\1699756266279_output.mp4'
    fm = r'D:\youtube_output\1699756266279_cover_with_title.jpeg'
    title_name = '美食一份'
    label_content = "#美食 #国外美食"
    driver_p = r'E:\pycharm\python_workspace\youTuBeCraw\conf\chromedriver.exe'
    uv_ks = UpLoadVideoToKs(video, fm, title_name, label_content)

    uv_ks.run(url_path)



