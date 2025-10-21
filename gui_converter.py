import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import config
from image_processor import ImageProcessor
from matrix_converter import MatrixConverter
from output_generator import OutputGenerator
import os

class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("照片转点阵工具 - 400×300墨水屏")
        self.root.geometry("1200x800")
        
        # 初始化处理器
        self.processor = ImageProcessor(config.EPAPER_WIDTH, config.EPAPER_HEIGHT)
        self.converter = MatrixConverter(config.EPAPER_WIDTH, config.EPAPER_HEIGHT)
        self.generator = OutputGenerator()
        
        # 存储图像
        self.original_img = None
        self.processed_img = None
        self.preview_img = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # ========== 顶部工具栏 ==========
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="📁 选择图片", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔄 转换", command=self.convert_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="💾 导出", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="✓ 验证", command=self.verify_data).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.status_label = ttk.Label(toolbar, text="状态: 等待加载图片...")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # ========== 主内容区 ==========
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：原图和预览
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 原图
        ttk.Label(left_frame, text="原始图片", font=("Arial", 12, "bold")).pack(pady=5)
        self.original_canvas = tk.Canvas(left_frame, width=400, height=300, bg="gray90")
        self.original_canvas.pack(pady=5)
        
        # 转换后
        ttk.Label(left_frame, text="转换预览", font=("Arial", 12, "bold")).pack(pady=5)
        self.preview_canvas = tk.Canvas(left_frame, width=400, height=300, bg="gray90")
        self.preview_canvas.pack(pady=5)
        
        # 右侧：参数控制
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        right_frame.pack_propagate(False)
        
        # 参数面板
        params_frame = ttk.LabelFrame(right_frame, text="转换参数", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示模式
        ttk.Label(params_frame, text="显示模式:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.mode_var = tk.StringVar(value="黑白")
        ttk.Radiobutton(params_frame, text="黑白 (1-bit, 15KB)", 
                       variable=self.mode_var, value="黑白").pack(anchor=tk.W)
        ttk.Radiobutton(params_frame, text="4级灰度 (2-bit, 30KB)", 
                       variable=self.mode_var, value="灰度").pack(anchor=tk.W)
        
        ttk.Separator(params_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 黑白模式参数
        bw_frame = ttk.LabelFrame(params_frame, text="黑白模式参数", padding=5)
        bw_frame.pack(fill=tk.X, pady=5)
        
        # 抖动开关
        self.dither_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bw_frame, text="启用Floyd-Steinberg抖动", 
                       variable=self.dither_var).pack(anchor=tk.W)
        
        # 阈值（仅在不抖动时有效）
        ttk.Label(bw_frame, text="阈值 (不抖动时):").pack(anchor=tk.W, pady=(10, 0))
        self.threshold_var = tk.IntVar(value=128)
        threshold_scale = ttk.Scale(bw_frame, from_=0, to=255, 
                                   variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.pack(fill=tk.X)
        ttk.Label(bw_frame, textvariable=self.threshold_var).pack(anchor=tk.E)
        
        # 亮度
        ttk.Label(bw_frame, text="亮度调整:").pack(anchor=tk.W, pady=(10, 0))
        self.brightness_var = tk.DoubleVar(value=0.95)
        brightness_scale = ttk.Scale(bw_frame, from_=0.5, to=1.0, 
                                    variable=self.brightness_var, orient=tk.HORIZONTAL)
        brightness_scale.pack(fill=tk.X)
        brightness_label = ttk.Label(bw_frame, text="")
        brightness_label.pack(anchor=tk.E)
        
        def update_brightness_label(*args):
            brightness_label.config(text=f"{self.brightness_var.get():.2f}")
        self.brightness_var.trace('w', update_brightness_label)
        update_brightness_label()
        
        # 对比度
        ttk.Label(bw_frame, text="对比度调整:").pack(anchor=tk.W, pady=(10, 0))
        self.contrast_var = tk.DoubleVar(value=1.5)
        contrast_scale = ttk.Scale(bw_frame, from_=1.0, to=2.0, 
                                  variable=self.contrast_var, orient=tk.HORIZONTAL)
        contrast_scale.pack(fill=tk.X)
        contrast_label = ttk.Label(bw_frame, text="")
        contrast_label.pack(anchor=tk.E)
        
        def update_contrast_label(*args):
            contrast_label.config(text=f"{self.contrast_var.get():.2f}")
        self.contrast_var.trace('w', update_contrast_label)
        update_contrast_label()
        
        ttk.Separator(params_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 信息显示
        info_frame = ttk.LabelFrame(params_frame, text="图像信息", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(info_frame, height=8, width=30, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH)
        self.update_info("未加载图片")

        # 参数建议窗口
        text_frame = ttk.LabelFrame(params_frame, text="参数建议", padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 创建滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本框
        self.text_display = tk.Text(
            text_frame, 
            height=10,
            width=30,
            wrap=tk.WORD,
            yscrollcommand=text_scroll.set,
            font=("Arial", 9),
            state=tk.NORMAL  # 先设置为可编辑，填充内容后再改为只读
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.text_display.yview)
        
        # 填充说明文本（你可以在这里修改内容）
        help_text = """【参数调整建议】

黑白模式：
• 照片偏亮 → 降低亮度 (0.7-0.8)
• 照片偏暗 → 提高亮度 (0.9-1.0)
• 对比不足 → 提高对比度 (1.3-1.5)
• 细节丢失 → 启用抖动算法

抖动效果：
• 抖动开启：细节更好，有噪点
• 抖动关闭：清晰锐利，细节少

阈值法（不抖动）：
• 阈值越低 → 越多黑色
• 阈值越高 → 越多白色
• 推荐值：120-150

灰度模式：
• 4级灰度效果更柔和
• 数据量是黑白的2倍
• 适合显示照片
"""
        self.text_display.insert(1.0, help_text)
        
        # 设置为只读
        self.text_display.config(state=tk.DISABLED)
        
    def update_info(self, message):
        """更新信息框"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, message)
        
    def load_image(self):
        """加载图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            self.status_label.config(text=f"状态: 正在加载...")
            self.root.update()
            
            # 加载图片
            self.original_img = self.processor.load(file_path)
            if self.original_img is None:
                messagebox.showerror("错误", "无法加载图片！")
                return
            
            # 调整尺寸
            self.processed_img = self.processor.resize(self.original_img)
            
            # 显示原图
            self.display_image(self.processed_img, self.original_canvas)
            
            # 更新信息
            info = f"文件: {os.path.basename(file_path)}\n"
            info += f"原始尺寸: {self.original_img.size[0]}×{self.original_img.size[1]}\n"
            info += f"目标尺寸: 400×300\n"
            info += f"模式: {self.original_img.mode}\n"
            self.update_info(info)
            
            self.status_label.config(text=f'状态: 图片已加载，点击"转换"按钮')

        except Exception as e:
            messagebox.showerror("错误", f"加载失败: {str(e)}")
            self.status_label.config(text=f"状态: 加载失败")
    
    def convert_image(self):
        """转换图片"""
        if self.processed_img is None:
            messagebox.showwarning("警告", "请先加载图片！")
            return
        
        try:
            mode = self.mode_var.get()
            
            self.status_label.config(text=f"状态: 正在转换...")
            self.root.update()
            
            if mode == "黑白":
                # 黑白模式
                self.preview_img = self.processor.convert_to_bw(
                    self.processed_img,
                    threshold=self.threshold_var.get(),
                    use_dithering=self.dither_var.get(),
                    brightness_factor=self.brightness_var.get(),
                    contrast_factor=self.contrast_var.get()
                )
                data_size = 15000
            else:
                # 灰度模式
                self.preview_img = self.processor.convert_to_grayscale(
                    self.processed_img,
                    levels=4
                )
                data_size = 30000
            
            # 显示预览
            self.display_image(self.preview_img, self.preview_canvas)
            
            # 更新信息
            info = f"转换模式: {mode}\n"
            info += f"数据大小: {data_size} 字节 ({data_size/1024:.1f} KB)\n"
            info += f"\n参数:\n"
            if mode == "黑白":
                info += f"  抖动: {'是' if self.dither_var.get() else '否'}\n"
                if not self.dither_var.get():
                    info += f"  阈值: {self.threshold_var.get()}\n"
                info += f"  亮度: {self.brightness_var.get():.2f}\n"
                info += f"  对比度: {self.contrast_var.get():.2f}\n"
            else:
                info += f"  灰度级别: 4级\n"
            
            self.update_info(info)
            self.status_label.config(text=f"状态: 转换完成，可以导出")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            self.status_label.config(text=f"状态: 转换失败")
    
    def export_data(self):
        """导出数据"""
        if self.preview_img is None:
            messagebox.showwarning("警告", "请先转换图片！")
            return
        
        try:
            self.status_label.config(text=f"状态: 正在导出...")
            self.root.update()
            
            mode = self.mode_var.get()
            
            # 转换为点阵数据
            if mode == "黑白":
                data = self.converter.convert(self.preview_img, mode='1bit')
            else:
                data = self.converter.convert(self.preview_img, mode='2bit')
            
            # 选择保存位置
            file_path = filedialog.asksaveasfilename(
                title="保存数据文件",
                defaultextension=".h",
                filetypes=[
                    ("C头文件", "*.h"),
                    ("二进制文件", "*.bin"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 生成并保存
            if file_path.endswith('.bin'):
                # 二进制格式
                with open(file_path, 'wb') as f:
                    f.write(bytes(data))
            else:
                # C数组格式
                c_code = self.generator.generate_c_array(data, "image_400x300")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(c_code)
            
            # 同时保存预览图
            preview_path = file_path.rsplit('.', 1)[0] + '_preview.png'
            self.preview_img.save(preview_path)
            
            messagebox.showinfo("成功", 
                              f"导出成功！\n\n"
                              f"数据文件: {os.path.basename(file_path)}\n"
                              f"预览图片: {os.path.basename(preview_path)}\n"
                              f"数据大小: {len(data)} 字节")
            
            self.status_label.config(text=f"状态: 导出成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
            self.status_label.config(text=f"状态: 导出失败")
    
    def verify_data(self):
        """验证数据（还原显示）"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[
                ("C头文件", "*.h"),
                ("二进制文件", "*.bin"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.config(text=f"状态: 正在验证...")
            self.root.update()
            
            # 读取数据
            if file_path.endswith('.bin'):
                with open(file_path, 'rb') as f:
                    data = list(f.read())
            else:
                # 从C数组读取
                import re
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                hex_values = re.findall(r'0x[0-9A-Fa-f]{2}', content)
                data = [int(h, 16) for h in hex_values]
            
            # 根据数据大小判断模式
            if len(data) == 15000:
                mode = '1bit'
            elif len(data) == 30000:
                mode = '2bit'
            else:
                messagebox.showerror("错误", f"数据大小不匹配！\n期望: 15000或30000字节\n实际: {len(data)}字节")
                return
            
            # 还原图像
            if mode == '1bit':
                restored = self.restore_1bit(data)
            else:
                restored = self.restore_2bit(data)
            
            # 显示
            self.display_image(restored, self.preview_canvas)
            
            messagebox.showinfo("验证成功", 
                              f"数据验证成功！\n\n"
                              f"模式: {mode}\n"
                              f"数据大小: {len(data)} 字节\n"
                              f"图像尺寸: 400×300")
            
            self.status_label.config(text=f"状态: 验证完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"验证失败: {str(e)}")
            self.status_label.config(text=f"状态: 验证失败")
    
    def restore_1bit(self, data):
        """还原1-bit黑白图像"""
        import numpy as np
        img = Image.new('L', (400, 300), 255)
        pixels = img.load()
        
        byte_idx = 0
        for y in range(300):
            for x in range(0, 400, 8):
                if byte_idx >= len(data):
                    break
                byte_val = data[byte_idx]
                for bit in range(8):
                    if x + bit < 400:
                        if (byte_val >> (7 - bit)) & 1:
                            pixels[x + bit, y] = 0
                        else:
                            pixels[x + bit, y] = 255
                byte_idx += 1
        
        return img
    
    def restore_2bit(self, data):
        """还原2-bit灰度图像"""
        import numpy as np
        img = Image.new('L', (400, 300), 255)
        pixels = img.load()
        
        byte_idx = 0
        for y in range(300):
            for x in range(0, 400, 4):
                if byte_idx >= len(data):
                    break
                byte_val = data[byte_idx]
                for i in range(4):
                    if x + i < 400:
                        shift = 6 - (i * 2)
                        gray_level = (byte_val >> shift) & 0x03
                        pixel_value = gray_level * 85
                        pixels[x + i, y] = pixel_value
                byte_idx += 1
        
        return img
    
    def display_image(self, pil_image, canvas):
        """在画布上显示图像"""
        # 创建缩略图
        display_img = pil_image.copy()
        display_img.thumbnail((400, 300), Image.LANCZOS)
        
        # 转换为Tkinter格式
        photo = ImageTk.PhotoImage(display_img)
        
        # 保存引用（防止被垃圾回收）
        canvas.image = photo
        
        # 清空并显示
        canvas.delete("all")
        canvas.create_image(200, 150, image=photo)

def main():
    root = tk.Tk()
    app = ImageConverterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

