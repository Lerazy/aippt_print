#!/usr/bin/env python3
"""
aippt.cn PPT转PDF工具 - 配置文件版
支持从JSON配置文件读取所有设置，方便调试
使用方法: python aippt_to_pdf_config.py <PPT链接> [配置名称]
"""

import asyncio
import sys
import os
import json
from playwright.async_api import async_playwright
from datetime import datetime
import re
from PyPDF2 import PdfMerger
from pypdf import PdfReader, PdfWriter

def crop_pdf_page(input_path, output_path, crop_margins):
    """
    裁剪PDF页面
    crop_margins: {"top": 0, "right": 0, "bottom": 0, "left": 0}
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            # 获取页面尺寸
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # 计算裁剪后的尺寸
            new_width = page_width - crop_margins["left"] - crop_margins["right"]
            new_height = page_height - crop_margins["top"] - crop_margins["bottom"]
            
            # 设置新的页面尺寸
            page.mediabox.lower_left = (crop_margins["left"], crop_margins["bottom"])
            page.mediabox.upper_right = (page_width - crop_margins["right"], page_height - crop_margins["top"])
            
            writer.add_page(page)
        
        # 保存裁剪后的PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    except Exception as e:
        print(f"❌ PDF裁剪失败: {e}")
        return False

class PDFConfigManager:
    """PDF配置管理器"""
    
    def __init__(self, config_file="pdf_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 已加载配置文件: {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {self.config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            sys.exit(1)
    
    def get_pdf_config(self, config_name="default"):
        """获取PDF配置"""
        pdf_configs = self.config.get("pdf_configs", {})
        if config_name not in pdf_configs:
            print(f"❌ 未知的配置名称: {config_name}")
            print("可用的配置:", ", ".join(pdf_configs.keys()))
            sys.exit(1)
        return pdf_configs[config_name]
    
    def get_preprocess_settings(self):
        """获取预处理设置"""
        return self.config.get("preprocess_settings", {})
    
    def get_browser_settings(self):
        """获取浏览器设置"""
        return self.config.get("browser_settings", {})
    
    def get_output_settings(self):
        """获取输出设置"""
        return self.config.get("output_settings", {})
    
    def get_debug_settings(self):
        """获取调试设置"""
        return self.config.get("debug_settings", {})

async def preprocess_page(page, config_manager):
    """预处理页面：删除侧边栏、调整缩放、删除工具栏"""
    
    preprocess_settings = config_manager.get_preprocess_settings()
    
    if not preprocess_settings.get("enable_preprocess", True):
        print("⚠️  预处理已禁用")
        return
    
    print("开始预处理页面...")
    
    steps = preprocess_settings.get("steps", {})
    
    # 第一步：删除侧边栏
    sidebar_config = steps.get("remove_sidebar", {})
    if sidebar_config.get("enabled", True):
        try:
            print("🔍 正在查找侧边栏元素...")
            await page.wait_for_timeout(1000)
            
            selector = sidebar_config.get("selector", ".main-preview-aside")
            aside_element = await page.query_selector(selector)
            
            if aside_element:
                await aside_element.evaluate('element => element.remove()')
                print(f"✅ 已删除侧边栏 ({selector})")
                
                wait_after = sidebar_config.get("wait_after", 2000)
                await page.wait_for_timeout(wait_after)
            else:
                print(f"⚠️  未找到侧边栏元素 ({selector})")
        except Exception as e:
            print(f"❌ 删除侧边栏失败: {e}")
    
    # 第二步：调整缩放比例
    zoom_config = steps.get("adjust_zoom", {})
    if zoom_config.get("enabled", True):
        try:
            print("🔍 开始调整缩放比例...")
            await page.wait_for_timeout(1000)
            
            # 找到缩放按钮和显示元素
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
                zoom_out_target = zoom_config.get("zoom_out_target", 10)
                zoom_in_target = zoom_config.get("zoom_in_target", 170)
                click_delay = zoom_config.get("click_delay", 800)
                wait_after_target = zoom_config.get("wait_after_target", 2000)
                
                # 先缩小到目标值
                print(f"📉 开始缩小到{zoom_out_target}%...")
                max_attempts = 50
                attempts = 0
                
                while attempts < max_attempts:
                    current_scale_text = await scale_display.text_content()
                    current_scale = int(re.findall(r'\d+', current_scale_text)[0])
                    
                    if current_scale <= zoom_out_target:
                        print(f"✅ 缩放已调整到{zoom_out_target}%或以下")
                        await page.wait_for_timeout(wait_after_target)
                        break
                    
                    await zoom_out_btn.click()
                    await page.wait_for_timeout(100)  # 进一步减少等待时间
                    attempts += 1
                
                # 再放大到目标值
                print(f"📈 开始放大到{zoom_in_target}%...")
                attempts = 0
                while attempts < max_attempts:
                    current_scale_text = await scale_display.text_content()
                    current_scale = int(re.findall(r'\d+', current_scale_text)[0])
                    
                    if current_scale >= zoom_in_target:
                        print(f"✅ 缩放已调整到{zoom_in_target}%")
                        await page.wait_for_timeout(wait_after_target)
                        break
                    
                    await zoom_in_btn.click()
                    await page.wait_for_timeout(100)  # 进一步减少等待时间
                    attempts += 1
                    
            else:
                print("⚠️  未找到缩放控制元素")
                
        except Exception as e:
            print(f"❌ 调整缩放失败: {e}")
    
    # 第三步：删除工具栏
    toolbar_config = steps.get("remove_toolbar", {})
    if toolbar_config.get("enabled", True):
        try:
            print("🔍 正在查找工具栏元素...")
            await page.wait_for_timeout(1000)
            
            selector = toolbar_config.get("selector", ".sharepreview-toolkit")
            toolkit_element = await page.query_selector(selector)
            
            if toolkit_element:
                await toolkit_element.evaluate('element => element.remove()')
                print(f"✅ 已删除工具栏 ({selector})")
                
                wait_after = toolbar_config.get("wait_after", 2000)
                await page.wait_for_timeout(wait_after)
            else:
                print(f"⚠️  未找到工具栏元素 ({selector})")
        except Exception as e:
            print(f"❌ 删除工具栏失败: {e}")
    
    print("页面预处理完成！")

async def generate_pdf_from_aippt(url, config_manager, config_name="default"):
    """从aippt.cn生成PDF文件 - 配置文件版（支持多页幻灯片）"""
    
    # 获取配置
    pdf_config = config_manager.get_pdf_config(config_name)
    browser_settings = config_manager.get_browser_settings()
    output_settings = config_manager.get_output_settings()
    debug_settings = config_manager.get_debug_settings()
    
    print(f"使用配置: {pdf_config['name']}")
    print(f"浏览器大小: {pdf_config['viewport']['width']}x{pdf_config['viewport']['height']}")
    print(f"PDF格式: {pdf_config['pdf_format']}, 横屏: {pdf_config['landscape']}, 缩放: {pdf_config['scale']}")
    
    # 生成输出路径
    output_dir = output_settings.get("output_dir", "/Users/leiyang/Desktop/new/pdf")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp_format = output_settings.get("timestamp_format", "%Y%m%d_%H%M%S")
    timestamp = datetime.now().strftime(timestamp_format)
    
    # 修改文件名模板，支持多页和自定义标题
    filename_template = output_settings.get("filename_template", "{title}.pdf")
    print(f"📝 文件名模板: {filename_template}")
    
    async with async_playwright() as p:
        # 启动浏览器
        headless = browser_settings.get("headless", True)
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        # 设置视口大小
        await page.set_viewport_size(pdf_config["viewport"])
        
        print(f"正在访问: {url}")
        
        # 访问页面 - 优化加载速度
        print(f"🌐 正在加载页面...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)  # 减少等待时间
        
        # 获取PPT标题
        try:
            title_element = await page.query_selector('.sharepreview-header-workname-text')
            if title_element:
                title = await title_element.inner_text()
                print(f"PPT标题: {title}")
            else:
                title = await page.title()
                print(f"使用页面标题: {title}")
        except Exception as e:
            title = await page.title()
            print(f"获取PPT标题失败，使用页面标题: {title}")
        
        # 清理标题，移除不适合文件名的字符
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        clean_title = clean_title.strip()
        
        # 立即查找幻灯片列表（在预处理之前）
        print("🔍 正在查找幻灯片列表...")
        
        slide_list = await page.query_selector('.slide-list-root')
        if not slide_list:
            print("⚠️  未找到幻灯片列表，将生成单页PDF")
            total_slides = 1
            is_multi_page = False
            slide_buttons = []
        else:
            # 获取幻灯片数量并保存
            slide_items = await slide_list.query_selector_all('> *')
            total_slides = len(slide_items)
            print(f"✅ 找到幻灯片列表，共 {total_slides} 页")
            
            # 查找幻灯片点击元素（.slide-page 元素）并保存
            slide_buttons = await slide_list.query_selector_all('.slide-page')
            
            if not slide_buttons:
                print("⚠️  未找到幻灯片按钮，将生成单页PDF")
                total_slides = 1
                is_multi_page = False
            else:
                print(f"✅ 找到 {len(slide_buttons)} 个幻灯片按钮，将逐页生成PDF")
                is_multi_page = True
                
            # 简化幻灯片按钮处理，直接使用序号
            print(f"📝 检测到 {total_slides} 页幻灯片")
        
        # 预处理页面
        await preprocess_page(page, config_manager)
        
        # 等待预处理完成 - 减少等待时间
        await page.wait_for_timeout(1000)
        
        # 根据检测结果生成PDF
        if not is_multi_page:
            # 生成单页PDF
            filename = filename_template.format(title=clean_title)
            output_path = os.path.join(output_dir, filename)
            
            # 应用缩放（通过CSS）
            if pdf_config["scale"] != 1.0:
                await page.add_style_tag(content=f"""
                    body {{
                        transform: scale({pdf_config['scale']});
                        transform-origin: top left;
                        width: {100/pdf_config['scale']}%;
                        height: {100/pdf_config['scale']}%;
                    }}
                """)
            
            print("开始生成单页PDF...")
            
            # 生成PDF
            pdf_options = {
                "path": output_path,
                "format": pdf_config["pdf_format"],
                "landscape": pdf_config["landscape"],
                "print_background": pdf_config.get("print_background", True),
                "margin": pdf_config["margin"],
                "prefer_css_page_size": pdf_config.get("prefer_css_page_size", True),
                "display_header_footer": pdf_config.get("display_header_footer", True),
                "header_template": f"<div style='font-size: 10px; text-align: center; width: 100%;'>{title}</div>",
                "footer_template": "<div style='font-size: 10px; text-align: center; width: 100%;'>第 <span class='pageNumber'></span> 页 / 共 <span class='totalPages'></span> 页</div>"
            }
            
            await page.pdf(**pdf_options)
            print(f"✅ 单页PDF已生成: {output_path}")
            
        else:
            # 逐页生成PDF
            generated_files = []
            
            for page_num in range(1, total_slides + 1):
                print(f"\n📄 正在生成第 {page_num} 页...")
                print(f"✅ 当前是第 {page_num} 页")
                
                # 应用缩放（通过CSS）
                if pdf_config["scale"] != 1.0:
                    await page.add_style_tag(content=f"""
                        body {{
                            transform: scale({pdf_config['scale']});
                            transform-origin: top left;
                            width: {100/pdf_config['scale']}%;
                            height: {100/pdf_config['scale']}%;
                        }}
                    """)
                
                # 生成当前页的PDF
                if total_slides > 1:
                    # 多页时添加页面编号
                    filename = f"{clean_title}_第{page_num}页.pdf"
                else:
                    # 单页时直接使用标题
                    filename = filename_template.format(title=clean_title)
                output_path = os.path.join(output_dir, filename)
                print(f"📄 生成文件: {filename}")
                
                pdf_options = {
                    "path": output_path,
                    "format": pdf_config["pdf_format"],
                    "landscape": pdf_config["landscape"],
                    "print_background": pdf_config.get("print_background", True),
                    "margin": pdf_config["margin"],
                    "prefer_css_page_size": pdf_config.get("prefer_css_page_size", True),
                    "display_header_footer": pdf_config.get("display_header_footer", True),
                    "header_template": f"<div style='font-size: 10px; text-align: center; width: 100%;'>{title} - 第{page_num}页</div>",
                    "footer_template": f"<div style='font-size: 10px; text-align: center; width: 100%;'>第 {page_num} 页 / 共 {total_slides} 页</div>"
                }
                
                await page.pdf(**pdf_options)
                print(f"✅ 第 {page_num} 页PDF已生成: {output_path}")
                
                # 应用PDF裁剪
                crop_settings = config_manager.config.get("crop_settings", {})
                if crop_settings.get("enabled", False):
                    crop_margins = crop_settings.get("crop_margins", {"top": 0, "right": 0, "bottom": 0, "left": 0})
                    if any(crop_margins.values()):  # 如果有任何边距不为0
                        cropped_path = output_path.replace('.pdf', '_cropped.pdf')
                        if crop_pdf_page(output_path, cropped_path, crop_margins):
                            # 删除原文件，使用裁剪后的文件
                            os.remove(output_path)
                            os.rename(cropped_path, output_path)
                            print(f"✂️ 第 {page_num} 页PDF已裁剪")
                        else:
                            print(f"⚠️ 第 {page_num} 页PDF裁剪失败，使用原文件")
                
                generated_files.append(output_path)
                
                # 如果不是最后一页，按键盘下键切换到下一张
                if page_num < total_slides:
                    print(f"⬇️ 按键盘下键切换到第 {page_num + 1} 页...")
                    await page.keyboard.press('ArrowDown')
                    await page.wait_for_timeout(500)  # 减少页面切换等待时间
            
            print(f"\n🎉 共生成 {len(generated_files)} 页PDF")
            for i, file_path in enumerate(generated_files, 1):
                print(f"  {i}. {os.path.basename(file_path)}")
            
            # 合并所有PDF页面
            if len(generated_files) > 1:
                print(f"\n📚 正在合并 {len(generated_files)} 页PDF...")
                merged_filename = f"{clean_title}.pdf"
                merged_path = os.path.join(output_dir, merged_filename)
                
                merger = PdfMerger()
                for file_path in generated_files:
                    merger.append(file_path)
                
                merger.write(merged_path)
                merger.close()
                
                print(f"✅ PDF合并完成: {merged_filename}")
                
                # 删除单独的页面文件
                print("🗑️ 正在删除单独的页面文件...")
                for file_path in generated_files:
                    try:
                        os.remove(file_path)
                        print(f"  ✅ 已删除: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"  ⚠️ 删除失败: {os.path.basename(file_path)} - {e}")
                
                output_path = merged_path
                print(f"📁 最终文件: {merged_filename}")
            else:
                # 只有一页，直接使用原文件
                output_path = generated_files[0]
        
        await browser.close()
        
        # 自动打开第一个PDF文件
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", output_path])
                print("📖 PDF已自动打开，您可以使用键盘方向键浏览页面")
            elif system == "Windows":
                os.startfile(output_path)
                print("📖 PDF已自动打开，您可以使用键盘方向键浏览页面")
            elif system == "Linux":
                subprocess.run(["xdg-open", output_path])
                print("📖 PDF已自动打开，您可以使用键盘方向键浏览页面")
            else:
                print(f"📖 请手动打开PDF文件: {output_path}")
        except Exception as e:
            print(f"⚠️  无法自动打开PDF: {e}")
            print(f"📖 请手动打开PDF文件: {output_path}")
        
        return output_path

def show_available_configs(config_manager):
    """显示可用的配置选项"""
    pdf_configs = config_manager.config.get("pdf_configs", {})
    print("可用的预设配置:")
    print("-" * 50)
    for key, config in pdf_configs.items():
        print(f"{key:12} - {config['name']}")
        print(f"            浏览器: {config['viewport']['width']}x{config['viewport']['height']}")
        print(f"            PDF: {config['pdf_format']}, 横屏: {config['landscape']}, 缩放: {config['scale']}")
        print()

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python aippt_to_pdf_config.py <PPT链接> [配置名称]")
        print("示例: python aippt_to_pdf_config.py https://www.aippt.cn/share/xxx landscape")
        print()
        
        # 显示可用配置
        config_manager = PDFConfigManager()
        show_available_configs(config_manager)
        return
    
    ppt_url = sys.argv[1]
    config_name = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    # 验证URL
    if not ppt_url.startswith("https://www.aippt.cn/share/"):
        print("❌ 请提供有效的aippt.cn分享链接")
        return
    
    try:
        # 创建配置管理器
        config_manager = PDFConfigManager()
        
        # 生成PDF
        output_path = await generate_pdf_from_aippt(ppt_url, config_manager, config_name)
        
        print(f"\n✅ PDF生成成功！")
        print(f"📁 文件位置: {os.path.abspath(output_path)}")
        print(f"📄 文件名: {os.path.basename(output_path)}")
        
    except Exception as e:
        print(f"❌ 生成PDF时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

