#!/usr/bin/env python3
"""
使用Playwright生成PDF的脚本
从aippt.cn的PPT预览页面生成PDF文件
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def generate_pdf_from_aippt(url, output_path):
    """从aippt.cn生成PDF文件"""
    
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
            header_template="<div style='font-size: 10px; text-align: center; width: 100%;'>客服技能提升秘籍：转化率、客单价与服务态度</div>",
            footer_template="<div style='font-size: 10px; text-align: center; width: 100%;'>第 <span class='pageNumber'></span> 页 / 共 <span class='totalPages'></span> 页</div>"
        )
        
        print(f"PDF已生成: {output_path}")
        
        await browser.close()

async def main():
    """主函数"""
    # PPT链接
    ppt_url = "https://www.aippt.cn/share/2fxIYpUY1wc83C46fUrYzA"
    
    # 设置输出目录
    output_dir = "/Users/leiyang/Desktop/new/pdf"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"客服技能提升秘籍_{timestamp}.pdf"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        await generate_pdf_from_aippt(ppt_url, output_path)
        print(f"\n✅ PDF生成成功！")
        print(f"📁 文件位置: {output_path}")
        print(f"📄 文件名: {output_filename}")
        
    except Exception as e:
        print(f"❌ 生成PDF时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
