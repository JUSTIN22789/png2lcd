from PIL import Image
import numpy as np


# ============ 配置 ============
WIDTH = 400
HEIGHT = 300
MODE = '1bit'  # '1bit' 黑白 或 '2bit' 4级灰度



# ============ 转换函数 ============
def c_array_to_image_1bit(data, width, height):
    """将1-bit C数组还原为黑白图像"""
    img = Image.new('L', (width, height), 255)
    pixels = img.load()
    
    byte_idx = 0
    for y in range(height):
        for x in range(0, width, 8):
            if byte_idx >= len(data):
                break
            byte_val = data[byte_idx]
            
            # 解析8个像素
            for bit in range(8):
                if x + bit < width:
                    # bit为1表示黑色，bit为0表示白色
                    if (byte_val >> (7 - bit)) & 1:
                        pixels[x + bit, y] = 0  # 黑色
                    else:
                        pixels[x + bit, y] = 255  # 白色
            
            byte_idx += 1
    
    return img

def c_array_to_image_2bit(data, width, height):
    """将2-bit C数组还原为4级灰度图像"""
    img = Image.new('L', (width, height), 255)
    pixels = img.load()
    
    byte_idx = 0
    for y in range(height):
        for x in range(0, width, 4):
            if byte_idx >= len(data):
                break
            byte_val = data[byte_idx]
            
            # 解析4个像素（每个2bit）
            for i in range(4):
                if x + i < width:
                    # 提取2位灰度值（0-3）
                    shift = 6 - (i * 2)
                    gray_level = (byte_val >> shift) & 0x03
                    
                    # 映射到0-255
                    # 0→0, 1→85, 2→170, 3→255
                    pixel_value = gray_level * 85
                    pixels[x + i, y] = pixel_value
            
            byte_idx += 1
    
    return img

# ============ 从文件读取C数组 ============
def read_c_array_from_file(filename):
    """从.h文件中读取C数组数据"""
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 查找所有0x开头的十六进制数
        import re
        hex_values = re.findall(r'0x[0-9A-Fa-f]{2}', content)
        
        for hex_str in hex_values:
            data.append(int(hex_str, 16))
    
    return data

# ============ 主程序 ============
def main():
    print("="*50)
    print("C数组转点阵图像工具")
    print("="*50)
    
    # 选择输入方式
    print("\n选择输入方式：")
    print("1. 从 epaper_data.h 文件读取")
    print("2. 使用脚本中的data数组")
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == '1':
        filename = 'epaper_data.h'
        print(f"\n正在读取 {filename}...")
        try:
            data = read_c_array_from_file(filename)
            print(f"✓ 读取到 {len(data)} 字节数据")
        except Exception as e:
            print(f"✗ 读取失败: {e}")
            return
    else:
        print(f"\n使用脚本中的data数组 ({len(data)} 字节)")
    
    # 验证数据量
    if MODE == '1bit':
        expected_size = WIDTH * HEIGHT // 8
    elif MODE == '2bit':
        expected_size = WIDTH * HEIGHT // 4
    else:
        print("✗ 不支持的模式！")
        return
    
    print(f"\n数据验证：")
    print(f"  实际数据: {len(data)} 字节")
    print(f"  理论大小: {expected_size} 字节 ({WIDTH}×{HEIGHT}, {MODE})")
    
    if len(data) < expected_size:
        print(f"  ⚠ 警告: 数据不足，将使用现有数据")
    elif len(data) > expected_size:
        print(f"  ⚠ 警告: 数据过多，将截取前{expected_size}字节")
        data = data[:expected_size]
    
    # 转换为图像
    print(f"\n正在转换为图像 ({MODE})...")
    if MODE == '1bit':
        img = c_array_to_image_1bit(data, WIDTH, HEIGHT)
    elif MODE == '2bit':
        img = c_array_to_image_2bit(data, WIDTH, HEIGHT)
    
    # 保存结果
    output_file = 'restored_image.png'
    img.save(output_file)
    
    print("\n" + "="*50)
    print("✓ 转换完成！")
    print("="*50)
    print(f"输出文件: {output_file}")
    print(f"图像尺寸: {WIDTH}×{HEIGHT}")
    print(f"显示模式: {MODE}")
    print("\n对比 restored_image.png 和 preview.png 看是否一致！")

if __name__ == '__main__':
    main()

