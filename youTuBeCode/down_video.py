import pytube
import os
from pytube import Channel
from pytube.exceptions import VideoUnavailable

from utils import utils as ut
from conf import conf as cf


class DownLoadYouTuBeVideo:
    """
    下载YouToBe上的视频和音频文件
    官方开发参考文档：https://pytube.io/_/downloads/en/latest/pdf/
    """

    def __init__(self, video_url):
        """
        :param video_url: youTuBe视频地址
        :param download_dir: 下载视频的根目录
        """
        self.video_url = video_url
        # 在下载的根目录中创建当前日期的文件夹作为当天下载视频的存放目录
        self.download_path = ut.create_path_dir(os.path.join(cf.DOWNLOAD_PATH, ut.get_str_date()))
        # 使用当前时间戳作为文件名
        timestamp_str = ut.get_str_timestamp()
        # 视频文件绝对路径
        self.webm_file = os.path.join(self.download_path, timestamp_str + '.webm')
        # 音频文件绝对路径
        self.mp4_file = os.path.join(self.download_path, timestamp_str + '.mp4')
        self.title = ''
        self.author = ''
        self.done_flag = 0

    def download_complete_handler(self, title, author):
        """
        回调函数，在视频下载完后将done_flag改为True
        """
        self.done_flag += 1

    def download_highest_resolution(self):
        """
        下载1080以下的最高分辨率视频
        搬运视频当然最好是用比较高的分辨率，一般不建议使用大于1440p，因为过高的分辨率可能会在后面上传自媒体平台时被平台压缩，导致画质更差。
        因此用1080p一般就足够了，所以让我们用一个for循环找出res不大于1080p的画质最高的那个stream
        """
        current_res = 0
        try:
            video = pytube.YouTube(self.video_url, on_complete_callback=self.download_complete_handler)
            self.title = video.title
            self.author = video.author
            print("title:", self.title)
            print("author:", self.author)
            stream_highest_res = video.streams[0]
            for every_stream in video.streams.filter(type="video"):
                if int(every_stream.resolution[:-1]) > 1080:
                    continue
                if int(every_stream.resolution[:-1]) > current_res:
                    current_res = int(every_stream.resolution[:-1])
                    stream_highest_res = every_stream
            print("current resolution:", current_res)
            # 下载视频文件
            print("---开始下载视频文件...")
            stream_highest_res.download(filename=self.webm_file)
            print("---开始下载音频文件...")
            # 下载音频文件
            stream_audio = video.streams.filter(type="audio", abr="128kbps")[0]
            stream_audio.download(filename=self.mp4_file)
        except Exception:
            print("当前视频无法下载，已跳过！视频地址：{}".format(self.video_url))


if __name__ == '__main__':
    # 将频道下的历史数据进行下载
    channel_url = "https://www.youtube.com/channel/UCuOjFdUTw4wyWqMkUOHREzA"
    channel = Channel(channel_url)
    video_urls = channel.video_urls
    video_urls = video_urls[:24]
    print(video_urls)
    video_urls.reverse()
    print(video_urls)
    for video_url in video_urls:
        y = DownLoadYouTuBeVideo(video_url)
        # 下载视频文件和音频文件
        y.download_highest_resolution()
        res = y.done_flag
        if res == 2:
            print("下载视频文件和音频文件成功！")
            print("视频文件为：{}".format(y.webm_file))
            print("音频文件为：{}".format(y.mp4_file))
            title = y.title
            author = y.author
            video_json_file = y.webm_file.replace(".webm", ".json")
            channel_name = "国外音乐"
            channel_category = "音乐"
            channel_language = 'en'
            new_video_id = video_url[-11:]
            new_video_url = video_url
            ut.write_video_info_to_json(title, author, video_json_file,
                                        channel_url, channel_name, channel_category, channel_language,
                                        new_video_id, new_video_url)
            print("json文件为：{}".format(y.mp4_file))
