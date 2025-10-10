#!/usr/bin/env python3
"""
aippt.cn PPT转PDF工具
使用方法: python aippt_to_pdf.py <PPT链接>
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright
from datetime import datetime
import re

async def generate_pdf_from_aippt(url, output_path=None):
    """从aippt.cn生成PDF文件"""
    
    if not output_path:
        # 设置默认输出目录
        output_dir = "/Users/leiyang/Desktop/new/pdf"
        os.makedirs(output_dir, exist_ok=True)
        
        # 从URL提取文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"aippt_ppt_{timestamp}.pdf")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置视口大小
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"正在访问: {url}")
        
        # 访问页面
        await page.goto(url, wait_until="networkidle")
        
        # 等待页面完全加载
        await page.wait_for_timeout(5000)
        
        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")
        
        print("页面加载完成，开始生成PDF...")
        
        # 生成PDF
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={
                "top": "1cm",
                "right": "1cm", 
                "bottom": "1cm",
                "left": "1cm"
            },
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template=f"<div style='font-size: 10px; text-align: center; width: 100%;'>{title}</div>",
            footer_template="<div style='font-size: 10px; text-align: center; width: 100%;'>第 <span class='pageNumber'></span> 页 / 共 <span class='totalPages'></span> 页</div>"
        )
        
        print(f"PDF已生成: {output_path}")
        
        await browser.close()
        return output_path

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python aippt_to_pdf.py <PPT链接>")
        print("示例: python aippt_to_pdf.py https://www.aippt.cn/share/2fxIYpUY1wc83C46fUrYzA")
        return
    
    ppt_url = sys.argv[1]
    
    # 验证URL
    if not ppt_url.startswith("https://www.aippt.cn/share/"):
        print("❌ 请提供有效的aippt.cn分享链接")
        return
    
    try:
        output_path = await generate_pdf_from_aippt(ppt_url)
        print(f"\n✅ PDF生成成功！")
        print(f"📁 文件位置: {os.path.abspath(output_path)}")
        print(f"📄 文件名: {os.path.basename(output_path)}")
        
    except Exception as e:
        print(f"❌ 生成PDF时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
