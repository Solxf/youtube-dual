import json
import os
import time
from pytube import Channel
from utils import utils as ut
from conf import conf as cf
from youTuBeCode.down_video import DownLoadYouTuBeVideo


class CheckChannel:
    """
    通过conf/uploads.json文件监控频道下的shorts视频的更新，如果有更新则在第一时间下载对应频道的最新视频并更新json文件。
    注：1.pytube 模块下的 contrib 包中存放着channel.py的源码，默认安装的版本处理油管视频获取的video_urls为[]，所以该channel.py是进行修改后的。
    注：2.修改后的源码默认只能获取频道下的videos的url，而有时候想获取频道下的shorts的url，故需要再次修改源码。
    注：3.目前默认的channel.py文件是用来获取shorts的url，如果想获取videos的url，则使用目录下的channel_videos.py中的内容替换channel.py。
    注：4.同理，channel_shorts.py的内容就是用来获取shorts的url的代码。
    注：5.如果既想获取videos的内容又想获取shorts的内容，建议使用anaconda安装两个python环境，然后分别使用对应的channel.py文件即可。
    注：6.进入对应的python环境，使用pip -V可找到模块的安装位置
    注：7.不能直接使用油管上的频道url地址作为channel_url,目前只能按照https://www.youtube.com/channel/channelId使用。
    注：8.channelId可以在网页进入对应频道，右键打开网页源代码，搜索 externalId 即可找到。
    """

    def __init__(self, download_dir, json_file='../conf/uploads.json'):
        """
        :param download_dir: 下载视频的根目录
        :param json_file: 用于监控频道的json文件
        """
        self.download_dir = download_dir
        self.json_file = json_file

    def download_video(self, new_video_id, new_video_url, channel, channel_info, uploads_json):
        """
        下载视频并将下载信息更新到json文件中
        """
        dl = DownLoadYouTuBeVideo(new_video_url)
        dl.download_highest_resolution()
        done_flag = dl.done_flag
        title = ''
        author = ''
        webm_file = ''
        if done_flag == 2:
            # 将信息同步到json文件
            video_log = dict(id=new_video_id,
                             url=new_video_url,
                             name=channel.videos[0].title,
                             publish_date=str(channel.videos[0].publish_date),
                             published=[])
            channel_info['videos'].insert(0, video_log)
            ut.write_json(self.json_file, uploads_json)
            print("---下载视频文件和音频文件成功！")
            print("---视频文件为：{}".format(dl.webm_file))
            print("---音频文件为：{}".format(dl.mp4_file))
            print("---下载信息已同步至json文件!")
            title = dl.title
            author = dl.author
            webm_file = dl.webm_file
        else:
            print("---下载视频文件和音频文件失败！")
            print("---最新发布视频对应的url为：{},如有需要请手动查看".format(new_video_url))
        return done_flag, title, author, webm_file

    def check_channel_and_download(self):
        """
        使用json文件监控频道下的更新并下载更新视频
        """
        uploads_json = ut.read_json(self.json_file)
        count = len(uploads_json['uploads'])
        # json文件中配置了多个channel，循环监控每一个channel
        print("本程序共检测{}个频道!".format(count))
        for i, channel_info in enumerate(uploads_json['uploads']):
            channel_url = channel_info['channel_url']
            channel_name = channel_info['channel_name']
            channel_category = channel_info['category']
            channel_language = channel_info['language']
            print("开始检测第{}个频道，频道地址为:{}".format(i + 1, channel_url))
            latest_video_id = channel_info['videos'][0]['id']
            channel = Channel(channel_url)
            if len(channel.video_urls) == 0:
                print("---该频道暂无视频更新，开始检测下一个频道!")
                continue
            new_video_url = channel.video_urls[0]
            # video url的最后11为是该video的唯一标识，也就是video_id
            new_video_id = new_video_url[-11:]
            if new_video_id != latest_video_id:
                print("---该频道有视频更新，更新的视频地址为:{}".format(new_video_url))
                done_flag, title, author, webm_file = self.download_video(new_video_id, new_video_url, channel, channel_info, uploads_json)
                if done_flag == 2:
                    video_json_file = webm_file.replace(".webm", ".json")
                    print("---将下载视频对应的信息写入json文件:{}".format(video_json_file))
                    ut.write_video_info_to_json(title, author, video_json_file,
                                                channel_url, channel_name, channel_category, channel_language,
                                                new_video_id, new_video_url)
            else:
                print("---该频道暂无视频更新，检测下一频道!")
            # 为防止被官网封禁，间隔一段时间再处理下一个频道
            time.sleep(cf.WAIT_TIME_CHANNEL_CHECK)


if __name__ == '__main__':
    down_dir = 'D:\\youtube_download'
    cc = CheckChannel(down_dir)
    cc.check_channel_and_download()


