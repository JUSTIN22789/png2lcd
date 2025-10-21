from PIL import Image
import config
from image_processor import ImageProcessor
from matrix_converter import MatrixConverter
from output_generator import OutputGenerator

def main():
    input_image = r'D:\同济部分文件\在办\照片转点阵\02.jpg'
    output_file = 'epaper_data.h'
    
    print("="*50)
    mode_str = f"{config.GRAYSCALE_LEVELS}级灰度" if config.USE_GRAYSCALE else "黑白"
    print(f"E-Paper 图片转点阵工具 (400×300, {mode_str})")
    print("="*50)
    
    processor = ImageProcessor(config.EPAPER_WIDTH, config.EPAPER_HEIGHT)
    converter = MatrixConverter(config.EPAPER_WIDTH, config.EPAPER_HEIGHT)
    generator = OutputGenerator()
    
    # 1. 加载图片
    print(f"\n[1/5] 加载图片: {input_image}")
    img = processor.load(input_image)
    if img is None:
        return
    
    # 2. 调整尺寸
    print(f"[2/5] 调整尺寸: {config.EPAPER_WIDTH}×{config.EPAPER_HEIGHT}")
    img_resized = processor.resize(img)
    
    # 3. 根据模式进行转换
    if config.USE_GRAYSCALE:
        # 灰度模式
        print(f"[3/5] 转换为{config.GRAYSCALE_LEVELS}级灰度")
        img_processed = processor.convert_to_grayscale(
            img_resized, 
            levels=config.GRAYSCALE_LEVELS
        )
        mode = '2bit'
    else:
        # 黑白模式
        dither_str = "启用抖动" if config.DITHERING else f"阈值={config.THRESHOLD}"
        print(f"[3/5] 二值化处理 ({dither_str})")
        img_processed = processor.convert_to_bw(
            img_resized,
            threshold=config.THRESHOLD,
            use_dithering=config.DITHERING,
            brightness_factor=config.BRIGHTNESS_FACTOR,
            contrast_factor=config.CONTRAST_FACTOR
        )
        mode = '1bit'
    
    # 保存预览
    processor.preview(img_processed, 'preview.png')
    
    # 4. 转换为点阵数据
    print(f"[4/5] 转换为点阵数据 ({mode})")
    data = converter.convert(img_processed, mode=mode)
    print(f"     → 生成 {len(data)} 字节数据 ({len(data)/1024:.1f} KB)")
    
    # 5. 生成输出文件
    print(f"[5/5] 生成输出文件: {output_file}")
    c_code = generator.generate_c_array(data, "image_400x300")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(c_code)
    
    print("\n" + "="*50)
    print("✓ 转换完成！")
    print("="*50)
    print(f"输出文件: {output_file}")
    print(f"数据大小: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    print(f"预览图片: preview.png")
    print(f"显示模式: {mode_str}")

if __name__ == '__main__':
    main()