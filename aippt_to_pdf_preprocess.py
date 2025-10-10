#!/usr/bin/env python3
"""
aippt.cn PPT转PDF工具 - 网页预处理版
在生成PDF前对网页进行预处理：删除侧边栏、调整缩放、删除工具栏
使用方法: python aippt_to_pdf_preprocess.py <PPT链接> [配置名称]
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright
from datetime import datetime
import re

# 预设配置
PRESET_CONFIGS = {
    "default": {
        "name": "默认配置",
        "viewport": {"width": 1920, "height": 1080},
        "pdf_format": "A4",
        "landscape": False,
        "scale": 1.0,
        "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
    },
    "landscape": {
        "name": "横屏模式",
        "viewport": {"width": 1920, "height": 1080},
        "pdf_format": "A4",
        "landscape": True,
        "scale": 0.8,
        "margin": {"top": "0.5cm", "right": "0.5cm", "bottom": "0.5cm", "left": "0.5cm"}
    },
    "large": {
        "name": "大尺寸模式",
        "viewport": {"width": 2560, "height": 1440},
        "pdf_format": "A3",
        "landscape": True,
        "scale": 1.0,
        "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
    },
    "compact": {
        "name": "紧凑模式",
        "viewport": {"width": 1366, "height": 768},
        "pdf_format": "A4",
        "landscape": False,
        "scale": 0.7,
        "margin": {"top": "0.3cm", "right": "0.3cm", "bottom": "0.3cm", "left": "0.3cm"}
    },
    "presentation": {
        "name": "演示模式",
        "viewport": {"width": 1920, "height": 1080},
        "pdf_format": "A4",
        "landscape": True,
        "scale": 0.9,
        "margin": {"top": "0.8cm", "right": "0.8cm", "bottom": "0.8cm", "left": "0.8cm"}
    },
    "print": {
        "name": "打印优化",
        "viewport": {"width": 1920, "height": 1080},
        "pdf_format": "A4",
        "landscape": False,
        "scale": 0.85,
        "margin": {"top": "1.5cm", "right": "1cm", "bottom": "1.5cm", "left": "1cm"}
    }
}

async def preprocess_page(page):
    """预处理页面：删除侧边栏、调整缩放、删除工具栏"""
    
    print("开始预处理页面...")
    
    # 第一步：删除侧边栏
    try:
        print("🔍 正在查找侧边栏元素...")
        await page.wait_for_timeout(1000)  # 等待1秒让您看到查找过程
        aside_element = await page.query_selector('.main-preview-aside')
        if aside_element:
            await aside_element.evaluate('element => element.remove()')
            print("✅ 已删除侧边栏 (.main-preview-aside)")
            await page.wait_for_timeout(2000)  # 等待2秒让您看到删除效果
        else:
            print("⚠️  未找到侧边栏元素 (.main-preview-aside)")
    except Exception as e:
        print(f"❌ 删除侧边栏失败: {e}")
    
    # 第二步：调整缩放比例
    try:
        # 找到缩放按钮和显示元素
        # 先找到所有按钮，然后通过SVG内容判断
        all_buttons = await page.query_selector_all('div.btn')
        zoom_out_btn = None
        zoom_in_btn = None
        
        for btn in all_buttons:
            svg_content = await btn.query_selector('svg use')
            if svg_content:
                href = await svg_content.get_attribute('xlink:href')
                if href == '#icon-suoxiao1':
                    zoom_out_btn = btn
                elif href == '#icon-fangda1':
                    zoom_in_btn = btn
        
        scale_display = await page.query_selector('span.scale-num')
        
        if zoom_out_btn and zoom_in_btn and scale_display:
            print("🔍 开始调整缩放比例...")
            await page.wait_for_timeout(1000)  # 等待1秒让您看到开始过程
            
            # 先缩小到10%或以下
            max_attempts = 50  # 防止无限循环
            attempts = 0
            
            print("📉 开始缩小到10%...")
            while attempts < max_attempts:
                current_scale_text = await scale_display.text_content()
                current_scale = int(re.findall(r'\d+', current_scale_text)[0])
                
                print(f"当前缩放: {current_scale}%")
                
                if current_scale <= 10:
                    print("✅ 缩放已调整到10%或以下")
                    await page.wait_for_timeout(2000)  # 等待2秒让您看到最终效果
                    break
                
                # 点击缩小按钮
                await zoom_out_btn.click()
                await page.wait_for_timeout(800)  # 增加等待时间让您看到缩放过程
                attempts += 1
            
            # 再放大到170%
            print("📈 开始放大到170%...")
            attempts = 0
            while attempts < max_attempts:
                current_scale_text = await scale_display.text_content()
                current_scale = int(re.findall(r'\d+', current_scale_text)[0])
                
                print(f"当前缩放: {current_scale}%")
                
                if current_scale >= 170:
                    print("✅ 缩放已调整到170%")
                    await page.wait_for_timeout(2000)  # 等待2秒让您看到最终效果
                    break
                
                # 点击放大按钮
                await zoom_in_btn.click()
                await page.wait_for_timeout(800)  # 增加等待时间让您看到缩放过程
                attempts += 1
                
        else:
            print("⚠️  未找到缩放控制元素")
            
    except Exception as e:
        print(f"❌ 调整缩放失败: {e}")
    
    # 第三步：删除工具栏
    try:
        print("🔍 正在查找工具栏元素...")
        await page.wait_for_timeout(1000)  # 等待1秒让您看到查找过程
        toolkit_element = await page.query_selector('.sharepreview-toolkit')
        if toolkit_element:
            await toolkit_element.evaluate('element => element.remove()')
            print("✅ 已删除工具栏 (.sharepreview-toolkit)")
            await page.wait_for_timeout(2000)  # 等待2秒让您看到删除效果
        else:
            print("⚠️  未找到工具栏元素 (.sharepreview-toolkit)")
    except Exception as e:
        print(f"❌ 删除工具栏失败: {e}")
    
    print("页面预处理完成！")

async def generate_pdf_from_aippt(url, config_name="default", output_path=None):
    """从aippt.cn生成PDF文件 - 预处理版"""
    
    # 获取配置
    config = PRESET_CONFIGS.get(config_name, PRESET_CONFIGS["default"])
    print(f"使用配置: {config['name']}")
    print(f"浏览器大小: {config['viewport']['width']}x{config['viewport']['height']}")
    print(f"PDF格式: {config['pdf_format']}, 横屏: {config['landscape']}, 缩放: {config['scale']}")
    
    if not output_path:
        # 设置默认输出目录
        output_dir = "/Users/leiyang/Desktop/new/pdf"
        os.makedirs(output_dir, exist_ok=True)
        
        # 从URL提取文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aippt_ppt_preprocess_{config_name}_{timestamp}.pdf"
        output_path = os.path.join(output_dir, filename)
    
    async with async_playwright() as p:
        # 启动浏览器（有头模式，用于调试）
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 设置视口大小
        await page.set_viewport_size(config["viewport"])
        
        print(f"正在访问: {url}")
        
        # 访问页面
        await page.goto(url, wait_until="networkidle")
        
        # 等待页面完全加载
        await page.wait_for_timeout(5000)
        
        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 预处理页面
        await preprocess_page(page)
        
        # 等待预处理完成
        await page.wait_for_timeout(2000)
        
        # 应用缩放（通过CSS）
        if config["scale"] != 1.0:
            await page.add_style_tag(content=f"""
                body {{
                    transform: scale({config['scale']});
                    transform-origin: top left;
                    width: {100/config['scale']}%;
                    height: {100/config['scale']}%;
                }}
            """)
        
        print("页面加载完成，开始生成PDF...")
        
        # 生成PDF
        pdf_options = {
            "path": output_path,
            "format": config["pdf_format"],
            "landscape": config["landscape"],
            "print_background": True,
            "margin": config["margin"],
            "prefer_css_page_size": True,
            "display_header_footer": True,
            "header_template": f"<div style='font-size: 10px; text-align: center; width: 100%;'>{title}</div>",
            "footer_template": "<div style='font-size: 10px; text-align: center; width: 100%;'>第 <span class='pageNumber'></span> 页 / 共 <span class='totalPages'></span> 页</div>"
        }
        
        await page.pdf(**pdf_options)
        
        print(f"PDF已生成: {output_path}")
        
        await browser.close()
        return output_path

def show_available_configs():
    """显示可用的配置选项"""
    print("可用的预设配置:")
    print("-" * 50)
    for key, config in PRESET_CONFIGS.items():
        print(f"{key:12} - {config['name']}")
        print(f"            浏览器: {config['viewport']['width']}x{config['viewport']['height']}")
        print(f"            PDF: {config['pdf_format']}, 横屏: {config['landscape']}, 缩放: {config['scale']}")
        print()

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python aippt_to_pdf_preprocess.py <PPT链接> [配置名称]")
        print("示例: python aippt_to_pdf_preprocess.py https://www.aippt.cn/share/xxx landscape")
        print()
        show_available_configs()
        return
    
    ppt_url = sys.argv[1]
    config_name = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    # 验证URL
    if not ppt_url.startswith("https://www.aippt.cn/share/"):
        print("❌ 请提供有效的aippt.cn分享链接")
        return
    
    # 验证配置
    if config_name not in PRESET_CONFIGS:
        print(f"❌ 未知的配置名称: {config_name}")
        print("可用的配置:", ", ".join(PRESET_CONFIGS.keys()))
        return
    
    try:
        output_path = await generate_pdf_from_aippt(ppt_url, config_name)
        print(f"\n✅ PDF生成成功！")
        print(f"📁 文件位置: {os.path.abspath(output_path)}")
        print(f"📄 文件名: {os.path.basename(output_path)}")
        
    except Exception as e:
        print(f"❌ 生成PDF时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
