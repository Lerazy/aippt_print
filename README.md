# aippt.cn PPT转PDF工具

这个工具可以帮助您将aippt.cn的PPT预览页面转换为PDF文件，无需会员即可下载PPT内容。

## 功能特点

- ✅ 无需aippt.cn会员即可下载PPT
- ✅ 高质量PDF输出，保留原始格式和样式
- ✅ 自动添加页眉页脚
- ✅ 支持A4格式打印
- ✅ 自动生成时间戳文件名

## 安装要求

- Python 3.7+
- Playwright

## 安装步骤

1. 克隆或下载此项目
2. 创建虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate    # Windows
   ```

3. 安装依赖：
   ```bash
   pip install playwright
   playwright install chromium
   ```

## 使用方法

### 方法1：使用通用脚本
```bash
python aippt_to_pdf.py <PPT链接>
```

示例：
```bash
python aippt_to_pdf.py https://www.aippt.cn/share/2fxIYpUY1wc83C46fUrYzA
```

### 方法2：使用专用脚本
```bash
python generate_pdf.py
```

## 输出文件

- 文件名格式：`aippt_ppt_YYYYMMDD_HHMMSS.pdf`
- 文件位置：当前目录
- 文件大小：通常3-5MB（取决于PPT内容）

## 注意事项

1. 确保网络连接正常
2. PPT链接必须是有效的aippt.cn分享链接
3. 生成的PDF包含所有页面内容
4. 建议在生成PDF前确保页面完全加载

## 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'playwright'**
   - 解决：确保已激活虚拟环境并安装了playwright

2. **页面加载失败**
   - 解决：检查网络连接和URL有效性

3. **PDF生成失败**
   - 解决：确保有足够的磁盘空间和权限

## 技术说明

- 使用Playwright无头浏览器访问页面
- 自动等待页面完全加载
- 使用A4格式生成PDF
- 保留背景色和图片
- 添加页眉页脚信息

## 免责声明

此工具仅用于个人学习和研究目的。请遵守aippt.cn的使用条款和相关法律法规。

# aippt_print
# aippt_print
# aippt_print
