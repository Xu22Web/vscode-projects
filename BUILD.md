# 构建指南

本文档说明如何为不同平台构建 VSCode Projects Manager 的可执行文件。

## 📋 前置要求

### 必需环境

- **Python**: 3.11 或更高版本
  - 检查版本：`python --version` 或 `python3 --version`
  - 下载地址：[python.org](https://www.python.org/downloads/)
- **pip**: Python 包管理器（通常随 Python 安装）
  - 检查版本：`pip --version`
  - 升级 pip：`python -m pip install --upgrade pip`

### 自动安装的依赖

- **PyInstaller**: 用于打包 Python 程序为可执行文件
  - 构建脚本会自动检测并安装
  - 手动安装：`pip install pyinstaller`

### 推荐环境（可选）

- **虚拟环境**: 用于隔离构建环境
  ```bash
  # 创建虚拟环境
  python -m venv build_env

  # 激活虚拟环境
  # Windows
  build_env\Scripts\activate
  # macOS/Linux
  source build_env/bin/activate
  ```

- **磁盘空间**: 至少 500 MB 可用空间
- **内存**: 建议 2 GB 以上

## 🔨 构建方法

### Windows

使用 `build.bat` 脚本：

```batch
# 双击运行或在命令行中执行
build.bat
```

**输出位置：**
- `dist/windows/vscode-projects.exe`
- 自动复制到根目录：`vscode-projects.exe`

### macOS / Linux

使用 `build.sh` 脚本：

```bash
# 添加执行权限（首次运行需要）
chmod +x build.sh

# 运行构建脚本
./build.sh
```

**输出位置：**
- macOS: `dist/macos/vscode-projects`
- Linux: `dist/linux/vscode-projects`
- 自动复制到根目录：`vscode-projects`

### 多平台构建

使用 `build-all.sh` 脚本（推荐在 macOS/Linux 上运行）：

```bash
# 添加执行权限
chmod +x build-all.sh

# 构建并打包
./build-all.sh
```

**输出位置：**
- `dist/releases/vscode-projects-1.0.0-windows-x64.zip`
- `dist/releases/vscode-projects-1.0.0-macos-x64.tar.gz`
- `dist/releases/vscode-projects-1.0.0-linux-x64.tar.gz`

## 📦 手动构建

如果构建脚本不适用，可以手动构建：

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 构建可执行文件

**Windows:**
```batch
pyinstaller --onefile --console --name vscode-projects vscode-projects.py
```

**macOS/Linux:**
```bash
pyinstaller --onefile --console --name vscode-projects vscode-projects.py
```

### 3. 查找生成的文件

- Windows: `dist/vscode-projects.exe`
- macOS/Linux: `dist/vscode-projects`

## 🎯 构建选项说明

### PyInstaller 常用参数

- `--onefile`: 打包为单个可执行文件（推荐）
- `--console`: 控制台应用程序模式
- `--name`: 指定可执行文件名称
- `--clean`: 清理之前的构建缓存和临时文件
- `--noconfirm`: 覆盖输出目录时不询问确认
- `--distpath`: 指定输出目录（默认: dist/）
- `--workpath`: 指定临时工作目录（默认: build/）
- `--specpath`: 指定 spec 文件保存路径

### 高级选项

- `--upx-dir`: 指定 UPX 压缩工具路径（减小文件大小）
- `--add-data`: 添加数据文件到打包
- `--hidden-import`: 指定隐藏的导入模块
- `--exclude-module`: 排除不需要的模块
- `--icon`: 指定程序图标（.ico 或 .icns）

## 📄 Spec 文件说明

Spec 文件（`vscode-projects.spec`）是 PyInstaller 的配置文件，用于自定义构建过程。

### 当前配置

```python
# Analysis: 分析 Python 脚本的依赖
a = Analysis(
    ['vscode-projects.py'],  # 主程序
    pathex=[],               # 额外搜索路径
    binaries=[],             # 额外的二进制文件
    datas=[],                # 额外的数据文件
    hiddenimports=[],        # 隐藏导入
    excludes=[],             # 排除的模块
)

# EXE: 生成可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='vscode-projects',  # 可执行文件名
    debug=False,             # 调试模式
    console=True,            # 控制台模式
    upx=True,                # 使用 UPX 压缩
)
```

### 使用 Spec 文件构建

```bash
# 使用现有的 spec 文件
pyinstaller vscode-projects.spec

# 修改 spec 文件后重新构建
pyinstaller --clean vscode-projects.spec
```

### 何时需要修改 Spec 文件

- 添加数据文件（如图标、配置文件）
- 排除不需要的大型库
- 添加隐藏导入的模块
- 自定义图标或版本信息
- 需要更精细的控制

## 🔍 故障排除

### 问题 1: PyInstaller 未找到

**解决方案:**
```bash
python -m pip install --upgrade pyinstaller
```

### 问题 2: 权限错误（Linux/macOS）

**解决方案:**
```bash
chmod +x build.sh
chmod +x build-all.sh
```

### 问题 3: 编译后文件太大

**原因:** PyInstaller 会打包所有依赖

**优化方案:**
```bash
# 使用虚拟环境构建（仅安装必要依赖）
python -m venv build_env
source build_env/bin/activate  # Linux/macOS
# build_env\Scripts\activate   # Windows

pip install pyinstaller
pyinstaller --onefile --console vscode-projects.py
```

### 问题 4: Windows Defender 误报

**原因:** PyInstaller 生成的 exe 可能被杀毒软件误报

**解决方案:**
- 添加信任/白名单
- 使用代码签名证书签名 exe 文件

### 问题 5: 导入错误（ModuleNotFoundError）

**症状:** 运行可执行文件时提示缺少模块

**解决方案:**
```bash
# 在 spec 文件中添加隐藏导入
hiddenimports=['missing_module_name']

# 或使用命令行
pyinstaller --hidden-import=missing_module_name vscode-projects.py
```

### 问题 6: 编译速度慢

**解决方案:**
```bash
# 使用虚拟环境（只安装必要的依赖）
python -m venv build_env
source build_env/bin/activate  # Linux/macOS
build_env\Scripts\activate      # Windows

# 仅安装 PyInstaller
pip install pyinstaller

# 然后构建
pyinstaller vscode-projects.spec
```

### 问题 7: macOS "无法打开，因为无法验证开发者"

**解决方案:**
```bash
# 允许运行未签名的应用
xattr -cr dist/vscode-projects

# 或在系统偏好设置中允许
# 系统偏好设置 -> 安全性与隐私 -> 通用 -> 仍要打开
```

### 问题 8: Linux 缺少 GLIBC 版本

**症状:** 提示 GLIBC 版本不匹配

**解决方案:**
- 在目标系统相同的 Linux 发行版上构建
- 或使用 Docker 构建兼容性更好的版本

## 📊 构建性能

典型构建时间和文件大小：

| 平台 | 构建时间 | 文件大小 |
|------|---------|---------|
| Windows | ~30秒 | ~10-15 MB |
| macOS | ~30秒 | ~10-15 MB |
| Linux | ~30秒 | ~10-15 MB |

## 🚀 发布流程

1. **更新版本号**
   - 在 `vscode-projects.py` 中更新版本号
   - 更新 `CHANGELOG.md`
   - 更新 `build-all.sh` 中的 VERSION

2. **构建所有平台**
   ```bash
   # 在 Windows 上
   build.bat

   # 在 macOS 上
   ./build.sh

   # 在 Linux 上
   ./build.sh
   ```

3. **测试可执行文件**
   - 在各平台上测试基本功能
   - 验证命令行参数
   - 检查兼容性

4. **创建发布包**
   ```bash
   ./build-all.sh
   ```

5. **上传到 GitHub Releases**
   - 创建新的 Release (v1.0.0)
   - 上传各平台的压缩包
   - 附上 Release Notes

## 📝 注意事项

1. **跨平台构建限制**
   - Windows exe 只能在 Windows 上构建
   - macOS 二进制文件只能在 macOS 上构建
   - Linux 二进制文件只能在 Linux 上构建

2. **依赖检查**
   - 确保所有依赖都正确安装
   - 标准库不需要额外安装

3. **代码签名**（可选）
   - Windows: 使用 SignTool
   - macOS: 使用 codesign
   - 提高用户信任度

4. **CI/CD 集成**
   - 可以使用 GitHub Actions 自动构建
   - 下面是配置示例

## 🔄 CI/CD 集成

### GitHub Actions 示例

创建 `.github/workflows/build.yml`：

```yaml
name: Build Multi-Platform

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyinstaller
      - name: Build Windows
        run: .\build.bat
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: vscode-projects-windows
          path: dist/windows/vscode-projects.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyinstaller
      - name: Build macOS
        run: |
          chmod +x build.sh
          ./build.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: vscode-projects-macos
          path: dist/macos/vscode-projects

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyinstaller
      - name: Build Linux
        run: |
          chmod +x build.sh
          ./build.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: vscode-projects-linux
          path: dist/linux/vscode-projects

  release:
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    steps:
      - uses: actions/download-artifact@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            vscode-projects-windows/vscode-projects.exe
            vscode-projects-macos/vscode-projects
            vscode-projects-linux/vscode-projects
```

### 其他 CI/CD 平台

**GitLab CI (.gitlab-ci.yml):**
```yaml
stages:
  - build

build:linux:
  stage: build
  image: python:3.11
  script:
    - pip install pyinstaller
    - pyinstaller vscode-projects.spec
  artifacts:
    paths:
      - dist/
```

**Jenkins Pipeline:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'pip install pyinstaller'
                sh 'pyinstaller vscode-projects.spec'
            }
        }
    }
}
```

## 🔗 相关资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [Python 打包指南](https://packaging.python.org/)
- [GitHub Releases 文档](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

如有问题，请提交 [Issue](https://github.com/Xu22Web/vscode-projects/issues)。
