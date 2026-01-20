# VSCode Recent Projects Manager

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一款功能强大的 VSCode 最近项目管理器，采用 fzf 风格的交互式界面，支持跨平台使用。

## 🎬 演示界面

```plaintext
📁 VSCode Projects  1/23

> [✓] vscode-projects                d:/Project
  [ ] my-web-app                    c:/Users/User/Documents
  [ ] data-analysis [无效]          d:/Project
  [ ] mini-food-ordering            d:/Project
  [ ] web-merchant-backend          d:/Project
  [ ] web-merchant-backend [WSL: Ubuntu] /home/user/projects
  [ ] app-merchant-backend [WSL: Ubuntu] /home/user/projects
  [ ] pc-display-system [WSL: Ubuntu] /home/user/projects
  ...

路径: d:/Project/vscode-projects

↑↓移动 Space选择 a全选 | Enter打开 n新窗口 w工作区 y复制路径 o资源管理器 d删除 u撤销 /搜索 q退出
```

## ✨ 特性

- 🎨 **优雅的 fzf 风格界面** - 流畅的交互体验，支持实时过滤搜索
- 🖱️ **鼠标支持** - 可以使用鼠标点击选择项目（需终端支持）
- 🔍 **智能搜索** - 支持项目名称、路径模糊搜索
- 🌈 **彩色显示** - 项目类型、路径、标签使用不同颜色标识
- 🗑️ **项目管理** - 支持删除项目、撤销删除
- 📋 **快捷操作** - 复制路径、在文件管理器中打开
- 🌐 **跨平台** - Windows、macOS、Linux、WSL 完美支持
- 🔌 **远程项目** - 支持 SSH、WSL、Dev Container 等远程项目
- ⚡ **独立可执行文件** - 可编译为单文件，无需 Python 环境

## 📦 安装

### 方式一：从源码运行

```bash
# 克隆项目
git clone https://github.com/Xu22Web/vscode-projects.git
cd vscode-projects

# 直接运行（需要 Python 3.11+）
python vscode-projects.py
```

### 方式二：编译为可执行文件

**详细构建指南请参阅 [BUILD.md](BUILD.md)**

#### Windows

```batch
# 运行编译脚本
build.bat

# 编译完成后，可执行文件位于 dist/windows/ 目录
dist\windows\vscode-projects.exe

# 或者手动编译
pip install pyinstaller
pyinstaller --onefile --console --name vscode-projects vscode-projects.py
```

#### macOS / Linux

```bash
# 添加执行权限
chmod +x build.sh

# 运行编译脚本
./build.sh

# 编译完成后运行
./dist/macos/vscode-projects  # macOS
./dist/linux/vscode-projects  # Linux

# 或者手动编译
pip install pyinstaller
pyinstaller --onefile --console --name vscode-projects vscode-projects.py
./dist/vscode-projects
```

#### 多平台发布包

```bash
# 使用多平台构建脚本
chmod +x build-all.sh
./build-all.sh

# 生成的发布包位于 dist/releases/
# - vscode-projects-1.0.0-windows-x64.zip
# - vscode-projects-1.0.0-macos-x64.tar.gz
# - vscode-projects-1.0.0-linux-x64.tar.gz
```

### 方式三：下载预编译版本

从 [Releases](https://github.com/Xu22Web/vscode-projects/releases) 页面下载最新版本：

- Windows: `vscode-projects-x.x.x-windows-x64.zip`
- macOS: `vscode-projects-x.x.x-macos-x64.tar.gz`
- Linux: `vscode-projects-x.x.x-linux-x64.tar.gz`

下载后解压即可使用，无需安装 Python 环境。

## 🚀 使用方法

### 基本用法

```bash
# 交互模式（默认）
vscode-projects

# 列出所有项目
vscode-projects -l
vscode-projects --list

# 显示帮助
vscode-projects -h
vscode-projects --help

# 显示版本
vscode-projects -v
vscode-projects --version
```

### 高级用法

```bash
# 指定自定义数据库路径
vscode-projects --db "/path/to/state.vscdb"

# 指定 VSCode 可执行文件路径
vscode-projects --code "/path/to/code"

# 组合使用
vscode-projects --db "/custom/path/state.vscdb" --code "code-insiders"
```

## ⌨️ 快捷键

### 交互模式快捷键

| 快捷键 | 功能 |
|--------|------|
| `↑` / `↓` | 上下移动光标 |
| `PgUp` / `PgDn` | 上下翻页 |
| `Home` / `End` | 跳转到第一项/最后一项 |
| `Space` | 选中/取消选中当前项 |
| `a` | 全选/取消全选 |
| `Enter` | 单选：当前窗口打开并退出；多选：新窗口打开并退出 |
| `n` | 在新窗口打开（不退出程序） |
| `w` | 多选：作为工作区打开；单选：新窗口打开 |
| `o` | 在文件管理器中打开 |
| `y` | 复制项目路径到剪贴板 |
| `d` | 删除选中的项目（需确认） |
| `u` | 撤销上次删除操作 |
| `r` | 刷新项目列表 |
| `/` | 进入搜索模式 |
| `Ctrl+C` / `Esc` / `q` | 退出程序 |

### 鼠标操作

- **左键单击** - 选择项目
- **左键双击** - 打开项目
- **鼠标滚轮** - 上下滚动列表

## 📊 界面说明

```
┌─────────────────────────────────────────────────────────────┐
│  VSCode Recent Projects (12 projects)                       │
├─────────────────────────────────────────────────────────────┤
│ > search query here                                         │
├─────────────────────────────────────────────────────────────┤
│ ► 📁 project-name              /path/to/project      [tag]  │
│   📄 file.py                   /path/to/file.py             │
│   🔧 workspace.code-workspace  /path/to/workspace           │
│   🌐 remote-project [SSH]      ssh://host/path              │
└─────────────────────────────────────────────────────────────┘
```

### 图标说明

- `📁` - 文件夹项目
- `📄` - 单文件项目
- `🔧` - 工作区项目
- `🌐` - 远程项目
- `🗑️` - 已标记为无效的项目

### 颜色标识

- **绿色** - 项目名称
- **蓝色** - 文件路径
- **黄色** - 标签
- **灰色** - 远程类型标识
- **删除线** - 已标记删除的项目

## 🛠️ 数据库位置

程序会自动检测 VSCode 数据库位置：

### Windows
```
%APPDATA%\Code\User\globalStorage\state.vscdb
```

### macOS
```
~/Library/Application Support/Code/User/globalStorage/state.vscdb
```

### Linux
```
~/.config/Code/User/globalStorage/state.vscdb
```

### WSL
```
/mnt/c/Users/{username}/AppData/Roaming/Code/User/globalStorage/state.vscdb
```

## 🌐 远程项目支持

支持以下类型的远程项目：

- **SSH Remote** - `ssh://hostname/path`
- **WSL** - `wsl+Ubuntu`, `wsl+Debian` 等
- **Dev Container** - `dev-container+...`
- **Codespaces** - `codespaces+...`
- **vscode-remote** - 其他远程协议

## 📝 项目类型

- **Folder** - 普通文件夹项目
- **File** - 单个文件
- **Workspace** - VSCode 工作区（`.code-workspace` 文件）

## 🔧 系统要求

### 运行源码时

- **Python**: 3.11 或更高版本
- **pip**: Python 包管理器
- **操作系统**:
  - Windows 10/11
  - macOS 10.14+
  - Linux（任何主流发行版）
  - WSL 1/2

### 使用预编译版本时

- **无需 Python 环境**
- **操作系统**:
  - Windows 10/11（64位）
  - macOS 10.14+（64位）
  - Linux（64位，GLIBC 2.27+）
- **终端**: 支持 ANSI 颜色的现代终端
  - Windows Terminal（推荐）
  - PowerShell 7+
  - iTerm2 / Terminal.app（macOS）
  - GNOME Terminal / Konsole（Linux）

### 构建可执行文件时

- **Python**: 3.11 或更高版本
- **PyInstaller**: 自动安装
- **磁盘空间**: 至少 500 MB
- **内存**: 建议 2 GB 以上

详细的构建要求和说明请参阅 [BUILD.md](BUILD.md)

## 🎯 应用场景

- 快速切换多个项目
- 管理大量 VSCode 工作区
- 清理无效的历史项目
- 查找最近打开的文件
- 管理远程开发项目

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详细的贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)

### 快速开始贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 贡献类型

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔨 提交代码修复
- 🌐 添加国际化支持
- 🧪 编写测试
- 🏗️ 改进构建脚本

### 文档结构

- [README.md](README.md) - 项目主文档
- [BUILD.md](BUILD.md) - 构建指南
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [USAGE.md](USAGE.md) - 详细使用说明
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日志

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 灵感来源于 [fzf](https://github.com/junegunn/fzf)
- 感谢 VSCode 团队提供的优秀编辑器

## 📞 联系方式

如有问题或建议，请：
- 提交 [Issue](https://github.com/Xu22Web/vscode-projects/issues)
- 参与 [讨论](https://github.com/Xu22Web/vscode-projects/discussions)

## 🔄 更新日志

### v1.0.0（2026-01-20）

首次发布！🎉

**核心功能：**
- ✨ fzf 风格的交互式界面
- 🔍 智能搜索和实时过滤
- 🖱️ 鼠标支持（单击/双击/滚轮）
- 🌐 跨平台支持（Windows/macOS/Linux/WSL）
- 🔌 远程项目支持（SSH/WSL/Dev Container）
- 📋 丰富的快捷键操作
- 🎨 彩色界面显示
- 🗑️ 项目管理功能（删除/撤销）

**命令行参数：**
- `--db` 自定义数据库路径
- `--code` 自定义 VSCode 可执行文件路径
- `--list` 列表模式
- `--help` 帮助信息
- `--version` 版本信息

---

⭐ 如果这个项目对你有帮助，请给个 Star！
