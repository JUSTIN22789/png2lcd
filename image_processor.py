from PIL import Image, ImageOps, ImageEnhance

class ImageProcessor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def load(self, image_path):
        """加载图片"""
        try:
            img = Image.open(image_path)
            print(f"原始尺寸: {img.size[0]}X{img.size[1]}")
            return img
        except Exception as e:
            print(f"错误: 无法加载图片 - {e}")
            return None
    
    def resize(self, img):
        """智能缩放到目标尺寸"""
        orig_w, orig_h = img.size
        target_w, target_h = self.width, self.height
        
        ratio = max(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        img_scaled = img.resize((new_w, new_h), Image.LANCZOS)
        
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img_cropped = img_scaled.crop((
            left, top, 
            left + target_w, 
            top + target_h
        ))
        
        return img_cropped
    
    def convert_to_grayscale(self, img, levels=4):
        """转换为指定级别的灰度图
        
        参数:
            img: 输入图像
            levels: 灰度级别（2/4/16/256）
        """
        import numpy as np
        
        # 转为灰度图
        img_gray = img.convert('L')
        
        # 量化到指定灰度级别
        pixels = np.array(img_gray, dtype=np.uint16)  # 使用uint16避免溢出
        
        # 映射0-255到0-(levels-1)
        # 例如4级: 0-63→0, 64-127→1, 128-191→2, 192-255→3
        quantized = (pixels * levels // 256).astype(np.uint8)
        
        # 映射回0-255用于显示
        # 例如4级: 0→0, 1→85, 2→170, 3→255
        if levels > 1:
            display = (quantized.astype(np.uint16) * 255 // (levels - 1)).astype(np.uint8)
        else:
            display = quantized
        
        img_result = Image.fromarray(display, mode='L')
        return img_result
    
    def convert_to_bw(self, img, threshold=128, use_dithering=True, 
                      brightness_factor=0.95, contrast_factor=1.5):
        """转为黑白图（二值化）"""
        # 转为灰度图
        img_gray = img.convert('L')
        
        if use_dithering:
            # 使用Floyd-Steinberg抖动算法
            contrast = ImageEnhance.Contrast(img_gray)
            img_gray = contrast.enhance(contrast_factor)
            
            brightness = ImageEnhance.Brightness(img_gray)
            img_gray = brightness.enhance(brightness_factor)

            img_bw = img_gray.convert('1', dither=Image.FLOYDSTEINBERG)
        else:
            img_bw = img_gray.point(lambda x: 255 if x > threshold else 0, '1')
        
        return img_bw
    
    def preview(self, img, filename='preview.png'):
        """保存预览"""
        img.save(filename)
        print(f"   预览已保存: {filename}")