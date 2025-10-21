# 墨水屏参数配置
EPAPER_WIDTH = 400
EPAPER_HEIGHT = 300

# 显示模式
USE_GRAYSCALE = False       # False=黑白模式, True=灰度模式
GRAYSCALE_LEVELS = 4        # 灰度级别（仅在USE_GRAYSCALE=True时有效）

# 黑白模式参数
THRESHOLD = 128             # 二值化阈值 (0-255)
DITHERING = True            # 是否使用抖动算法
BRIGHTNESS_FACTOR = 0.75    # 亮度调整（0.5-1.0，越小越暗）
CONTRAST_FACTOR = 1.2       # 对比度调整（1.0-1.5，越大越分明）

# 输出设置
OUTPUT_FORMAT = 'c_array'
BYTES_PER_LINE = 16