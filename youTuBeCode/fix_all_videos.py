import os

from conf import conf as cf
from utils import utils as ut
from fix_video import FixVideo


download_bak_path = ut.create_path_dir(cf.DOWNLOAD_BAK_PATH)
# 获取下载目录下的所有文件
download_file_list = ut.get_download_files(cf.DOWNLOAD_PATH)
# 找出同时具有webm,mp4,json的文件
valid_file_list = ut.get_valid_files(download_file_list)
if valid_file_list:
    # 获取去重后的不带后缀的文件名
    file_list = sorted(set([os.path.basename(i).split(".")[0] for i in valid_file_list]))
    print("本次待剪辑的文件列表为：{}".format(file_list))
    for file in file_list:
        # 找出当前文件命对应的3个文件（webm, mp4, json）
        current_file_list = [i for i in valid_file_list if file in i]
        webm_file = [i for i in current_file_list if i.endswith(".webm")][0]
        mp4_file = [i for i in current_file_list if i.endswith(".mp4")][0]
        json_file = [i for i in current_file_list if i.endswith(".json")][0]
        print("准备处理{}对应的文件...".format(file))
        print("{}对应的视频文件为:{}".format(file, webm_file))
        print("{}对应的音频文件为:{}".format(file, mp4_file))
        print("{}对应的信息文件为:{}".format(file, json_file))
        # fix该文件
        fv = FixVideo(webm_file, mp4_file, json_file)
        res = fv.output_video()
        # 将成功处理后的原始文件移动到备份目录
        if res:
            ut.move(webm_file, os.path.join(download_bak_path, os.path.basename(webm_file)))
            ut.move(mp4_file, os.path.join(download_bak_path, os.path.basename(mp4_file)))


