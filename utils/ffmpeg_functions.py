import os
import sys

from utils.utils import execute_command


def combine_webm_and_mp4(webm_file, mp4_file, output_file):
    """
    ffmpeg：合并视频文件和音频文件
    :param webm_file: 视频文件
    :param mp4_file: 音频文件
    :param output_file: 合并后的文件
    :return: 返回command命令执行后的结果，0表示成功，其余表示失败
    """
    cmd_list = ["ffmpeg", "-y", "-i", webm_file, "-i", mp4_file, "-shortest", output_file]
    print(' '.join(cmd_list))
    return_code = execute_command(cmd_list)
    return return_code


def sharpen(input_file, output_file):
    """
    ffmpeg: 锐化
    使用锐化效果来让画面更锐利，细节可以更加容易的体现出来。
    锐化的滤镜名称是unsharp，它的一般格式是unsharp=x:y:c，x和y是明亮度矩阵xy，默认是5*5，而c是“浓度”，默认值是1。
    快速应用的话，只修改c就能达到想要的目的。c的数字越大，画面越锐利，但随之而来的就是噪点的增加，
    所以要选择适中的参数，基于实战经验，对于国外下载的视频，使用5:5:2的效果比较好。
    """
    filter_complex = "unsharp=5:5:2"
    cmd_list = ["ffmpeg", "-i", input_file, "-filter_complex", filter_complex, "-c:v", "libx264", "-c:a", "copy", "-f", "mp4", output_file, "-y"]
    print(' '.join(cmd_list))
    res = execute_command(cmd_list)
    return res


def contrast_and_brightness(input_file, output_file):
    """
    ffmpeg: 对比度和亮度
    参数格式是"eq=contrast=c:brightness=b..."其中，c是对比度值，1是不调整，>1是对比度加强，<1是对比度减弱。目前使用的值是1.2。
    b是亮度值，0是不调整，>0是变亮，<0是变暗，我目前使用的值是0.1。
    另外，eq滤镜下还有不少其他的参数，如色温等，有需求完全可以自行添加。
    """
    filter_complex = "eq=contrast=1.2:brightness=0.1"
    cmd_list = ["ffmpeg", "-i", input_file, "-filter_complex", filter_complex, "-c:v", "libx264", "-c:a", "copy", "-f", "mp4", output_file, "-y"]
    print(' '.join(cmd_list))
    res = execute_command(cmd_list)
    return res


def zoom_and_crop(input_file, output_file):
    """
    ffmpeg: 缩放和裁剪
    首先看缩放滤镜，它的滤镜格式是scale=x:y，其中x是缩放后的x方向像素数目，y是缩放后的y方向像素数目。
    比如原视频的分辨率是1024*640，如果scale=1025:641就是指放大图像，scale=1023:639就是指缩小图像。
    如果想保持原视频的长宽比，可以把x或y的值设成-1，如scale=1280:-1。
    在实际应用中，光把视频画面放大，提交到平台后往往还是会呈现出一样的大小。
    如果我们想要画面更大，通常需要在放大画面的同时配合裁剪，把画面裁切到原来一样的大小。
    裁剪的滤镜格式是crop=w:h:x:y。
    其中w是裁剪后的x像素数目，h是y像素数目，x是从原视频的左边开始第几个像素开始截取，y是在从原视频的上方开始第几个像素开始截取。
    如我们想要一个1024*640的视频，并且画面的左上角是从原视频的10*20位置开始裁剪：crop=1024:640:10:20。
    现在我们尝试把测试视频略微放大，并裁减到原尺寸（原视频分辨率为1080*1920）
    """
    filter_complex = "scale=1180:-1, crop=1080:1920:150:100"
    cmd_list = ["ffmpeg", "-i", input_file, "-filter_complex", filter_complex, "-c:v", "libx264", "-c:a", "copy", "-f", "mp4", output_file, "-y"]
    print(' '.join(cmd_list))
    res = execute_command(cmd_list)
    return res


def sharpen_contrast_zoom(input_file, output_file):
    """
    ffmpeg: 同时处理锐化、对比度和亮度、缩放和裁剪
    因直接传递字符串cmd命令会报错，所以传递拆分后的命令列表进行处理
    """
    filter_complex = "unsharp=5:5:2, eq=contrast=1.2:brightness=0.1, scale=1180:-1, crop=1080:1920:30:10"
    cmd_list = ["ffmpeg", "-i", input_file, "-filter_complex", filter_complex, "-c:v", "libx264", "-c:a", "copy", "-f", "mp4", output_file, "-y"]
    print(' '.join(cmd_list))
    res = execute_command(cmd_list)
    return res


def get_cover(input_file, cover_file):
    """
    ffmpeg: 抽帧作为封面
    由于发布到自媒体平台时，平台都会要求提供一张封面图用于展示使用.
    如果不主动提供，系统往往会默认使用第一帧或自动随机选一帧，这样一般展示效果不佳。建议主动从视频里获取一帧图片，作为封面图.
    在Youtube里，可以使用pytube调用接口得到原视频作者提供的封面，但是经过我的测试，这些图片分辨率都很低，没有办法下载到原图。
    所以使用强大的ffmpeg，从视频里“抽帧”。抽帧的细节就不介绍了，总的来说使用I帧比较保险，在自动化脚本里，定义获取影片的第一个I帧作为封面图。
    """
    vf = r"select=eq(pict_type\,I)"
    cmd_list = ["ffmpeg", "-i", input_file, "-vf", vf, "-vframes", "1", "-vsync", "vfr", "-qscale:v", "2", "-f", "image2", cover_file, "-y"]
    print(' '.join(cmd_list))
    res = execute_command(cmd_list)
    return res


def combine_srt_and_video_nq(srt_file, video_file, output_file, font_name=None, alignment=2, font_size=10):
    """
    ffmpeg: 使用内嵌字幕的方式合并字幕文件和video视频文件(-y参数告诉 ffmpeg在输出文件已经存在时覆盖它而不提示确认。)
    :param srt_file: 如果是windows系统，输入的路径必须是os.path.join()得到的路径。
        例如 'D:\youtube_fix\aaaaaa.mp4' 这样使用一个\分割的路径, 因为ffmpeg的命令必须使用两个\\，所以有下面程序中的处理方式
        又因为srt_file这个参数是写在单引号里面，所以还需要在:前面加个\
        关于srt_file路径报错，参考：https://www.bilibili.com/read/cv24758560/
    :param video_file:
    :param output_file:
    :param font_name:
    :param alignment:字幕位置：1：左下方，2：底部中心，3右下方，5：左上方，6：顶部中央，7：右上方，9：左中，10：中间中，11：右中
    :param font_size:
    TODO: 添加字幕的大小，位置，字体，颜色等功能 参考：https://magiclen.org/ffmpeg-subtitle/
    方式：内嵌字幕：硬字幕
    """
    if not font_name:
        font_name = 'Noto Sans CJK TC Regular'
    if sys.platform == 'win32':
        srt_file = srt_file.replace("\\", "\\\\").replace(":", r"\:")
        video_file = video_file.replace("\\", "\\\\")
        output_file = output_file.replace("\\", "\\\\")
    # 要使用subprocess.run执行cmd命令，则必须写在一行，不能换行
    # command_str = """ffmpeg -i {} -vf "subtitles='{}':force_style='FontName={},FontSize={}'" {} -y""".format(video_file, srt_file, font_name, font_size, output_file)
    command_str = """ffmpeg -i {} -vf "subtitles='{}':force_style='FontName={},FontSize={},Alignment={}'" {} -y""".format(video_file, srt_file, font_name, font_size, alignment, output_file)
    print(command_str)
    res = execute_command(command_str)
    return res