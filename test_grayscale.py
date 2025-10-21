from PIL import Image
from image_processor import ImageProcessor

print("="*50)
print("灰度转换测试")
print("="*50)

# 初始化
processor = ImageProcessor(400, 300)

# 加载图片
print("\n[1] 加载图片...")
img = processor.load(r"D:\同济部分文件\在办\照片转点阵\02.jpg")

# 调整尺寸
print("[2] 调整尺寸到 400×300...")
img_resized = processor.resize(img)

# 保存原图
img_resized.save('gray_0_original.png')
print("    → 原图: gray_0_original.png")

# 测试不同灰度级别
print("\n[3] 转换灰度...")

# 4级灰度
print("    → 4级灰度")
img_4gray = processor.convert_to_grayscale(img_resized, levels=4)
img_4gray.save('gray_1_4levels.png')

# 16级灰度
print("    → 16级灰度")
img_16gray = processor.convert_to_grayscale(img_resized, levels=16)
img_16gray.save('gray_2_16levels.png')

print("\n" + "="*50)
print("✓ 测试完成！")
print("="*50)
print("生成文件：")
print("  - gray_0_original.png  (原图)")
print("  - gray_1_4levels.png   (4级灰度)")
print("  - gray_2_16levels.png  (16级灰度)")

