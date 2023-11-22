import os
import time

from conf import conf as cf
from utils import utils as ut
from upload_video_to_ks import UpLoadVideoToKs


class UploadAllVideos:
    """
    检测output目录，上传到支持的各个平台，上传之后将其移动到被封目录
    """
    def __init__(self, json_file='../conf/uploads.json'):
        self.json_file = json_file
        self.output_bak_path = ut.create_path_dir(cf.OUTPUT_BAK_PATH)

    def get_json_published(self, channel_url, video_id):
        """
        获取uploads.json中的published内容，如果平台信息已存在则后续不用再上传
        """
        uploads_json = ut.read_json(self.json_file)
        channel_list = uploads_json.get("uploads")
        published = []
        for c in channel_list:
            if c.get('channel_url') == channel_url:
                videos = c.get('videos')
                for v in videos:
                    if v.get('id') == video_id:
                        published = v.get('published')
        return published

    def update_json_published(self, channel_url, video_id, platform):
        """
        在平台上发布成功后，更新uploads.json中的published内容
        """
        uploads_json = ut.read_json(self.json_file)
        channel_list = uploads_json.get("uploads")
        for c in channel_list:
            if c.get('channel_url') == channel_url:
                videos = c.get('videos')
                for v in videos:
                    if v.get('id') == video_id:
                        v['published'].insert(0, platform)
        ut.write_json(self.json_file, uploads_json)

    def upload_to_ks(self, video_file, fm_file, title, label, channel_url, video_id, platform):
        """
        上传到快手平台, 如果已存在对应的标识，则无需再次上传
        """
        print("--开始上传至快手平台...")
        url_path = cf.PLATFORM_KS
        label = ' '.join(["#" + i.replace("#", '') for i in label.split(" ")])
        uks = UpLoadVideoToKs(video_file, fm_file, title, label)
        res = uks.run(url_path)
        # 更新uploads.json中的published内容
        if res:
            self.update_json_published(channel_url, video_id, platform)

    def upload_to_dy(self, video_file, fm_file, title, label, channel_url, video_id, platform):
        """
        上传到抖音平台
        """
        print("--开始上传至抖音平台...")
        pass

    def upload_to_xhs(self, video_file, fm_file, title, label, channel_url, video_id, platform):
        """
        上传到小红书平台
        """
        print("--开始上传至小红书平台...")
        pass

    def move(self, video_file, fm_file, json_file):
        """
        上传成功后将文件移动到output的备份目录
        """
        ut.move(video_file, os.path.join(self.output_bak_path, os.path.basename(video_file)))
        ut.move(fm_file, os.path.join(self.output_bak_path, os.path.basename(fm_file)))
        ut.move(json_file, os.path.join(self.output_bak_path, os.path.basename(json_file)))

    def upload(self, wait_publish_list, video_file, fm_file, translate_title, channel_category, channel_url, video_id):
        """
        根据等待上传的平台列表上传视频到对应平台上
        :param wait_publish_list:待上传列表
        :param video_file:视频
        :param fm_file:封面
        :param translate_title:标题
        :param channel_category:当做标签
        :param channel_url:频道url
        :param video_id:视频的唯一id
        """
        flag = False
        try:
            for platform in wait_publish_list:
                if platform == 'KS':
                    self.upload_to_ks(video_file, fm_file, translate_title, channel_category, channel_url, video_id, platform)
                if platform == 'DY':
                    self.upload_to_dy(video_file, fm_file, translate_title, channel_category, channel_url, video_id, platform)
                if platform == 'XHS':
                    self.upload_to_xhs(video_file, fm_file, translate_title, channel_category, channel_url, video_id, platform)
                time.sleep(cf.WAIT_TIME_UPLOAD_COVER)
            flag = True
        except Exception:
            print("上传至{}失败！".format(wait_publish_list))
        return flag

    @staticmethod
    def get_file_info(json_file):
        json_file_content = ut.read_json(json_file)
        title = json_file_content['title']
        channel_name = json_file_content['channel_name']
        channel_language = json_file_content['channel_language']
        channel_category = json_file_content['channel_category']
        translate_title = ut.translate_to_chinese(title, channel_name, channel_language)
        channel_url = json_file_content['channel_url']
        video_id = json_file_content['video_id']
        return channel_category, translate_title, channel_url, video_id

    def run(self):
        # 获取本次需要上传的文件列表前缀
        file_list = ut.get_distinct_files(cf.OUTPUT_PATH)
        # 循环上传每一个视频
        print("本次待上传的文件列表为：{}".format(file_list))
        for file in file_list:
            print("准备上传{}对应的文件...".format(file))
            video_file = os.path.join(cf.OUTPUT_PATH, file + '_output.mp4')
            fm_file = os.path.join(cf.OUTPUT_PATH, file + '_cover_with_title.jpeg')
            json_file = os.path.join(cf.OUTPUT_PATH, file + '.json')
            print("视频文件为:{}".format(video_file))
            print("封面文件为:{}".format(fm_file))
            print("信息文件为:{}".format(json_file))
            channel_category, translate_title, channel_url, video_id = self.get_file_info(json_file)
            # 获取已经上传的列表
            published = self.get_json_published(channel_url, video_id)
            wait_publish_list = [i for i in cf.SUPPORT_PLATFORM if i not in published]
            print("本视频支持上传的平台为:{}".format(cf.SUPPORT_PLATFORM))
            print("本视频暂未上传的平台为:{}".format(wait_publish_list))
            if not wait_publish_list:
                # 将成功处理后的原始文件移动到备份目录
                self.move(video_file, fm_file, json_file)
                print("当前视频在所有支持的平台上都已上传，相关文件已移动到备份目录，开始处理下一个视频！当前支持的所有平台:{}".format(','.join(cf.SUPPORT_PLATFORM)))
                continue
            # 在剩余待上传的平台上挨个上传
            res = self.upload(wait_publish_list, video_file, fm_file, translate_title, channel_category, channel_url, video_id)
            if res:
                self.move(video_file, fm_file, json_file)
                print(
                    "当前视频在所有支持的平台上都已上传，相关文件已移动到备份目录，开始处理下一个视频！当前支持的所有平台:{}".format(','.join(cf.SUPPORT_PLATFORM)))


if __name__ == '__main__':
    m = UploadAllVideos()
    m.run()