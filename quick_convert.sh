#!/bin/bash
# aippt.cn PPT转PDF工具 - 快速使用脚本
# 使用方法: ./quick_convert.sh <PPT链接> [配置名称]

# 检查参数
if [ $# -lt 1 ]; then
    echo "使用方法: $0 <PPT链接> [配置名称]"
    echo ""
    echo "可用配置:"
    echo "  default      - 默认配置（A4竖屏）"
    echo "  landscape    - 横屏模式（A4横屏）"
    echo "  large        - 大尺寸模式（A3横屏）"
    echo "  compact      - 紧凑模式（A4竖屏）"
    echo "  presentation - 演示模式（A4横屏）"
    echo "  print        - 打印优化（A4竖屏）"
    echo ""
    echo "示例:"
    echo "  $0 https://www.aippt.cn/share/xxx landscape"
    echo "  $0 https://www.aippt.cn/share/xxx presentation"
    exit 1
fi

PPT_URL="$1"
CONFIG="${2:-default}"

# 检查URL格式
if [[ ! "$PPT_URL" =~ ^https://www\.aippt\.cn/share/ ]]; then
    echo "❌ 请提供有效的aippt.cn分享链接"
    exit 1
fi

# 进入脚本目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 激活虚拟环境并运行
echo "🚀 开始转换PPT为PDF..."
echo "📄 链接: $PPT_URL"
echo "⚙️  配置: $CONFIG"
echo ""

source venv/bin/activate
python aippt_to_pdf_preprocess.py "$PPT_URL" "$CONFIG"

echo ""
echo "✅ 转换完成！PDF文件已保存到: /Users/leiyang/Desktop/new/pdf/"

