# 快速开始

这是 VSCode Recent Projects Manager 的快速入门指南。

## ⚡ 5 分钟快速开始

### 步骤 1: 获取代码

```bash
git clone https://github.com/Xu22Web/vscode-projects.git
cd vscode-projects
```

### 步骤 2: 运行程序

#### 直接运行（需要 Python 3.11+）

```bash
python vscode-projects.py
```

#### 或者编译为可执行文件

**Windows:**
```batch
build.bat
dist\vscode-projects.exe
```

**macOS/Linux:**
```bash
pip install pyinstaller
pyinstaller --onefile --console vscode-projects.py
./dist/vscode-projects
```

### 步骤 3: 使用程序

程序启动后，你会看到项目列表界面：

```plaintext
📁 VSCode Projects  1/23

> [✓] vscode-projects                d:/Project
  [ ] my-web-app                    c:/Users/User/Documents
  [ ] mini-food-ordering            d:/Project
  [ ] web-merchant-backend [WSL: Ubuntu] /home/user/projects
  ...

路径: d:/Project/vscode-projects

↑↓移动 Space选择 | Enter打开 n新窗口 y复制 o资源管理器 d删除 u撤销 q退出
```

**基本操作：**
1. 使用 `↑` `↓` 键选择项目
2. 按 `Enter` 打开项目
3. 按 `Ctrl+C` 或 `q` 退出

就这么简单！🎉

## 🎯 常用操作

### 搜索项目

在搜索框中输入关键词即可过滤：

- 输入项目名
- 输入路径
- 输入标签

### 快捷键

| 按键 | 功能 |
|------|------|
| `↑` `↓` | 移动选择 |
| `Space` | 选中/取消选中 |
| `a` | 全选/取消全选 |
| `Enter` | 单选：当前窗口打开并退出；多选：新窗口打开并退出 |
| `n` | 新窗口打开（不退出） |
| `w` | 多选：作为工作区打开；单选：新窗口打开 |
| `y` | 复制路径 |
| `o` | 资源管理器打开 |
| `d` | 删除项目（需确认） |
| `u` | 撤销删除 |
| `r` | 刷新列表 |
| `/` | 搜索 |
| `q` | 退出 |

## 📋 命令行使用

```bash
# 交互模式（默认）
python vscode-projects.py

# 列出所有项目
python vscode-projects.py --list

# 自定义数据库路径
python vscode-projects.py --db "/path/to/state.vscdb"

# 自定义 VSCode 路径
python vscode-projects.py --code "code-insiders"

# 显示帮助
python vscode-projects.py --help
```

## 🔧 常见问题

### 找不到 VSCode 数据库？

程序会自动检测，如果失败，可以手动指定：

```bash
# Windows
python vscode-projects.py --db "%APPDATA%\Code\User\globalStorage\state.vscdb"

# macOS
python vscode-projects.py --db "~/Library/Application Support/Code/User/globalStorage/state.vscdb"

# Linux
python vscode-projects.py --db "~/.config/Code/User/globalStorage/state.vscdb"
```

### 无法打开 VSCode？

确保 `code` 命令在 PATH 中，或手动指定：

```bash
# Windows
python vscode-projects.py --code "C:\Program Files\Microsoft VS Code\bin\code.cmd"

# macOS
python vscode-projects.py --code "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"

# Linux
python vscode-projects.py --code "/usr/bin/code"
```

### 中文显示乱码（Windows）？

使用 Windows Terminal 或在 CMD 中运行：

```batch
chcp 65001
python vscode-projects.py
```

## 📚 下一步

- 查看 [完整文档](README.md)
- 阅读 [使用指南](USAGE.md)
- 了解 [截图说明](SCREENSHOTS.md)
- 参与 [贡献](CONTRIBUTING.md)

## 🆘 需要帮助？

- 查看 [常见问题](USAGE.md#故障排除)
- 提交 [Issue](https://github.com/Xu22Web/vscode-projects/issues)
- 加入讨论

---

祝使用愉快！如有问题随时提问。😊
