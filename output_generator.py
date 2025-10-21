class OutputGenerator:
    def generate_c_array(self, data, var_name="epaper_image"):
        """生成C语言数组"""
        output = []
        output.append(f"// Image size: {len(data)} bytes")
        output.append(f"const unsigned char {var_name}[{len(data)}] = {{")
        
        # 每行16个字节
        for i in range(0, len(data), 16):
            line = data[i:i+16]
            hex_str = ', '.join([f'0x{b:02X}' for b in line])
            output.append(f"    {hex_str},")
        
        output.append("};")
        return '\n'.join(output)
    
    def generate_binary(self, data, filename):
        """生成二进制文件"""
        with open(filename, 'wb') as f:
            f.write(bytes(data))
    
    def generate_hex_file(self, data, filename):
        """生成HEX文件（某些墨水屏需要）"""
        pass