from utils.utils import execute_command


def get_srt_file(input_file, output_dir, model='medium', language='zh'):
    """
    whisper: 获取srt字幕文件,输出的srt文件默认与输入文件同名
    注：只有将model设置为medium，才可以把语言翻译成中文，不然指定language无效
    """
    cmd_list = ["whisper", input_file, "--model", model, "--language", language, "-o", output_dir, "-f", "srt"]
    print(cmd_list)
    res = execute_command(cmd_list)
    return res
