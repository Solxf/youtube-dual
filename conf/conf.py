# 快手平台地址
PLATFORM_KS = "https://cp.kuaishou.com/article/publish/video"

# 抖音平台上传地址
PLATFORM_DY = None

# 西瓜平台上传地址
PLATFORM_XG = None

# 小红书平台上传地址
PLATFORM_XHS = None

# 皮皮搞笑平台上传地址
PLATFORM_PP = None

# 目前支持的平台，后续如果有增加其他平台的功能，则在此处加入，即可上传到对应的平台
SUPPORT_PLATFORM = ['KS', 'DY', 'XHS']

# 下载文件的根目录
DOWNLOAD_PATH = 'D:\\youtube_download'
# 剪辑文件的根目录（中间目录）
FIX_PATH = 'D:\\youtube_fix'
# 将剪辑成功的文件移到备份目录（备份目录）
DOWNLOAD_BAK_PATH = 'D:\\youtube_download_bak'
# 最终输出文件的根目录
OUTPUT_PATH = 'D:\\youtube_output'
# 上传成功后移出OUTPUT_PATH,备份到这个目录
OUTPUT_BAK_PATH = 'D:\\youtube_output_bak'

# 上传视频过程中等待的时间
WAIT_TIME_UPLOAD_VIDEO = 120

# 上传封面和点击上传按钮后等待的时间
WAIT_TIME_UPLOAD_COVER = 10

# 频道检测等待时间
WAIT_TIME_CHANNEL_CHECK = 1

# chrome浏览器驱动位置
CHROME_DRIVER_PATH = r'E:\pycharm\python_workspace\youtobe-deal\conf\chromedriver.exe'
