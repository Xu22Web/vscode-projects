# 贡献指南

感谢您考虑为 VSCode Projects Manager 做出贡献！

## 🤝 如何贡献

### 报告 Bug

如果发现 Bug，请：

1. 检查是否已有相关 Issue
2. 创建新 Issue，包含：
   - Bug 描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 系统环境（OS、Python 版本、终端类型）
   - 截图（如适用）

### 功能建议

如果有新功能建议：

1. 检查是否已有相关讨论
2. 创建 Issue 描述：
   - 功能需求
   - 使用场景
   - 预期效果
   - 可能的实现方案（可选）

### 提交代码

1. **Fork 项目**
   ```bash
   # 克隆你的 fork
   git clone https://github.com/你的用户名/vscode-projects.git
   cd vscode-projects
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档

4. **测试代码**
   ```bash
   # 测试运行
   python vscode-projects.py

   # 测试编译
   python -m PyInstaller vscode-projects.spec

   # 或使用构建脚本
   # Windows
   build.bat

   # macOS/Linux
   chmod +x build.sh
   ./build.sh
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "描述你的更改"
   ```

6. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 描述你的更改
   - 引用相关 Issue
   - 等待 Review

## 📝 代码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 行长度限制为 100 字符
- 使用有意义的变量名

```python
# 好的示例
def get_project_path(uri):
    """从 URI 获取项目路径"""
    parsed = urlparse(uri)
    return unquote(parsed.path)

# 不好的示例
def gpp(u):
    p = urlparse(u)
    return unquote(p.path)
```

### 注释规范

```python
# 单行注释使用 #

def complex_function(param1, param2):
    """函数文档字符串

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明
    """
    pass
```

### 命名规范

- **变量和函数**: `snake_case`
- **类**: `PascalCase`
- **常量**: `UPPER_CASE`
- **私有成员**: `_leading_underscore`

## 🧪 测试

### 构建测试

在提交涉及构建的更改前，请测试所有构建脚本：

#### Windows 构建测试
```batch
# 测试 build.bat
build.bat

# 验证输出
dir dist\windows\vscode-projects.exe

# 测试可执行文件
dist\windows\vscode-projects.exe -h
dist\windows\vscode-projects.exe -l
```

#### macOS/Linux 构建测试
```bash
# 测试 build.sh
chmod +x build.sh
./build.sh

# 验证输出
ls -lh dist/macos/vscode-projects   # macOS
ls -lh dist/linux/vscode-projects   # Linux

# 测试可执行文件
./dist/macos/vscode-projects -h     # macOS
./dist/linux/vscode-projects -l     # Linux
```

#### 多平台构建测试
```bash
# 测试 build-all.sh
chmod +x build-all.sh
./build-all.sh

# 验证发布包
ls -lh dist/releases/
```

#### Spec 文件修改测试

如果修改了 `vscode-projects.spec`：

```bash
# 清理旧构建
rm -rf build dist

# 使用 spec 文件构建
pyinstaller vscode-projects.spec

# 测试可执行文件
./dist/vscode-projects -h
```

### 手动测试清单

在提交 PR 前，请确保测试：

- [ ] Windows 系统
  - [ ] CMD
  - [ ] PowerShell
  - [ ] Windows Terminal
  - [ ] Git Bash
- [ ] macOS 系统
  - [ ] Terminal.app
  - [ ] iTerm2
- [ ] Linux 系统
  - [ ] 主流发行版（Ubuntu、Fedora、Arch 等）
- [ ] WSL 环境
  - [ ] WSL 1
  - [ ] WSL 2

### 功能测试

- [ ] 启动程序
- [ ] 搜索功能
- [ ] 键盘导航
- [ ] 鼠标操作（如支持）
- [ ] 打开项目
- [ ] 删除项目
- [ ] 复制路径
- [ ] 文件管理器打开
- [ ] 命令行参数

## 📚 文档

如果你的更改影响用户使用，请更新：

- [ ] README.md - 主要文档和功能介绍
- [ ] BUILD.md - 构建相关的更改
- [ ] QUICKSTART.md - 快速开始指南
- [ ] USAGE.md - 使用说明
- [ ] CONTRIBUTING.md - 贡献指南（本文档）
- [ ] 代码注释 - 重要的代码说明
- [ ] CHANGELOG.md - 版本更改记录（如适用）

### 文档编写规范

- 使用清晰的标题和章节
- 提供代码示例
- 包含截图（如适用）
- 保持格式一致
- 使用正确的 Markdown 语法

### 构建文档更新指南

当修改构建相关内容时，需要更新：

1. **BUILD.md** - 如果改变了：
   - 构建脚本
   - 构建参数
   - 输出路径
   - 构建流程

2. **QUICKSTART.md** - 如果改变了：
   - 编译步骤
   - 快速开始流程

3. **README.md** - 如果改变了：
   - 安装方法
   - 基本使用方式

## 🔍 Pull Request 检查清单

提交 PR 前，请确保：

- [ ] 代码遵循项目风格
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
- [ ] 测试通过
- [ ] 没有引入新的警告或错误
- [ ] Commit 信息清晰明确
- [ ] PR 描述完整

## 📋 Commit 信息规范

使用清晰的 Commit 信息：

```
类型: 简短描述 (不超过 50 字符)

详细说明（可选，72 字符换行）

相关 Issue: #123
```

### Commit 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建或辅助工具

### 示例

```
feat: 添加鼠标点击支持

- 实现鼠标事件处理
- 支持单击选择、双击打开
- 添加滚轮滚动功能

相关 Issue: #45
```

## 🎯 开发环境设置

### 推荐工具

- **编辑器**: VSCode（当然！）
- **Python**: 3.11+
- **虚拟环境**: venv 或 conda

### 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install pyinstaller

# 运行程序
python vscode-projects.py
```

### VSCode 配置

推荐的 `.vscode/settings.json`：

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "autopep8",
  "editor.formatOnSave": true,
  "files.trimTrailingWhitespace": true
}
```

## 🐛 调试技巧

### 启用调试输出

在代码中添加调试信息：

```python
DEBUG = True  # 开发时设为 True

if DEBUG:
    print(f"Debug: {variable_name}")
```

### 使用 Python 调试器

```python
import pdb; pdb.set_trace()  # 设置断点
```

### VSCode 调试配置

`.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

## 📮 联系方式

- GitHub Issues: 技术问题和 Bug 报告
- Pull Requests: 代码贡献
- Discussions: 一般讨论和问题

## 📜 许可证

贡献的代码将采用 MIT 许可证。

提交代码即表示你同意：
- 代码可以被包含在项目中
- 遵循 MIT 许可证
- 放弃对代码的独占权利

## 🙏 致谢

感谢所有贡献者！你们的帮助让这个项目变得更好。

---

再次感谢您的贡献！❤️
