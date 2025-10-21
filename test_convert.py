from PIL import Image
from image_processor import ImageProcessor

print("="*50)
print("黑白二值化转换测试")
print("="*50)

# 初始化
processor = ImageProcessor(400, 300)

# 加载图片
print("\n[1] 加载图片...")
img = processor.load(r"D:\同济部分文件\在办\照片转点阵\02.jpg")

# 调整尺寸
print("[2] 调整尺寸到 400×300...")
img_resized = processor.resize(img)
img_bw_1 = processor.convert_to_bw(img_resized, threshold=128, use_dithering=True,
                                 brightness_factor=1, contrast_factor=1.5)
processor.preview(img_bw_1, 'preview_dither_standard.png')

