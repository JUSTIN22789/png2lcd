import numpy as np

class MatrixConverter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def convert_1bit(self, img_bw):
        """转换为1位黑白数据（纯黑白）
        
        每个像素用1位表示（0或1）
        8个像素组成1个字节
        
        字节格式：横向8个像素从高位到低位
        """
        pixels = np.array(img_bw)
        buffer = []
        
        for y in range(self.height):
            for x in range(0, self.width, 8):
                byte_val = 0
                
                # 处理8个像素
                for bit in range(8):
                    if x + bit < self.width:
                        pixel = pixels[y, x + bit]
                        
                        # 如果是黑色（0），设置对应位为1
                        if pixel == 0:
                            byte_val |= (1 << (7 - bit))
                
                buffer.append(byte_val)
        
        return buffer
    
    def convert_2bit(self, img_gray):
        """转换为2位灰度数据（4级灰度）
        
        每个像素用2位表示（0-3）
        4个像素组成1个字节
        
        字节格式：[像素0(2bit)][像素1(2bit)][像素2(2bit)][像素3(2bit)]
        """
        pixels = np.array(img_gray)
        buffer = []
        
        for y in range(self.height):
            for x in range(0, self.width, 4):
                byte_val = 0
                
                # 处理4个像素
                for i in range(4):
                    if x + i < self.width:
                        pixel = pixels[y, x + i]
                        
                        # 映射0-255到0-3
                        gray_level = pixel * 4 // 256
                        
                        # 放入字节的对应位置
                        # 像素0在最高2位，像素3在最低2位
                        shift = 6 - (i * 2)
                        byte_val |= (gray_level << shift)
                
                buffer.append(byte_val)
        
        return buffer
    
    def convert(self, img, mode='1bit'):
        """转换接口
        
        参数:
            img: PIL Image对象
            mode: '1bit' (黑白) 或 '2bit' (4级灰度)
        """
        if mode == '1bit':
            return self.convert_1bit(img)
        elif mode == '2bit':
            return self.convert_2bit(img)
        else:
            raise ValueError(f"不支持的模式: {mode}，请使用 '1bit' 或 '2bit'")