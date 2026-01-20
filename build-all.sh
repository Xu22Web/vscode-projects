#!/bin/bash
# VSCode Projects Manager - 多平台构建脚本
# 在 macOS/Linux 上构建所有平台的版本（需要 Docker）

set -e

echo "=========================================="
echo " VSCode Projects Manager - 多平台构建"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION="1.0.0"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python 3"
    exit 1
fi

PYTHON_EXE=$(command -v python3)
echo "使用 Python: $PYTHON_EXE"
$PYTHON_EXE --version
echo ""

# 检查/安装 PyInstaller
echo "[1/3] 检查 PyInstaller..."
if ! $PYTHON_EXE -m pip show pyinstaller &> /dev/null; then
    echo "     正在安装 PyInstaller..."
    $PYTHON_EXE -m pip install pyinstaller --quiet
fi
echo ""

# 清理旧文件
echo "[2/3] 清理旧文件..."
rm -rf dist build vscode-projects 2>/dev/null || true
mkdir -p dist/releases
echo ""

# 编译当前平台
echo "[3/3] 编译当前平台版本..."
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
    Linux*)     PLATFORM="linux"; EXT="";;
    Darwin*)    PLATFORM="macos"; EXT="";;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows"; EXT=".exe";;
    *)          echo "[警告] 未知操作系统: $OS_TYPE，默认为 linux"; PLATFORM="linux"; EXT="";;
esac

echo "当前平台: $PLATFORM"
echo ""

# 执行编译
$PYTHON_EXE -m PyInstaller \
    --onefile \
    --console \
    --name vscode-projects \
    --clean \
    --noconfirm \
    --distpath dist/$PLATFORM \
    --workpath build/$PLATFORM \
    vscode-projects.py

# 生成发布包
if [ -f "dist/$PLATFORM/vscode-projects$EXT" ]; then
    echo ""
    echo "打包发布文件..."

    # 创建平台特定的压缩包
    cd dist/$PLATFORM

    if [ "$PLATFORM" = "windows" ]; then
        zip -q ../../dist/releases/vscode-projects-$VERSION-windows-x64.zip vscode-projects.exe
        echo "✓ 创建: vscode-projects-$VERSION-windows-x64.zip"
    elif [ "$PLATFORM" = "macos" ]; then
        tar -czf ../../dist/releases/vscode-projects-$VERSION-macos-x64.tar.gz vscode-projects
        echo "✓ 创建: vscode-projects-$VERSION-macos-x64.tar.gz"
    else
        tar -czf ../../dist/releases/vscode-projects-$VERSION-linux-x64.tar.gz vscode-projects
        echo "✓ 创建: vscode-projects-$VERSION-linux-x64.tar.gz"
    fi

    cd "$SCRIPT_DIR"
fi

echo ""
echo "=========================================="
echo " 编译完成"
echo "=========================================="
echo ""
echo "可执行文件:"
ls -lh dist/$PLATFORM/ 2>/dev/null || true
echo ""
echo "发布包:"
ls -lh dist/releases/ 2>/dev/null || true
echo ""
echo "✨ 构建成功!"
echo ""
echo "提示: 在其他平台上运行此脚本以生成对应平台的版本"
