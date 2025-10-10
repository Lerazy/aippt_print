#!/usr/bin/env python3
"""
aippt.cn PPT转PDF工具 - 自定义配置版
允许用户自定义所有PDF生成参数
使用方法: python aippt_to_pdf_custom.py <PPT链接>
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright
from datetime import datetime
import json

class PDFConfig:
    """PDF配置类"""
    
    def __init__(self):
        # 默认配置
        self.viewport_width = 1920
        self.viewport_height = 1080
        self.pdf_format = "A4"  # A4, A3, Letter
        self.landscape = False
        self.scale = 1.0
        self.margin_top = "1cm"
        self.margin_right = "1cm"
        self.margin_bottom = "1cm"
        self.margin_left = "1cm"
        self.print_background = True
        self.display_header_footer = True
        
    def load_from_file(self, config_file):
        """从配置文件加载设置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            self.viewport_width = config_data.get('viewport_width', self.viewport_width)
            self.viewport_height = config_data.get('viewport_height', self.viewport_height)
            self.pdf_format = config_data.get('pdf_format', self.pdf_format)
            self.landscape = config_data.get('landscape', self.landscape)
            self.scale = config_data.get('scale', self.scale)
            self.margin_top = config_data.get('margin_top', self.margin_top)
            self.margin_right = config_data.get('margin_right', self.margin_right)
            self.margin_bottom = config_data.get('margin_bottom', self.margin_bottom)
            self.margin_left = config_data.get('margin_left', self.margin_left)
            self.print_background = config_data.get('print_background', self.print_background)
            self.display_header_footer = config_data.get('display_header_footer', self.display_header_footer)
            
            print(f"✅ 已加载配置文件: {config_file}")
            
        except FileNotFoundError:
            print(f"⚠️  配置文件不存在: {config_file}，使用默认配置")
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}，使用默认配置")
    
    def save_to_file(self, config_file):
        """保存配置到文件"""
        config_data = {
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'pdf_format': self.pdf_format,
            'landscape': self.landscape,
            'scale': self.scale,
            'margin_top': self.margin_top,
            'margin_right': self.margin_right,
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'print_background': self.print_background,
            'display_header_footer': self.display_header_footer
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存到: {config_file}")
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
    
    def print_config(self):
        """打印当前配置"""
        print("当前PDF配置:")
        print("-" * 40)
        print(f"浏览器大小: {self.viewport_width}x{self.viewport_height}")
        print(f"PDF格式: {self.pdf_format}")
        print(f"横屏模式: {self.landscape}")
        print(f"缩放比例: {self.scale}")
        print(f"边距: 上{self.margin_top} 右{self.margin_right} 下{self.margin_bottom} 左{self.margin_left}")
        print(f"打印背景: {self.print_background}")
        print(f"显示页眉页脚: {self.display_header_footer}")
        print()

async def generate_pdf_from_aippt(url, config, output_path=None):
    """从aippt.cn生成PDF文件 - 自定义配置版"""
    
    config.print_config()
    
    if not output_path:
        # 设置默认输出目录
        output_dir = "/Users/leiyang/Desktop/new/pdf"
        os.makedirs(output_dir, exist_ok=True)
        
        # 从URL提取文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aippt_ppt_custom_{timestamp}.pdf"
        output_path = os.path.join(output_dir, filename)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置视口大小
        await page.set_viewport_size({
            "width": config.viewport_width, 
            "height": config.viewport_height
        })
        
        print(f"正在访问: {url}")
        
        # 访问页面
        await page.goto(url, wait_until="networkidle")
        
        # 等待页面完全加载
        await page.wait_for_timeout(5000)
        
        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 应用缩放（通过CSS）
        if config.scale != 1.0:
            await page.add_style_tag(content=f"""
                body {{
                    transform: scale({config.scale});
                    transform-origin: top left;
                    width: {100/config.scale}%;
                    height: {100/config.scale}%;
                }}
            """)
        
        print("页面加载完成，开始生成PDF...")
        
        # 生成PDF
        pdf_options = {
            "path": output_path,
            "format": config.pdf_format,
            "landscape": config.landscape,
            "print_background": config.print_background,
            "margin": {
                "top": config.margin_top,
                "right": config.margin_right,
                "bottom": config.margin_bottom,
                "left": config.margin_left
            },
            "prefer_css_page_size": True,
            "display_header_footer": config.display_header_footer,
            "header_template": f"<div style='font-size: 10px; text-align: center; width: 100%;'>{title}</div>",
            "footer_template": "<div style='font-size: 10px; text-align: center; width: 100%;'>第 <span class='pageNumber'></span> 页 / 共 <span class='totalPages'></span> 页</div>"
        }
        
        await page.pdf(**pdf_options)
        
        print(f"PDF已生成: {output_path}")
        
        await browser.close()
        return output_path

def create_sample_config():
    """创建示例配置文件"""
    config_file = "pdf_config.json"
    
    sample_configs = {
        "横屏演示": {
            "viewport_width": 1920,
            "viewport_height": 1080,
            "pdf_format": "A4",
            "landscape": True,
            "scale": 0.8,
            "margin_top": "0.5cm",
            "margin_right": "0.5cm",
            "margin_bottom": "0.5cm",
            "margin_left": "0.5cm",
            "print_background": True,
            "display_header_footer": True
        },
        "打印优化": {
            "viewport_width": 1920,
            "viewport_height": 1080,
            "pdf_format": "A4",
            "landscape": False,
            "scale": 0.85,
            "margin_top": "1.5cm",
            "margin_right": "1cm",
            "margin_bottom": "1.5cm",
            "margin_left": "1cm",
            "print_background": True,
            "display_header_footer": True
        },
        "大尺寸": {
            "viewport_width": 2560,
            "viewport_height": 1440,
            "pdf_format": "A3",
            "landscape": True,
            "scale": 1.0,
            "margin_top": "1cm",
            "margin_right": "1cm",
            "margin_bottom": "1cm",
            "margin_left": "1cm",
            "print_background": True,
            "display_header_footer": True
        }
    }
    
    print("可用的示例配置:")
    for name, config in sample_configs.items():
        print(f"- {name}")
    
    choice = input("请选择配置名称 (或按回车使用默认): ").strip()
    
    if choice in sample_configs:
        config_data = sample_configs[choice]
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"✅ 已创建配置文件: {config_file}")
        return config_file
    else:
        print("使用默认配置")
        return None

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python aippt_to_pdf_custom.py <PPT链接> [配置文件]")
        print("示例: python aippt_to_pdf_custom.py https://www.aippt.cn/share/xxx")
        print()
        print("首次使用建议创建配置文件:")
        create_sample_config()
        return
    
    ppt_url = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "pdf_config.json"
    
    # 验证URL
    if not ppt_url.startswith("https://www.aippt.cn/share/"):
        print("❌ 请提供有效的aippt.cn分享链接")
        return
    
    # 创建配置对象
    config = PDFConfig()
    
    # 加载配置文件
    if os.path.exists(config_file):
        config.load_from_file(config_file)
    else:
        print(f"⚠️  配置文件不存在: {config_file}")
        create_choice = input("是否创建示例配置文件? (y/n): ").strip().lower()
        if create_choice == 'y':
            config_file = create_sample_config()
            if config_file:
                config.load_from_file(config_file)
    
    try:
        output_path = await generate_pdf_from_aippt(ppt_url, config)
        print(f"\n✅ PDF生成成功！")
        print(f"📁 文件位置: {os.path.abspath(output_path)}")
        print(f"📄 文件名: {os.path.basename(output_path)}")
        
    except Exception as e:
        print(f"❌ 生成PDF时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

