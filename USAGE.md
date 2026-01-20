# 使用示例

本文档提供了 VSCode Recent Projects Manager 的详细使用示例。

## 快速开始

### 1. 基本使用

启动程序进入交互模式：

```bash
python vscode-projects.py
# 或者使用编译后的可执行文件
./vscode-projects
```

### 2. 搜索项目

按 `/` 进入搜索模式，在搜索框中输入关键词，支持：
- 项目名称模糊搜索
- 路径模糊搜索

**示例：**
```
> my-proj        # 搜索项目名称包含 "my-proj" 的项目
> /home/user     # 搜索路径包含 "/home/user" 的项目
> react          # 搜索名称包含 "react" 的项目
```

**操作：**
- 输入内容实时过滤
- `Enter` 确认搜索
- `Esc` 退出搜索模式
- `Backspace` 删除字符

### 3. 打开项目

**单个项目：**
- 使用 `↑` `↓` 键选择项目
- 按 `Enter` 在当前窗口打开（程序退出）
- 按 `n` 在新窗口打开（程序不退出，可继续操作）

**多个项目：**
- 按 `Space` 选中/取消选中项目
- 按 `a` 全选/取消全选
- 按 `Enter` 在新窗口打开所有选中项目（程序退出）
- 按 `w` 将所有选中项目作为工作区打开（程序不退出）

**使用鼠标：**
- 单击选择/取消选择项目
- 双击打开项目

### 4. 管理项目

#### 删除项目

```
1. 选择要删除的项目（可多选）
2. 按 d 键
3. 输入 y 确认删除，或 n/Esc 取消
```

**提示：**
- 支持多选后批量删除
- 删除后可以按 `u` 键撤销

#### 撤销删除

```
1. 按 u 键
2. 恢复上次删除的项目
```

**注意：** 只能撤销最近一次的删除操作。

#### 刷新项目列表

```
1. 按 r 键
2. 重新从数据库加载项目列表
```

#### 复制项目路径

```
1. 选择项目
2. 按 y 键
3. 路径已复制到剪贴板
```

**注意：** Linux 系统需要安装 `xclip` 或 `xsel` 工具。

#### 在文件管理器中打开

```
1. 选择项目
2. 按 o 键
3. 系统文件管理器会打开项目所在目录
```

## 命令行参数示例

### 列出所有项目

```bash
# 以表格形式列出所有项目
python vscode-projects.py --list

# 输出示例：
# ┌──────────────────────────────────────────────────────────┐
# │  VSCode Recent Projects (15 projects)                    │
# ├──────────────────────────────────────────────────────────┤
# │ 📁 my-project        /home/user/projects/my-project      │
# │ 📄 script.py         /home/user/scripts/script.py        │
# │ 🔧 workspace         /home/user/workspace.code-workspace │
# └──────────────────────────────────────────────────────────┘
```

### 自定义数据库路径

```bash
# Windows
python vscode-projects.py --db "C:\Users\YourName\AppData\Roaming\Code\User\globalStorage\state.vscdb"

# macOS / Linux
python vscode-projects.py --db "~/Library/Application Support/Code/User/globalStorage/state.vscdb"

# WSL
python vscode-projects.py --db "/mnt/c/Users/YourName/AppData/Roaming/Code/User/globalStorage/state.vscdb"
```

### 自定义 VSCode 路径

```bash
# 使用 Code Insiders
python vscode-projects.py --code "code-insiders"

# Windows - 指定完整路径
python vscode-projects.py --code "C:\Program Files\Microsoft VS Code\bin\code.cmd"

# macOS
python vscode-projects.py --code "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"

# Linux
python vscode-projects.py --code "/usr/bin/code"
```

### 组合使用参数

```bash
# 同时指定数据库和 VSCode 路径
python vscode-projects.py \
  --db "/custom/path/state.vscdb" \
  --code "code-insiders"
```

## 高级使用技巧

### 1. 创建快捷命令（Windows）

将可执行文件添加到 PATH：

```batch
# 复制到用户目录
copy vscode-projects.exe %USERPROFILE%\

# 或者添加到 System32（需要管理员权限）
copy vscode-projects.exe C:\Windows\System32\

# 创建别名（PowerShell）
Set-Alias -Name vsp -Value vscode-projects
```

### 2. 创建快捷命令（Linux/macOS）

```bash
# 复制到 /usr/local/bin
sudo cp vscode-projects /usr/local/bin/

# 或者创建符号链接
sudo ln -s $(pwd)/vscode-projects /usr/local/bin/vsp

# 添加别名到 ~/.bashrc 或 ~/.zshrc
echo 'alias vsp="vscode-projects"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 在终端配置文件中集成

#### Bash (Linux/macOS)

编辑 `~/.bashrc`：

```bash
# VSCode Projects 快捷命令
alias vsp='python ~/path/to/vscode-projects.py'

# 自定义函数：快速打开项目
vsc() {
  if [ $# -eq 0 ]; then
    python ~/path/to/vscode-projects.py
  else
    code "$1"
  fi
}
```

#### PowerShell (Windows)

编辑 PowerShell 配置文件（`$PROFILE`）：

```powershell
# VSCode Projects 快捷命令
function vsp {
  python D:\path\to\vscode-projects.py $args
}

# 自定义函数
function vsc {
  if ($args.Count -eq 0) {
    python D:\path\to\vscode-projects.py
  } else {
    code $args[0]
  }
}
```

### 4. WSL 环境配置

在 WSL 中使用 Windows 的 VSCode：

```bash
# 方法一：自动检测（推荐）
python vscode-projects.py

# 方法二：指定 Windows VSCode 路径
python vscode-projects.py --code "/mnt/c/Users/YourName/AppData/Local/Programs/Microsoft VS Code/bin/code"

# 方法三：使用 code 命令（如果已在 WSL PATH 中）
python vscode-projects.py --code "code"
```

### 5. 远程项目使用

#### SSH 远程项目

程序会自动识别 SSH 远程项目：

```
显示格式：
🌐 project-name [SSH] ssh://hostname/path/to/project
```

打开远程项目时，VSCode 会自动使用 Remote-SSH 扩展连接。

#### WSL 项目

```
显示格式：
🌐 project-name [WSL:Ubuntu] /path/in/wsl
```

#### Dev Container

```
显示格式：
🌐 project-name [Container] dev-container+...
```

## 故障排除

### 问题 1：找不到 VSCode 数据库

**症状：**
```
错误: 未找到 VSCode 数据库
```

**解决方案：**
1. 确认已安装 VSCode
2. 至少打开过一次 VSCode
3. 手动指定路径：
   ```bash
   python vscode-projects.py --db "/path/to/state.vscdb"
   ```

### 问题 2：无法打开 VSCode

**症状：**
```
错误: 未找到 VSCode 命令
```

**解决方案：**
1. 确认 VSCode 已安装
2. 确认 `code` 命令在 PATH 中
3. 手动指定路径：
   ```bash
   python vscode-projects.py --code "/path/to/code"
   ```

### 问题 3：中文显示乱码（Windows CMD）

**解决方案：**
```batch
# 设置 UTF-8 编码
chcp 65001

# 或使用 Windows Terminal（推荐）
```

### 问题 4：颜色显示异常

**解决方案：**
- 使用支持 ANSI 颜色的现代终端
- Windows：使用 Windows Terminal
- macOS：使用 iTerm2 或 Terminal.app
- Linux：使用 GNOME Terminal、Konsole 等

### 问题 5：鼠标点击无效

**原因：**终端不支持鼠标事件

**解决方案：**
- 使用键盘快捷键代替
- 升级到支持鼠标的终端
  - Windows: Windows Terminal
  - macOS: iTerm2
  - Linux: 最新版 GNOME Terminal

## 性能优化

### 处理大量项目

如果有数百个项目，可以：

1. **定期清理无效项目**
   - 使用 `d` 键删除不需要的项目
   - 误删可用 `u` 键撤销
   - 使用 `r` 键刷新列表

2. **使用搜索功能**
   - 按 `/` 进入搜索模式
   - 输入项目名称或路径关键词
   - 实时过滤结果

3. **优化 VSCode 设置**
   - 在 VSCode 中限制历史记录数量
   - 定期清理 VSCode 工作区

## 最佳实践

1. **项目命名规范**
   - 使用有意义的项目名称
   - 避免使用特殊字符

2. **项目组织**
   - 将相关项目放在同一目录下
   - 使用有规律的路径结构
   - 便于通过路径搜索快速定位

3. **定期维护**
   - 每月清理一次无效项目
   - 删除不再使用的工作区

4. **备份重要工作区**
   - 定期备份 `.code-workspace` 文件
   - 导出项目列表

## 配置文件（可选）

虽然程序不需要配置文件，但可以创建一个脚本来保存常用设置：

**config.sh (Linux/macOS):**
```bash
#!/bin/bash
DB_PATH="$HOME/Library/Application Support/Code/User/globalStorage/state.vscdb"
CODE_PATH="/usr/local/bin/code"

python vscode-projects.py --db "$DB_PATH" --code "$CODE_PATH" "$@"
```

**config.bat (Windows):**
```batch
@echo off
set DB_PATH=%APPDATA%\Code\User\globalStorage\state.vscdb
set CODE_PATH=code

python vscode-projects.py --db "%DB_PATH%" --code "%CODE_PATH%" %*
```

## 集成到其他工具

### 与 tmux 集成

```bash
# ~/.tmux.conf
bind-key v run-shell "python ~/vscode-projects.py"
```

### 与 Alfred 集成（macOS）

创建 Workflow 执行：
```bash
python ~/vscode-projects.py
```

### 与 Raycast 集成（macOS）

创建脚本命令执行 `vscode-projects.py`

## 更多资源

- [GitHub 仓库](https://github.com/Xu22Web/vscode-projects)
- [问题反馈](https://github.com/Xu22Web/vscode-projects/issues)
- [VSCode 官方文档](https://code.visualstudio.com/docs)

---

**提示：** 本文档持续更新中，如有疑问请提交 Issue。
