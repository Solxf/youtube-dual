import os
from utils import utils as ut
from utils import ffmpeg_functions as ff
from utils import whisper_function as wf
from conf import conf as cf


class FixVideo:
    """
    针对下载的文件进行处理
    TODO: 其他需要对原视频进行处理的操作，例如视频中的字幕翻译，将视频转为16:9的分辨率等。
    """

    def __init__(self, input_webm_file, input_mp4_file, input_json_file, model="medium", language='zh', font_size=50, font_file='./HYBiRanTianTianQuanW-2.ttf'):
        """
        :param input_webm_file: 下载的视频文件
        :param input_mp4_file:  下载的音频文件
        :param input_json_file: 记录下载文件的相关信息的json文件
        :param model:语音识别所用的模型
        :param language:语音识别后输出文件的语言
        :param font_size:字体大小
        :param font_file:使用的字体
        """
        self.input_webm_file = input_webm_file
        self.input_mp4_file = input_mp4_file
        self.input_json_file = input_json_file
        # 创建中间文件的根目录
        self.fix_path = ut.create_path_dir(cf.FIX_PATH)
        # 创建输出文件的根目录
        self.output_path = ut.create_path_dir(cf.OUTPUT_PATH)
        self.model = model
        self.language = language
        self.font_file = font_file
        self.font_size = font_size

    def get_cover_text(self):
        """
        获取封面要添加的文字，优先使用原视频翻译后的title,如果翻译失败，则使用channel_name代替
        """
        json_file_content = ut.read_json(self.input_json_file)
        title = json_file_content['title']
        channel_name = json_file_content['channel_name']
        channel_language = json_file_content['channel_language']
        cover_text = ut.translate_to_chinese(title, channel_name, channel_language)
        return cover_text

    def fix_video(self):
        """
        针对下载文件的处理过程
        """
        basename = os.path.basename(self.input_mp4_file)
        print("1.开始合并视频文件与音频文件...")
        combine_file = os.path.join(self.fix_path, basename.replace(".mp4", "_combine.mp4"))
        ff.combine_webm_and_mp4(self.input_webm_file, self.input_mp4_file, combine_file)
        # print("2.开始对合并后的文件进行综合滤镜处理...")
        # filter_file = os.path.join(self.fix_path, basename.replace(".mp4", "_filter.mp4"))
        # width, height = ut.get_video_resolution(combine_file)
        # # 平台支持16:9的视频，故暂时无需进行转换
        # # if width > 1080:
        # #     # 将1920:1080 转为1080:1920
        # #     ff.trans16_9_to_9_16(combine_file, filter_file)
        # # else:
        # #     ff.sharpen_contrast_zoom_of_video(combine_file, filter_file)
        # if width > 1080:
        #     # video视频
        #     ff.sharpen_contrast_zoom_of_video(combine_file, filter_file)
        # else:
        #     # short视频
        #     ff.sharpen_contrast_zoom_of_short(combine_file, filter_file)
        # print("3.开始根据综合滤镜处理后的文件制作封面文件...")
        # cover_file = os.path.join(self.fix_path, basename.replace(".mp4", "_cover.jpeg"))
        # ff.get_cover(filter_file, cover_file)
        # print("4.开始根据原始音频文件提取字幕...")
        # res = wf.get_srt_file(self.input_mp4_file, self.fix_path, model=self.model, language=self.language)
        # return basename, filter_file, cover_file, res

    def output_video(self):
        """
        将最终的封面文件以及合并了字幕的视频文件写出到output目录供后面上传逻辑使用
        :return: True表示封面文件和添加了字幕的视频文件都成功写入到了output目录
        """
        # flag = True
        # basename, filter_file, cover_file, res = self.fix_video()
        # print("5.开始给封面添加文字,结果写入到output目录...")
        # output_cover_file = os.path.join(self.output_path, basename.replace(".mp4", "_cover_with_title.jpeg"))
        # cover_text = self.get_cover_text()
        # ut.cover_add_text(cover_file, output_cover_file, cover_text, font_path=self.font_file, font_size=self.font_size)
        # # whisper执行结束后srt文件输出的默认路径在fix_path下且与视频文件同名
        # srt_file = os.path.join(self.fix_path, basename.replace(".mp4", ".srt"))
        # output_video_file = os.path.join(self.output_path, basename.replace(".mp4", "_output.mp4"))
        # if res != 0 or not os.path.exists(srt_file):
        #     print("res:", res)
        #     print("exist:", os.path.exists(srt_file))
        #     print("6.字幕文件生成失败，请检查字幕文件生成逻辑！")
        #     return False
        # else:
        #     print("6.开始合并字幕文件到视频中,结果写入到output目录...")
        #     try:
        #         ff.combine_srt_and_video_nq(srt_file=srt_file, video_file=filter_file, output_file=output_video_file)
        #     except Exception:
        #         flag = False
        #         print("---合并字幕文件和视频文件的过程失败！")
        #         print("---请检查字幕文件{}是否存在！".format(srt_file))
        #         print("---请检查视频文件{}是否存在！".format(filter_file))
        #     print("7.移动对应的json文件到output目录...")
        #     source_file_name = self.input_webm_file.replace('.webm', '.json')
        #     tag_file_name = os.path.join(cf.OUTPUT_PATH, os.path.basename(source_file_name))
        #     ut.move(source_file_name, tag_file_name)
        # return flag
        self.fix_video()


if __name__ == '__main__':
    webm_file = r'D:\youtube_download\20231126\1700983912269.webm'
    mp4_file = r'D:\youtube_download\20231126\1700983912269.mp4'
    json_file = r'D:\youtube_download\20231126\1700983912269.json'
    fv = FixVideo(webm_file, mp4_file, json_file, model="medium")
    fv.fix_video()

