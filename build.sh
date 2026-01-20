#!/bin/bash
# VSCode Projects Manager - Build Script for macOS/Linux

set -e  # 遇到错误立即退出

echo "========================================"
echo " VSCode Projects Manager - Build Script"
echo "========================================"
echo ""

# 检测操作系统
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="macos";;
    *)          echo "[错误] 不支持的操作系统: $OS_TYPE"; exit 1;;
esac

echo "检测到操作系统: $PLATFORM"
echo ""

# 检查 Python
echo "[1/4] 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python 3，请先安装 Python 3.11+"
    exit 1
fi

PYTHON_EXE=$(command -v python3)
echo "使用 Python: $PYTHON_EXE"
$PYTHON_EXE --version
echo ""

# 检查/安装 PyInstaller
echo "[2/4] 检查 PyInstaller..."
if ! $PYTHON_EXE -m pip show pyinstaller &> /dev/null; then
    echo "     正在安装 PyInstaller..."
    $PYTHON_EXE -m pip install pyinstaller --quiet
fi
echo ""

# 清理旧文件
echo "[3/4] 清理旧文件..."
rm -rf dist/$PLATFORM build/$PLATFORM vscode-projects 2>/dev/null || true
echo ""

# 编译
echo "[4/4] 正在编译 $PLATFORM 版本..."
cd "$(dirname "$0")"
$PYTHON_EXE -m PyInstaller \
    --onefile \
    --console \
    --name vscode-projects \
    --clean \
    --noconfirm \
    --distpath dist/$PLATFORM \
    --workpath build/$PLATFORM \
    vscode-projects.py

echo ""
echo "========================================"
echo " 编译结果"
echo "========================================"
echo ""
echo "$PLATFORM 可执行文件:"
echo "  $(pwd)/dist/$PLATFORM/vscode-projects"
echo ""

# 显示文件大小
if [ -f "dist/$PLATFORM/vscode-projects" ]; then
    FILE_SIZE=$(ls -lh dist/$PLATFORM/vscode-projects | awk '{print $5}')
    echo "文件大小: $FILE_SIZE"

    # 添加执行权限
    chmod +x dist/$PLATFORM/vscode-projects

    # 复制到根目录（可选）
    cp dist/$PLATFORM/vscode-projects .
    echo "已复制到: $(pwd)/vscode-projects"
fi

echo ""
echo "使用方法:"
echo "  ./vscode-projects        交互模式"
echo "  ./vscode-projects -l     列出项目"
echo "  ./vscode-projects -h     显示帮助"
echo ""
echo "✨ 编译完成!"
