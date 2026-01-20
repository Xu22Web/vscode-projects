#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSCode Recent Projects Manager v1.0.0
跨平台 VSCode 最近项目管理器 - fzf 风格界面
支持: Windows (CMD/PowerShell/Terminal/Git Bash), macOS, Linux, WSL
新增: 鼠标点击支持, --db 参数指定数据库路径
"""

import os
import sys
import json
import sqlite3
import subprocess
import unicodedata
import tempfile
import shutil
from urllib.parse import unquote, urlparse

# 平台检测
IS_WINDOWS = sys.platform == 'win32'

# 平台相关模块
HAS_UNIX_TERMINAL = False
HAS_WINDOWS_TERMINAL = False

if IS_WINDOWS:
    try:
        import msvcrt
        HAS_WINDOWS_TERMINAL = True
    except ImportError:
        pass
else:
    try:
        import termios
        import tty
        import fcntl
        HAS_UNIX_TERMINAL = True
    except ImportError:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# 颜色和样式
# ═══════════════════════════════════════════════════════════════════════════════

class C:
    """颜色常量"""
    RST = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    STRIKETHROUGH = '\033[9m'  # 删除线
    REVERSE = '\033[7m'

    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

    # 亮色
    LRED = '\033[91m'
    LGREEN = '\033[92m'
    LYELLOW = '\033[93m'
    LBLUE = '\033[94m'
    LMAGENTA = '\033[95m'
    LCYAN = '\033[96m'

    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_GRAY = '\033[100m'


# ═══════════════════════════════════════════════════════════════════════════════
# 字符串宽度处理
# ═══════════════════════════════════════════════════════════════════════════════

import re

# ANSI 转义序列正则
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(s):
    """移除 ANSI 转义序列"""
    return ANSI_ESCAPE.sub('', s)


def char_width(c):
    """获取字符显示宽度"""
    if ord(c) < 32:
        return 0
    ea = unicodedata.east_asian_width(c)
    return 2 if ea in ('F', 'W', 'A') else 1


def str_width(s):
    """计算字符串显示宽度（忽略 ANSI 转义序列）"""
    return sum(char_width(c) for c in strip_ansi(s))


def str_pad(s, width, align='left', fill=' '):
    """填充字符串到指定宽度"""
    w = str_width(s)
    if w >= width:
        return s
    pad = fill * (width - w)
    if align == 'left':
        return s + pad
    elif align == 'right':
        return pad + s
    else:  # center
        left = (width - w) // 2
        right = width - w - left
        return fill * left + s + fill * right


def str_cut(s, max_width, ellipsis='..'):
    """截断字符串（保留 ANSI 转义序列）"""
    # 如果没有 ANSI 代码，简单处理
    if '\x1b' not in s:
        if str_width(s) <= max_width:
            return s

        result = ''
        width = 0
        ew = str_width(ellipsis)

        for c in s:
            cw = char_width(c)
            if width + cw + ew > max_width:
                return result + ellipsis
            result += c
            width += cw
        return result

    # 有 ANSI 代码，需要特殊处理
    plain = strip_ansi(s)
    if str_width(plain) <= max_width:
        return s

    # 截断纯文本
    result = ''
    width = 0
    ew = str_width(ellipsis)

    for c in plain:
        cw = char_width(c)
        if width + cw + ew > max_width:
            break
        result += c
        width += cw

    return result + ellipsis


# ═══════════════════════════════════════════════════════════════════════════════
# 系统检测和路径
# ═══════════════════════════════════════════════════════════════════════════════

def detect_os():
    """检测操作系统"""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    elif os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                return 'wsl'
    return 'linux'


def get_db_path(custom_path=None):
    """获取 VSCode state.vscdb 路径

    优先级:
    1. 用户指定的路径 (--db 参数)
    2. 默认路径
    """
    # 1. 用户指定的路径
    if custom_path:
        if os.path.exists(custom_path):
            return custom_path
        # 尝试展开路径
        expanded = os.path.expanduser(custom_path)
        if os.path.exists(expanded):
            return expanded
        return custom_path  # 返回原路径，让后续报错

    os_type = detect_os()

    if os_type == 'windows':
        base = os.environ.get('APPDATA', os.path.expanduser('~/AppData/Roaming'))
    elif os_type == 'macos':
        base = os.path.expanduser('~/Library/Application Support')
    elif os_type == 'wsl':
        try:
            result = subprocess.run(['cmd.exe', '/c', 'echo %USERNAME%'],
                                    capture_output=True, text=True, timeout=5)
            username = result.stdout.strip()
            base = f'/mnt/c/Users/{username}/AppData/Roaming'
        except:
            base = '/mnt/c/Users'
            for name in os.listdir(base):
                test = os.path.join(base, name, 'AppData/Roaming/Code/User/globalStorage/state.vscdb')
                if os.path.exists(test):
                    return test
            return None
    else:
        base = os.path.expanduser('~/.config')

    return os.path.join(base, 'Code/User/globalStorage/state.vscdb')


def get_vscode_cmd(custom_path=None):
    """获取 VSCode 命令

    优先级:
    1. 用户指定的路径 (--code 参数)
    2. PATH 环境变量中的命令
    3. Windows 常见安装位置
    """
    # 1. 用户指定的路径
    if custom_path:
        if os.path.exists(custom_path):
            return custom_path
        # 如果是命令名，尝试在 PATH 中查找
        found = shutil.which(custom_path)
        if found:
            return found

    # 2. PATH 中的命令
    for cmd in ['code', 'code-insiders', 'codium']:
        found = shutil.which(cmd)
        if found:
            return found

    # 3. Windows: 搜索常见安装位置
    if IS_WINDOWS:
        possible_paths = []

        # 用户目录安装 (最常见)
        local_app = os.environ.get('LOCALAPPDATA', '')
        if local_app:
            possible_paths.extend([
                os.path.join(local_app, 'Programs', 'Microsoft VS Code', 'bin', 'code.cmd'),
                os.path.join(local_app, 'Programs', 'Microsoft VS Code', 'Code.exe'),
                os.path.join(local_app, 'Programs', 'Microsoft VS Code Insiders', 'bin', 'code-insiders.cmd'),
                os.path.join(local_app, 'Programs', 'Microsoft VS Code Insiders', 'Code - Insiders.exe'),
            ])

        # 系统安装
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        for pf in [program_files, program_files_x86]:
            possible_paths.extend([
                os.path.join(pf, 'Microsoft VS Code', 'bin', 'code.cmd'),
                os.path.join(pf, 'Microsoft VS Code', 'Code.exe'),
                os.path.join(pf, 'Microsoft VS Code Insiders', 'bin', 'code-insiders.cmd'),
            ])

        # 检查每个路径
        for path in possible_paths:
            if os.path.exists(path):
                return path

    return None


def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    os_type = detect_os()
    try:
        if os_type == 'macos':
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
        elif os_type == 'wsl':
            subprocess.run(['clip.exe'], input=text.encode(), check=True)
        elif os_type == 'windows':
            subprocess.run(['clip'], input=text.encode(), shell=True, check=True)
        else:  # linux
            # 尝试 xclip 或 xsel
            if shutil.which('xclip'):
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
            elif shutil.which('xsel'):
                subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode(), check=True)
            else:
                return False
        return True
    except:
        return False


def open_in_file_manager(path):
    """在文件管理器中打开路径"""
    os_type = detect_os()
    try:
        if os_type == 'macos':
            subprocess.Popen(['open', path])
        elif os_type == 'wsl':
            # WSL 路径转 Windows 路径
            if path.startswith('/mnt/'):
                # /mnt/c/xxx -> C:\xxx
                win_path = path[5].upper() + ':' + path[6:].replace('/', '\\')
                subprocess.Popen(['explorer.exe', win_path])
            else:
                # 尝试使用 wslpath
                result = subprocess.run(['wslpath', '-w', path], capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.Popen(['explorer.exe', result.stdout.strip()])
                else:
                    subprocess.Popen(['explorer.exe', path])
        elif os_type == 'windows':
            # Windows 路径需要使用反斜杠，并确保路径存在
            win_path = path.replace('/', '\\')
            if os.path.exists(win_path):
                subprocess.Popen(['explorer', win_path], shell=True)
            else:
                # 如果路径不存在，尝试打开父目录
                parent = os.path.dirname(win_path)
                if os.path.exists(parent):
                    subprocess.Popen(['explorer', parent], shell=True)
                else:
                    subprocess.Popen(['explorer', win_path], shell=True)
        else:  # linux
            subprocess.Popen(['xdg-open', path])
        return True
    except:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 数据加载
# ═══════════════════════════════════════════════════════════════════════════════

def load_projects(db_path):
    """从数据库加载项目"""
    if not db_path or not os.path.exists(db_path):
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key='history.recentlyOpenedPathsList'")
        row = cursor.fetchone()
        conn.close()

        if not row:
            return []

        data = json.loads(row[0])
        projects = []

        for entry in data.get('entries', []):
            uri = entry.get('folderUri') or entry.get('fileUri') or \
                  (entry.get('workspace', {}) or {}).get('configPath', '')

            if not uri:
                continue

            label = entry.get('label', '')

            # 类型判断
            if entry.get('folderUri'):
                ptype = 'folder'
            elif entry.get('fileUri'):
                ptype = 'file'
            elif entry.get('workspace'):
                ptype = 'workspace'
            else:
                # 对于 vscode-remote，如果既没有 folderUri 也没有 fileUri
                # 根据路径判断（通常带扩展名的是文件）
                ptype = 'folder'

            # 解析路径
            remote_tag = ''
            if uri.startswith('file://'):
                parsed = urlparse(uri)
                path = unquote(parsed.path)
                if len(path) > 2 and path[0] == '/' and path[2] == ':':
                    path = path[1:]
            elif uri.startswith('vscode-remote://'):
                parsed = urlparse(uri)
                path = unquote(parsed.path)
                netloc = unquote(parsed.netloc)

                # 解析 wsl+Ubuntu, wsl+Debian, ssh-remote+hostname 等格式
                if netloc.lower().startswith('wsl+'):
                    # wsl+ubuntu -> WSL: Ubuntu (首字母大写)
                    distro = netloc[4:]
                    if distro:
                        distro = distro[0].upper() + distro[1:] if len(distro) > 0 else distro
                    remote_tag = f'WSL: {distro}' if distro else 'WSL'
                elif netloc.lower() == 'wsl':
                    remote_tag = 'WSL'
                elif netloc.lower().startswith('ssh-remote+'):
                    host = netloc[11:]
                    remote_tag = f'SSH: {host}' if host else 'SSH'
                elif 'ssh' in netloc.lower():
                    remote_tag = 'SSH'
                elif 'dev-container' in netloc.lower():
                    remote_tag = 'Container'
                else:
                    remote_tag = 'Remote'

                # 对于 vscode-remote URI，根据文件扩展名判断类型
                if ptype == 'folder':
                    basename = os.path.basename(path)
                    if '.' in basename and not basename.startswith('.'):
                        ext = basename.rsplit('.', 1)[-1].lower()
                        # 常见代码文件扩展名
                        if ext in ('py', 'js', 'ts', 'jsx', 'tsx', 'vue', 'json', 'sh', 'md',
                                   'txt', 'html', 'css', 'scss', 'yaml', 'yml', 'toml', 'xml'):
                            ptype = 'file'
            else:
                path = uri

            # 从 label 提取标签 (优先使用 VSCode 提供的标签)
            if label and '[' in label and ']' in label:
                ts = label.rfind('[')
                te = label.rfind(']')
                if ts < te:
                    remote_tag = label[ts+1:te]

            name = os.path.basename(path) or path
            dir_path = os.path.dirname(path) or '/'

            # 计算显示路径（根据运行环境调整）
            # Windows 环境：WSL 挂载路径 -> Windows 路径
            # WSL 环境：Windows 路径 -> WSL 挂载路径
            os_type = detect_os()
            display_path = ''  # 用于显示的转换路径

            if os_type == 'wsl':
                # WSL 环境：Windows 路径转换为挂载路径
                if len(path) > 2 and path[1] == ':':
                    # D:/xxx -> /mnt/d/xxx
                    drive = path[0].lower()
                    rest = path[2:].replace('\\', '/')
                    display_path = f'/mnt/{drive}{rest}'
            else:
                # Windows 环境：WSL 挂载路径转换为 Windows 路径
                if path.startswith('/mnt/') and len(path) > 6:
                    if path[6] == '/' and path[5].isalpha():
                        # /mnt/d/xxx -> D:/xxx
                        drive = path[5].upper()
                        rest = path[7:]
                        if ':' not in rest:
                            display_path = f'{drive}:/{rest}'

            # 检测路径是否存在
            exists = True

            if uri.startswith('file://'):
                if os_type == 'wsl' and display_path:
                    # WSL 环境，用转换后的挂载路径检测
                    exists = os.path.exists(display_path)
                else:
                    exists = os.path.exists(path)
            elif uri.startswith('vscode-remote://'):
                # 远程路径检测
                if display_path:
                    # 有转换路径，用转换路径检测
                    if os_type == 'wsl':
                        exists = os.path.exists(path)  # WSL 项目用原始路径
                    else:
                        win_path = display_path.replace('/', '\\')
                        exists = os.path.exists(win_path)
                else:
                    # SSH/Container 等远程路径，默认存在
                    exists = True

            projects.append({
                'uri': uri,
                'name': name,
                'path': dir_path,
                'full_path': path,
                'display_path': display_path,  # 转换后的显示路径
                'type': ptype,
                'tag': remote_tag,
                'exists': exists  # 路径是否存在
            })

        return projects
    except:
        return []


def save_projects(db_path, projects):
    """保存项目到数据库"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key='history.recentlyOpenedPathsList'")
        row = cursor.fetchone()

        if row:
            data = json.loads(row[0])
            keep_uris = {p['uri'] for p in projects}

            new_entries = []
            for entry in data.get('entries', []):
                uri = entry.get('folderUri') or entry.get('fileUri') or \
                      (entry.get('workspace', {}) or {}).get('configPath', '')
                if uri in keep_uris:
                    new_entries.append(entry)

            data['entries'] = new_entries
            cursor.execute("UPDATE ItemTable SET value=? WHERE key='history.recentlyOpenedPathsList'",
                          (json.dumps(data, ensure_ascii=False),))
            conn.commit()

        conn.close()
    except:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# 终端控制
# ═══════════════════════════════════════════════════════════════════════════════

class Terminal:
    """终端控制 - 跨平台支持"""

    def __init__(self):
        self.old = None
        self.rows = 24
        self.cols = 80
        self.is_windows_native = IS_WINDOWS and HAS_WINDOWS_TERMINAL and not HAS_UNIX_TERMINAL
        self.kernel32 = None
        self.in_handle = None
        self.old_input_mode = None
        if not self.is_windows_native:
            self.fd = sys.stdin.fileno()

    def start(self):
        """进入原始模式"""
        if self.is_windows_native:
            # Windows 原生模式 - 启用虚拟终端序列和鼠标事件
            if sys.platform == 'win32':
                try:
                    import ctypes
                    self.kernel32 = ctypes.windll.kernel32
                    # 常量定义
                    STD_OUTPUT_HANDLE = -11
                    STD_INPUT_HANDLE = -10
                    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                    ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
                    ENABLE_MOUSE_INPUT = 0x0010
                    ENABLE_EXTENDED_FLAGS = 0x0080
                    ENABLE_WINDOW_INPUT = 0x0008
                    ENABLE_QUICK_EDIT_MODE = 0x0040  # 需要禁用
                    ENABLE_PROCESSED_INPUT = 0x0001

                    # 输出句柄 - 启用 ANSI 转义序列
                    handle = self.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                    mode = ctypes.c_ulong()
                    self.kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                    self.kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

                    # 输入句柄 - 启用鼠标输入
                    self.in_handle = self.kernel32.GetStdHandle(STD_INPUT_HANDLE)
                    in_mode = ctypes.c_ulong()
                    self.kernel32.GetConsoleMode(self.in_handle, ctypes.byref(in_mode))
                    self.old_input_mode = in_mode.value

                    # 关键：禁用快速编辑模式，启用鼠标输入
                    # 快速编辑模式会拦截鼠标事件用于文本选择
                    new_mode = in_mode.value
                    new_mode |= ENABLE_MOUSE_INPUT | ENABLE_EXTENDED_FLAGS | ENABLE_WINDOW_INPUT
                    new_mode &= ~ENABLE_QUICK_EDIT_MODE  # 禁用快速编辑
                    self.kernel32.SetConsoleMode(self.in_handle, new_mode)
                except:
                    pass
            # 备用屏幕 + 隐藏光标 + 启用鼠标追踪
            sys.stdout.write('\033[?1049h\033[?25l\033[?1000h\033[?1006h')
            sys.stdout.flush()
        elif HAS_UNIX_TERMINAL:
            self.old = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
            # 备用屏幕 + 隐藏光标 + 启用鼠标追踪 (SGR模式)
            sys.stdout.write('\033[?1049h\033[?25l\033[?1000h\033[?1006h')
            sys.stdout.flush()
        else:
            # 没有可用的终端控制模块
            print(f"{C.RED}错误: 当前环境不支持终端原始模式{C.RST}")
            print(f"{C.GRAY}提示: 请使用以下方式之一运行:{C.RST}")
            print(f"{C.GRAY}  1. Windows 命令提示符 (cmd.exe){C.RST}")
            print(f"{C.GRAY}  2. Windows PowerShell{C.RST}")
            print(f"{C.GRAY}  3. Windows Terminal{C.RST}")
            print(f"{C.GRAY}  4. 使用 -l 参数列出项目: python {sys.argv[0]} -l{C.RST}")
            sys.exit(1)

    def stop(self):
        """恢复终端"""
        if self.old and HAS_UNIX_TERMINAL:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        # Windows: 恢复输入模式
        if self.kernel32 and self.in_handle and self.old_input_mode is not None:
            self.kernel32.SetConsoleMode(self.in_handle, self.old_input_mode)
        # 禁用鼠标追踪 + 显示光标 + 恢复主屏幕
        sys.stdout.write('\033[?1006l\033[?1000l\033[?25h\033[?1049l')
        sys.stdout.flush()

    def size(self):
        """获取尺寸"""
        sz = shutil.get_terminal_size()
        self.rows, self.cols = sz.lines, sz.columns
        return self.rows, self.cols

    def read_key(self):
        """读取按键 - 跨平台"""
        if self.is_windows_native:
            return self._read_key_windows()
        else:
            return self._read_key_unix()

    def _read_key_windows(self):
        """Windows 原生按键读取 (使用 Windows Console API)"""
        import ctypes

        # 如果有 Console API 句柄，使用 ReadConsoleInput 读取输入事件
        if self.kernel32 and self.in_handle:
            # 定义 INPUT_RECORD 结构
            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

            class KEY_EVENT_RECORD(ctypes.Structure):
                _fields_ = [
                    ("bKeyDown", ctypes.c_int),
                    ("wRepeatCount", ctypes.c_ushort),
                    ("wVirtualKeyCode", ctypes.c_ushort),
                    ("wVirtualScanCode", ctypes.c_ushort),
                    ("uChar", ctypes.c_wchar),
                    ("dwControlKeyState", ctypes.c_ulong),
                ]

            class MOUSE_EVENT_RECORD(ctypes.Structure):
                _fields_ = [
                    ("dwMousePosition", COORD),
                    ("dwButtonState", ctypes.c_ulong),
                    ("dwControlKeyState", ctypes.c_ulong),
                    ("dwEventFlags", ctypes.c_ulong),
                ]

            class INPUT_RECORD_UNION(ctypes.Union):
                _fields_ = [
                    ("KeyEvent", KEY_EVENT_RECORD),
                    ("MouseEvent", MOUSE_EVENT_RECORD),
                ]

            class INPUT_RECORD(ctypes.Structure):
                _fields_ = [
                    ("EventType", ctypes.c_ushort),
                    ("Event", INPUT_RECORD_UNION),
                ]

            KEY_EVENT = 0x0001
            MOUSE_EVENT = 0x0002
            FROM_LEFT_1ST_BUTTON_PRESSED = 0x0001
            MOUSE_WHEELED = 0x0004

            ir = INPUT_RECORD()
            num_read = ctypes.c_ulong()

            # 持续读取直到获得有效输入
            while True:
                result = self.kernel32.ReadConsoleInputW(
                    self.in_handle, ctypes.byref(ir), 1, ctypes.byref(num_read)
                )

                if not result or num_read.value == 0:
                    continue  # 继续等待

                if ir.EventType == KEY_EVENT:
                    ke = ir.Event.KeyEvent
                    if not ke.bKeyDown:
                        continue  # 忽略键盘释放事件

                    vk = ke.wVirtualKeyCode
                    ch = ke.uChar

                    # 方向键和功能键
                    if vk == 0x26: return 'UP'
                    if vk == 0x28: return 'DOWN'
                    if vk == 0x25: return 'LEFT'
                    if vk == 0x27: return 'RIGHT'
                    if vk == 0x21: return 'PGUP'
                    if vk == 0x22: return 'PGDN'
                    if vk == 0x24: return 'HOME'
                    if vk == 0x23: return 'END'
                    if vk == 0x2E: return 'DEL'
                    if vk == 0x1B: return 'ESC'
                    if vk == 0x0D: return 'ENTER'
                    if vk == 0x09: return 'TAB'
                    if vk == 0x08: return 'BACKSPACE'

                    # 字符键
                    if ch:
                        if ch == '\x03': return 'CTRL_C'
                        if ch == '\x04': return 'CTRL_D'
                        if ch == '\r' or ch == '\n': return 'ENTER'
                        if ch.isprintable():
                            return ch

                    # 忽略其他控制键（Shift, Ctrl, Alt 等）
                    continue

                elif ir.EventType == MOUSE_EVENT:
                    me = ir.Event.MouseEvent
                    x = me.dwMousePosition.X + 1
                    y = me.dwMousePosition.Y + 1

                    # 鼠标滚轮
                    if me.dwEventFlags & MOUSE_WHEELED:
                        wheel_delta = ctypes.c_short(me.dwButtonState >> 16).value
                        if wheel_delta > 0:
                            return 'UP'
                        else:
                            return 'DOWN'

                    # 鼠标左键点击（仅处理按下，不处理移动）
                    if (me.dwButtonState & FROM_LEFT_1ST_BUTTON_PRESSED) and me.dwEventFlags == 0:
                        return ('MOUSE_CLICK', x, y)

                    # 忽略其他鼠标事件（移动、释放等）
                    continue

                else:
                    # 忽略其他事件类型（窗口大小变化等）
                    continue

        # 降级使用 msvcrt（没有鼠标支持）
        ch = msvcrt.getwch()

        # 特殊键前缀
        if ch in ('\x00', '\xe0'):
            # 读取扩展键码
            ext = msvcrt.getwch()
            # 方向键和其他特殊键
            if ext == 'H': return 'UP'
            if ext == 'P': return 'DOWN'
            if ext == 'M': return 'RIGHT'
            if ext == 'K': return 'LEFT'
            if ext == 'G': return 'HOME'
            if ext == 'O': return 'END'
            if ext == 'I': return 'PGUP'
            if ext == 'Q': return 'PGDN'
            if ext == 'S': return 'DEL'
            return None

        # ESC 键
        if ch == '\x1b':
            # 检查是否有后续字符 (ANSI 序列)
            import time
            time.sleep(0.01)  # 短暂等待
            if msvcrt.kbhit():
                buf = ''
                while msvcrt.kbhit():
                    buf += msvcrt.getwch()
                # 解析 ANSI 序列
                if buf.startswith('['):
                    seq = buf[1:]
                    # SGR 鼠标事件: [<Btn;X;YM 或 [<Btn;X;Ym
                    if seq.startswith('<'):
                        return self._parse_mouse_sgr(seq[1:])
                    if 'A' in seq: return 'UP'
                    if 'B' in seq: return 'DOWN'
                    if 'C' in seq: return 'RIGHT'
                    if 'D' in seq: return 'LEFT'
            return 'ESC'

        # 回车键
        if ch == '\r' or ch == '\n':
            return 'ENTER'

        # Tab 键
        if ch == '\t':
            return 'TAB'

        # 退格键
        if ch == '\x08' or ch == '\x7f':
            return 'BACKSPACE'

        # Ctrl+C
        if ch == '\x03':
            return 'CTRL_C'

        # Ctrl+D
        if ch == '\x04':
            return 'CTRL_D'

        return ch

    def _read_key_unix(self):
        """Unix 系统按键读取 (使用 termios/fcntl)"""
        ch = sys.stdin.read(1)

        if ch == '\x1b':
            # 设置非阻塞模式读取后续字符
            old_flags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

            try:
                # 尝试读取更多字符
                buf = ''
                try:
                    buf = sys.stdin.read(64)  # 增大缓冲区以处理鼠标事件
                except (IOError, BlockingIOError):
                    pass

                if not buf:
                    return 'ESC'

                # 解析 ESC 序列
                if buf.startswith('['):
                    seq = buf[1:]

                    # SGR 鼠标事件: \x1b[<Btn;X;YM 或 \x1b[<Btn;X;Ym
                    if seq.startswith('<'):
                        return self._parse_mouse_sgr(seq[1:])

                    # 方向键等
                    if seq.startswith('A') or seq == 'A': return 'UP'
                    if seq.startswith('B') or seq == 'B': return 'DOWN'
                    if seq.startswith('C') or seq == 'C': return 'RIGHT'
                    if seq.startswith('D') or seq == 'D': return 'LEFT'
                    if seq.startswith('H') or seq == 'H': return 'HOME'
                    if seq.startswith('F') or seq == 'F': return 'END'
                    if seq.startswith('5~'): return 'PGUP'
                    if seq.startswith('6~'): return 'PGDN'
                    if seq.startswith('1~') or seq.startswith('7~'): return 'HOME'
                    if seq.startswith('4~') or seq.startswith('8~'): return 'END'
                    # 带修饰键的方向键 (如 1;5A)
                    if 'A' in seq: return 'UP'
                    if 'B' in seq: return 'DOWN'
                    if 'C' in seq: return 'RIGHT'
                    if 'D' in seq: return 'LEFT'
                    return None

                elif buf.startswith('O'):
                    seq = buf[1:2] if len(buf) > 1 else ''
                    if seq == 'A': return 'UP'
                    if seq == 'B': return 'DOWN'
                    if seq == 'C': return 'RIGHT'
                    if seq == 'D': return 'LEFT'
                    if seq == 'H': return 'HOME'
                    if seq == 'F': return 'END'
                    return None

                return None

            finally:
                # 恢复阻塞模式
                fcntl.fcntl(self.fd, fcntl.F_SETFL, old_flags)

        if ch == '\r' or ch == '\n': return 'ENTER'
        if ch == '\t': return 'TAB'
        if ch == '\x7f' or ch == '\x08': return 'BACKSPACE'
        if ch == '\x03': return 'CTRL_C'
        if ch == '\x04': return 'CTRL_D'

        return ch

    def _parse_mouse_sgr(self, seq):
        """解析 SGR 格式的鼠标事件: Btn;X;YM 或 Btn;X;Ym"""
        try:
            # 查找结束符 M (按下) 或 m (释放)
            if 'M' in seq:
                end_idx = seq.index('M')
                is_press = True
            elif 'm' in seq:
                end_idx = seq.index('m')
                is_press = False
            else:
                return None

            parts = seq[:end_idx].split(';')
            if len(parts) != 3:
                return None

            btn = int(parts[0])
            x = int(parts[1])  # 1-based
            y = int(parts[2])  # 1-based

            # 只处理鼠标左键点击 (btn=0) 和释放事件
            # btn: 0=左键, 1=中键, 2=右键, 64=滚轮上, 65=滚轮下
            if btn == 0 and is_press:
                return ('MOUSE_CLICK', x, y)
            elif btn == 64:  # 滚轮上
                return 'UP'
            elif btn == 65:  # 滚轮下
                return 'DOWN'

            return None
        except:
            return None

    def goto(self, row, col):
        sys.stdout.write(f'\033[{row};{col}H')

    def clear_line(self):
        sys.stdout.write('\033[K')

    def write(self, s):
        sys.stdout.write(s)

    def flush(self):
        sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════════════════════════

class App:
    """项目管理器"""

    def __init__(self):
        self.term = Terminal()
        self.projects = []
        self.visible = []       # 过滤后的索引
        self.selected = set()   # 多选的索引
        self.query = ''         # 搜索词
        self.cursor = 0         # 当前光标
        self.scroll = 0         # 滚动偏移
        self.list_height = 10   # 列表高度
        self.db_path = ''
        self.vscode = ''
        self.running = True
        self.message = ''       # 底部消息
        self.search_mode = False
        self.last_deleted = []  # 最近删除的项目（用于撤销）
        self.confirm_delete = False  # 删除确认模式
        self.pending_delete = []     # 待删除的索引

    def filter(self):
        """过滤项目"""
        if not self.query:
            self.visible = list(range(len(self.projects)))
        else:
            q = self.query.lower()
            self.visible = [
                i for i, p in enumerate(self.projects)
                if q in p['name'].lower() or q in p['path'].lower()
            ]

        # 修正光标
        if self.cursor >= len(self.visible):
            self.cursor = max(0, len(self.visible) - 1)

        # 修正滚动
        if self.cursor < self.scroll:
            self.scroll = self.cursor
        elif self.cursor >= self.scroll + self.list_height:
            self.scroll = self.cursor - self.list_height + 1

    def draw(self):
        """绘制界面"""
        rows, cols = self.term.size()
        self.list_height = rows - 8  # 留更多空间给帮助栏
        if self.list_height < 3:
            self.list_height = 3

        # 确保滚动范围正确（处理尺寸变化）
        if self.visible:
            if self.cursor >= len(self.visible):
                self.cursor = len(self.visible) - 1
            if self.cursor < self.scroll:
                self.scroll = self.cursor
            elif self.cursor >= self.scroll + self.list_height:
                self.scroll = self.cursor - self.list_height + 1
            max_scroll = max(0, len(self.visible) - self.list_height)
            if self.scroll > max_scroll:
                self.scroll = max_scroll

        # 布局计算 - 给名称更多空间
        name_w = min(45, max(25, cols * 40 // 100))
        path_w = cols - name_w - 14  # 减少前缀占用
        if path_w < 15:
            path_w = 15

        lines = []

        # ─────────────────────────────────────────────────
        # 标题栏
        # ─────────────────────────────────────────────────
        total = len(self.visible)
        pos_info = f'{C.GRAY}{self.cursor + 1}/{total}{C.RST}' if total > 0 else ''
        sel_info = f'{C.LGREEN}[{len(self.selected)} 已选]{C.RST} ' if self.selected else ''
        title = f'{C.BOLD}{C.LCYAN} 📂 VSCode Projects{C.RST}  {sel_info}{pos_info}'
        lines.append(title)
        lines.append(f'{C.GRAY}{"─" * (cols - 1)}{C.RST}')

        # ─────────────────────────────────────────────────
        # 搜索框 (fzf 风格)
        # ─────────────────────────────────────────────────
        if self.search_mode:
            prompt = f'{C.LGREEN}❯{C.RST} '
            cursor_char = f'{C.REVERSE} {C.RST}'
            lines.append(f' {prompt}{self.query}{cursor_char}')
        else:
            if self.query:
                lines.append(f' {C.LGREEN}❯{C.RST} {self.query} {C.GRAY}(Esc清除){C.RST}')
            else:
                lines.append(f' {C.GRAY}/ 搜索{C.RST}')

        lines.append(f'{C.GRAY}{"─" * (cols - 1)}{C.RST}')

        # ─────────────────────────────────────────────────
        # 项目列表
        # ─────────────────────────────────────────────────
        total = len(self.visible)
        end = min(self.scroll + self.list_height, total)

        for i in range(self.scroll, end):
            idx = self.visible[i]
            p = self.projects[idx]
            is_cur = (i == self.cursor)
            is_sel = (idx in self.selected)
            is_invalid = not p.get('exists', True)  # 失效项目

            # 选择指示器
            if is_sel:
                marker = f'{C.LGREEN}[✓]{C.RST}'
            else:
                marker = f'{C.GRAY}[ ]{C.RST}'

            # 光标指示器
            if is_cur:
                pointer = f'{C.LCYAN}❯{C.RST}'
            else:
                pointer = ' '

            # 图标 - 失效项目使用灰色图标
            if is_invalid:
                if p['type'] == 'folder':
                    icon = f'{C.GRAY}📁{C.RST}'
                elif p['type'] == 'file':
                    icon = f'{C.GRAY}📄{C.RST}'
                else:
                    icon = f'{C.GRAY}📦{C.RST}'
            elif p['type'] == 'folder':
                icon = f'{C.LYELLOW}📁{C.RST}'
            elif p['type'] == 'file':
                icon = f'{C.LBLUE}📄{C.RST}'
            else:
                icon = f'{C.LMAGENTA}📦{C.RST}'

            # 名称（不包含颜色代码）
            name = p['name']
            tag_str = ''
            if p['tag']:
                tag_str = f" [{p['tag']}]"
                name = name + tag_str

            # 失效项目添加标记
            if is_invalid:
                name = name + ' [无效]'

            name_display = str_cut(name, name_w)
            name_padded = str_pad(name_display, name_w)

            # 路径 - 有转换路径时优先显示转换路径
            show_path = p['path']
            if p.get('display_path'):
                show_path = os.path.dirname(p['display_path']) or '/'
            path_display = str_cut(show_path, path_w)
            path_padded = str_pad(path_display, path_w)

            # 组装行
            if is_invalid:
                # 失效项目 - 暗淡灰色样式
                name_colored = f'{C.DIM}{C.GRAY}{name_padded}{C.RST}'
                path_colored = f'{C.DIM}{C.GRAY}{path_padded}{C.RST}'
                line = f' {pointer} {marker} {icon} {name_colored} {path_colored}'
            elif is_cur:
                # 高亮当前行
                if p['tag']:
                    tag_start = name_padded.find('[')
                    if tag_start >= 0:
                        name_before = name_padded[:tag_start]
                        name_after = name_padded[tag_start:]
                        name_colored = f'{C.BOLD}{C.WHITE}{name_before}{C.LCYAN}{name_after}{C.RST}'
                    else:
                        name_colored = f'{C.BOLD}{C.WHITE}{name_padded}{C.RST}'
                else:
                    name_colored = f'{C.BOLD}{C.WHITE}{name_padded}{C.RST}'
                line = f' {pointer} {marker} {icon} {name_colored} {C.GRAY}{path_padded}{C.RST}'
            else:
                # 普通行
                if p['tag']:
                    tag_start = name_padded.find('[')
                    if tag_start >= 0:
                        name_before = name_padded[:tag_start]
                        name_after = name_padded[tag_start:]
                        name_colored = f'{C.WHITE}{name_before}{C.CYAN}{name_after}{C.RST}'
                    else:
                        name_colored = f'{C.WHITE}{name_padded}{C.RST}'
                else:
                    name_colored = f'{C.WHITE}{name_padded}{C.RST}'
                line = f' {pointer} {marker} {icon} {name_colored} {C.DIM}{path_padded}{C.RST}'

            lines.append(line)

        # 填充空行
        while len(lines) - 4 < self.list_height:
            lines.append('')

        # ─────────────────────────────────────────────────
        # 状态消息
        # ─────────────────────────────────────────────────
        lines.append(f'{C.GRAY}{"─" * (cols - 1)}{C.RST}')

        if self.message:
            lines.append(f' {C.LYELLOW}💡 {self.message}{C.RST}')
        else:
            # 当前项目信息
            if self.visible:
                idx = self.visible[self.cursor]
                p = self.projects[idx]
                is_invalid = not p.get('exists', True)

                # 有转换路径时显示转换后的路径
                if p.get('display_path'):
                    info = f'{C.LCYAN}{p["display_path"]}{C.RST}'
                else:
                    info = f'{C.WHITE}{p["full_path"]}{C.RST}'

                # 失效项目显示警告
                if is_invalid:
                    show_full = p.get('display_path') or p['full_path']
                    lines.append(f' {C.LYELLOW}⚠️  路径不存在:{C.RST} {C.DIM}{show_full}{C.RST}')
                else:
                    lines.append(f' {C.DIM}路径:{C.RST} {info}')
            else:
                lines.append(f' {C.GRAY}无匹配项目{C.RST}')

        # ─────────────────────────────────────────────────
        # 帮助栏 - 按功能分区
        # ─────────────────────────────────────────────────
        lines.append(f'{C.GRAY}{"─" * (cols - 1)}{C.RST}')

        if self.confirm_delete:
            # 删除确认模式
            help_line = f' {C.LRED}⚠️  删除确认:{C.RST} {C.LGREEN}y{C.RST} 确认删除  {C.LYELLOW}n{C.RST}/{C.LYELLOW}Esc{C.RST} 取消'
        elif self.search_mode:
            help_line = f' {C.LYELLOW}Enter{C.RST} 确认  {C.LYELLOW}Esc{C.RST} 取消  {C.GRAY}输入关键词过滤项目{C.RST}'
        else:
            # 分区显示 - 根据终端宽度调整
            if cols >= 100:
                nav = f'{C.LYELLOW}↑↓{C.RST}移动'
                sel = f'{C.LYELLOW}Space{C.RST}选择 {C.LYELLOW}a{C.RST}全选'
                opn = f'{C.LYELLOW}Enter{C.RST}当前窗口 {C.LYELLOW}n{C.RST}新窗口 {C.LYELLOW}w{C.RST}工作区'
                tool = f'{C.LYELLOW}y{C.RST}复制路径 {C.LYELLOW}o{C.RST}资源管理器'
                # 有可撤销内容时显示 u 撤销
                if self.last_deleted:
                    mng = f'{C.LYELLOW}d{C.RST}删除 {C.LGREEN}u{C.RST}撤销 {C.LYELLOW}/{C.RST}搜索 {C.LYELLOW}q{C.RST}退出'
                else:
                    mng = f'{C.LYELLOW}d{C.RST}删除 {C.LYELLOW}/{C.RST}搜索 {C.LYELLOW}q{C.RST}退出'
                help_line = f' {nav} {C.GRAY}│{C.RST} {sel} {C.GRAY}│{C.RST} {opn} {C.GRAY}│{C.RST} {tool} {C.GRAY}│{C.RST} {mng}'
            else:
                # 窄屏简化显示
                if self.last_deleted:
                    help_line = f' {C.LYELLOW}↑↓{C.RST}导航 {C.LYELLOW}Enter{C.RST}打开 {C.LYELLOW}Space{C.RST}选择 {C.LYELLOW}d{C.RST}删除 {C.LGREEN}u{C.RST}撤销 {C.LYELLOW}q{C.RST}退出'
                else:
                    help_line = f' {C.LYELLOW}↑↓{C.RST}导航 {C.LYELLOW}Enter{C.RST}打开 {C.LYELLOW}n{C.RST}新窗口 {C.LYELLOW}Space{C.RST}选择 {C.LYELLOW}/{C.RST}搜索 {C.LYELLOW}q{C.RST}退出'

        lines.append(help_line)

        # ─────────────────────────────────────────────────
        # 输出
        # ─────────────────────────────────────────────────
        for i, line in enumerate(lines):
            self.term.goto(i + 1, 1)
            self.term.clear_line()
            self.term.write(line)

        # 清除多余行
        for i in range(len(lines), rows):
            self.term.goto(i + 1, 1)
            self.term.clear_line()

        self.term.flush()

    def open_projects(self, indices, new_window=False, as_workspace=False):
        """打开项目"""
        if not indices:
            return

        if as_workspace and len(indices) > 1:
            # 作为工作区打开
            folders = []
            for idx in indices:
                p = self.projects[idx]
                if p['uri'].startswith('file://'):
                    parsed = urlparse(p['uri'])
                    path = unquote(parsed.path)
                    if len(path) > 2 and path[0] == '/' and path[2] == ':':
                        path = path[1:]
                    folders.append({'path': path})

            if folders:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.code-workspace', delete=False) as f:
                    json.dump({'folders': folders}, f)
                    ws_path = f.name
                # Windows 上需要 shell=True 来执行 .cmd 文件
                shell = IS_WINDOWS and self.vscode.endswith('.cmd')
                subprocess.Popen([self.vscode, ws_path],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                shell=shell)
        else:
            # 逐个打开
            for i, idx in enumerate(indices):
                p = self.projects[idx]
                uri = p['uri']

                if uri.startswith('vscode-remote://'):
                    args = [self.vscode, '--folder-uri', uri]
                    if new_window or i > 0:
                        args.insert(1, '--new-window')
                else:
                    parsed = urlparse(uri)
                    path = unquote(parsed.path)
                    if len(path) > 2 and path[0] == '/' and path[2] == ':':
                        path = path[1:]

                    args = [self.vscode]
                    if new_window or i > 0:
                        args.append('-n')
                    else:
                        args.append('-r')
                    args.append(path)

                # Windows 上需要 shell=True 来执行 .cmd 文件
                shell = IS_WINDOWS and self.vscode.endswith('.cmd')
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                shell=shell)

    def _do_delete(self, indices):
        """执行删除操作"""
        if not indices:
            return

        # 保存要删除的项目（用于撤销）
        deleted_projects = [self.projects[i] for i in indices]
        self.last_deleted = deleted_projects

        # 过滤掉要删除的
        uris_to_del = {self.projects[i]['uri'] for i in indices}
        new_projects = [p for p in self.projects if p['uri'] not in uris_to_del]

        # 保存
        save_projects(self.db_path, new_projects)

        # 重新加载
        self.projects = new_projects
        self.selected.clear()
        self.filter()

        self.message = f'🗑️ 已删除 {len(indices)} 个项目，按 u 撤销'

    def undo_delete(self):
        """撤销删除"""
        if not self.last_deleted:
            self.message = '没有可撤销的删除操作'
            return

        # 恢复删除的项目（插入到开头）
        restored = self.last_deleted
        self.projects = restored + self.projects
        self.last_deleted = []  # 清空撤销记录

        # 保存到数据库
        self._save_all_projects()

        self.filter()
        self.cursor = 0
        self.scroll = 0
        self.message = f'✅ 已恢复 {len(restored)} 个项目'

    def _save_all_projects(self):
        """保存所有项目到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key='history.recentlyOpenedPathsList'")
            row = cursor.fetchone()

            if row:
                data = json.loads(row[0])
                # 根据当前 projects 重建 entries
                keep_uris = {p['uri'] for p in self.projects}
                original_entries = {}
                for entry in data.get('entries', []):
                    uri = entry.get('folderUri') or entry.get('fileUri') or \
                          (entry.get('workspace', {}) or {}).get('configPath', '')
                    original_entries[uri] = entry

                # 重建 entries 列表，保持当前顺序
                new_entries = []
                for p in self.projects:
                    if p['uri'] in original_entries:
                        new_entries.append(original_entries[p['uri']])

                data['entries'] = new_entries
                cursor.execute("UPDATE ItemTable SET value=? WHERE key='history.recentlyOpenedPathsList'",
                              (json.dumps(data, ensure_ascii=False),))
                conn.commit()

            conn.close()
        except:
            pass

    def handle_key(self, key):
        """处理按键"""
        if key is None:
            return

        self.message = ''  # 清除消息

        # ─────────────────────────────────────────────────
        # 鼠标点击处理
        # ─────────────────────────────────────────────────
        if isinstance(key, tuple) and key[0] == 'MOUSE_CLICK':
            _, x, y = key
            # 计算点击的是哪一行项目
            # 项目列表从第 5 行开始 (标题1 + 分隔1 + 搜索1 + 分隔1 = 4)
            list_start_row = 5
            list_end_row = list_start_row + self.list_height

            if list_start_row <= y < list_end_row and self.visible:
                # 计算点击的是列表中的第几项
                clicked_index = y - list_start_row + self.scroll
                if 0 <= clicked_index < len(self.visible):
                    # 移动光标到点击位置
                    self.cursor = clicked_index
                    # 切换选中状态
                    idx = self.visible[clicked_index]
                    if idx in self.selected:
                        self.selected.remove(idx)
                    else:
                        self.selected.add(idx)
            return

        # ─────────────────────────────────────────────────
        # 搜索模式
        # ─────────────────────────────────────────────────
        if self.search_mode:
            if key == 'ESC':
                self.search_mode = False
            elif key == 'ENTER':
                self.search_mode = False
            elif key == 'BACKSPACE':
                if self.query:
                    self.query = self.query[:-1]
                    self.filter()
                else:
                    self.search_mode = False
            elif key == 'CTRL_C':
                self.query = ''
                self.search_mode = False
                self.filter()
            elif isinstance(key, str) and len(key) == 1 and key.isprintable():
                self.query += key
                self.filter()
            return

        # ─────────────────────────────────────────────────
        # 删除确认模式
        # ─────────────────────────────────────────────────
        if self.confirm_delete:
            if key in ('y', 'Y'):
                # 确认删除
                self._do_delete(self.pending_delete)
                self.confirm_delete = False
                self.pending_delete = []
            elif key in ('n', 'N', 'ESC', 'CTRL_C'):
                # 取消删除
                self.confirm_delete = False
                self.pending_delete = []
                self.message = '已取消删除'
            # 其他按键忽略，保持确认状态
            return

        # ─────────────────────────────────────────────────
        # 普通模式
        # ─────────────────────────────────────────────────

        # 退出
        if key in ('q', 'Q', 'CTRL_C', 'CTRL_D'):
            self.running = False
            return

        if key == 'ESC':
            if self.query:
                self.query = ''
                self.filter()
            elif self.selected:
                self.selected.clear()
            else:
                self.running = False
            return

        # 导航
        if key == 'UP' or key == 'k':
            if self.cursor > 0:
                self.cursor -= 1
                if self.cursor < self.scroll:
                    self.scroll = self.cursor
            return

        if key == 'DOWN' or key == 'j':
            if self.cursor < len(self.visible) - 1:
                self.cursor += 1
                if self.cursor >= self.scroll + self.list_height:
                    self.scroll = self.cursor - self.list_height + 1
            return

        if key == 'PGUP':
            self.cursor = max(0, self.cursor - self.list_height)
            self.scroll = max(0, self.scroll - self.list_height)
            return

        if key == 'PGDN':
            max_cursor = len(self.visible) - 1
            self.cursor = min(max_cursor, self.cursor + self.list_height)
            max_scroll = max(0, len(self.visible) - self.list_height)
            self.scroll = min(max_scroll, self.scroll + self.list_height)
            return

        if key == 'HOME' or key == 'g':
            self.cursor = 0
            self.scroll = 0
            return

        if key == 'END' or key == 'G':
            self.cursor = max(0, len(self.visible) - 1)
            self.scroll = max(0, len(self.visible) - self.list_height)
            return

        # 搜索
        if key == '/':
            self.search_mode = True
            return

        # 多选 (空格)
        if key == ' ':
            if self.visible:
                idx = self.visible[self.cursor]
                if idx in self.selected:
                    self.selected.remove(idx)
                else:
                    self.selected.add(idx)
            return

        # 全选/取消全选
        if key in ('a', 'A'):
            if len(self.selected) == len(self.visible):
                self.selected.clear()
            else:
                self.selected = set(self.visible)
            return

        # Enter: 当前窗口打开并退出脚本
        if key == 'ENTER':
            if self.visible:
                if self.selected:
                    # 多选时在新窗口打开
                    self.open_projects(list(self.selected), new_window=True)
                else:
                    # 单选在当前窗口打开 (使用 -r 参数)
                    idx = self.visible[self.cursor]
                    self.open_projects([idx], new_window=False)
                self.running = False
            return

        # 新窗口打开 - 不退出，可继续操作
        if key in ('n', 'N'):
            if self.visible:
                if self.selected:
                    self.open_projects(list(self.selected), new_window=True)
                    self.message = f'已在新窗口打开 {len(self.selected)} 个项目'
                    self.selected.clear()
                else:
                    idx = self.visible[self.cursor]
                    p = self.projects[idx]
                    self.open_projects([idx], new_window=True)
                    self.message = f'已在新窗口打开: {p["name"]}'
                # 不退出，可继续操作
            return

        # 工作区打开 - 不退出
        if key in ('w', 'W'):
            if self.selected:
                self.open_projects(list(self.selected), as_workspace=True)
                self.message = f'已作为工作区打开 {len(self.selected)} 个项目'
                self.selected.clear()
            elif self.visible:
                idx = self.visible[self.cursor]
                p = self.projects[idx]
                self.open_projects([idx], new_window=True)
                self.message = f'已打开: {p["name"]}'
            # 不退出，可继续操作
            return

        # 删除
        if key in ('d', 'D'):
            if not self.visible:
                return
            # 进入删除确认模式
            if self.selected:
                self.pending_delete = list(self.selected)
            else:
                self.pending_delete = [self.visible[self.cursor]]
            self.confirm_delete = True
            count = len(self.pending_delete)
            names = ', '.join(self.projects[i]['name'] for i in self.pending_delete[:3])
            if count > 3:
                names += f' ... 等 {count} 项'
            self.message = f'❗ 确认删除 {names}？ (y)确认 (n/Esc)取消'
            return

        # 刷新
        if key in ('r', 'R'):
            self.projects = load_projects(self.db_path)
            self.selected.clear()
            self.last_deleted = []  # 刷新后清除撤销记录
            self.filter()
            self.message = '✨ 已刷新项目列表'
            return

        # 复制路径到剪贴板
        if key in ('y', 'Y'):
            if self.visible:
                idx = self.visible[self.cursor]
                p = self.projects[idx]
                path = p['full_path']
                if copy_to_clipboard(path):
                    self.message = f'📋 已复制路径: {p["name"]}'
                else:
                    self.message = f'❌ 复制失败，请安装 xclip 或 xsel'
            return

        # 在资源管理器中打开
        if key in ('o', 'O'):
            if self.visible:
                idx = self.visible[self.cursor]
                p = self.projects[idx]
                # 优先打开目录，如果是文件则打开所在目录
                path = p['full_path'] if p['type'] == 'folder' else p['path']
                if open_in_file_manager(path):
                    self.message = f'📂 已在资源管理器中打开: {p["name"]}'
                else:
                    self.message = f'❌ 无法打开资源管理器'
            return

        # 撤销删除
        if key in ('u', 'U'):
            self.undo_delete()
            return

        # 清空搜索
        if key == 'BACKSPACE':
            if self.query:
                self.query = ''
                self.filter()
            return

    def run(self):
        """运行"""
        # 检查
        self.vscode = get_vscode_cmd(CUSTOM_CODE_PATH)
        if not self.vscode:
            print(f'{C.RED}错误: 未找到 VSCode 命令{C.RST}')
            print(f'{C.GRAY}提示: 使用 --code 参数指定 VSCode 路径{C.RST}')
            print(f'{C.GRAY}例如: vscode-projects --code "C:\\path\\to\\code.cmd"{C.RST}')
            return 1

        self.db_path = get_db_path(CUSTOM_DB_PATH)
        if not self.db_path or not os.path.exists(self.db_path):
            print(f'{C.RED}错误: 未找到 VSCode 数据库{C.RST}')
            print(f'{C.GRAY}路径: {self.db_path}{C.RST}')
            if not CUSTOM_DB_PATH:
                print(f'{C.GRAY}提示: 使用 --db 参数指定数据库路径{C.RST}')
                print(f'{C.GRAY}例如: vscode-projects --db "path/to/state.vscdb"{C.RST}')
            return 1

        # 加载
        self.projects = load_projects(self.db_path)

        if not self.projects:
            print(f'{C.YELLOW}没有最近打开的项目{C.RST}')
            return 0

        self.filter()

        # 启动终端
        self.term.start()

        try:
            while self.running:
                self.draw()
                key = self.term.read_key()
                self.handle_key(key)
        finally:
            self.term.stop()

        return 0


# ═══════════════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════════════

def show_help():
    print(f'''
{C.BOLD}{C.LCYAN}📂 VSCode Projects Manager v1.0.0{C.RST}
{C.GRAY}跨平台 VSCode 最近项目管理器 - 支持 Windows/macOS/Linux/WSL{C.RST}

{C.BOLD}用法:{C.RST}
  vscode-projects [选项]

{C.BOLD}选项:{C.RST}
  -h, --help          显示帮助
  -l, --list          列出项目
  -v, --version       版本信息
  -c, --code <path>   指定 VSCode 可执行文件路径
  -d, --db <path>     指定 state.vscdb 数据库路径

{C.BOLD}示例:{C.RST}
  vscode-projects                            # 交互模式
  vscode-projects -l                         # 列出所有项目
  vscode-projects --code "C:\\path\\code.cmd"  # 指定 VSCode 路径
  vscode-projects --db "path/to/state.vscdb"  # 指定数据库路径

{C.BOLD}快捷键 - 导航:{C.RST}
  {C.YELLOW}↑/↓ j/k{C.RST}    上下移动
  {C.YELLOW}鼠标点击{C.RST}   点击项目移动光标
  {C.YELLOW}滚轮{C.RST}       上下滚动
  {C.YELLOW}PgUp/PgDn{C.RST}  翻页
  {C.YELLOW}g/G{C.RST}        跳到开头/结尾

{C.BOLD}快捷键 - 选择:{C.RST}
  {C.YELLOW}Space{C.RST}      选择/取消当前项
  {C.YELLOW}a{C.RST}          全选/取消全选

{C.BOLD}快捷键 - 打开:{C.RST}
  {C.YELLOW}Enter{C.RST}      当前窗口打开并退出
  {C.YELLOW}n{C.RST}          新窗口打开 (不退出)
  {C.YELLOW}w{C.RST}          多选项目作为工作区打开 (不退出)

{C.BOLD}快捷键 - 工具:{C.RST}
  {C.YELLOW}y{C.RST}          复制当前项目路径到剪贴板
  {C.YELLOW}o{C.RST}          在资源管理器中打开

{C.BOLD}快捷键 - 管理:{C.RST}
  {C.YELLOW}/{C.RST}          进入搜索模式
  {C.YELLOW}Esc{C.RST}        清除搜索 → 取消选择 → 退出
  {C.YELLOW}d{C.RST}          删除记录
  {C.YELLOW}u{C.RST}          撤销删除（未被其他操作覆盖时可用）
  {C.YELLOW}r{C.RST}          刷新列表
  {C.YELLOW}q{C.RST}          退出
''')


def list_projects():
    db_path = get_db_path(CUSTOM_DB_PATH)
    projects = load_projects(db_path)
    for p in projects:
        tag = f" [{p['tag']}]" if p['tag'] else ''
        invalid = '' if p.get('exists', True) else f' {C.DIM}[无效]{C.RST}'
        icon = '📁' if p['type'] == 'folder' else '📄' if p['type'] == 'file' else '📦'
        print(f"{icon} {C.WHITE}{p['name']}{C.RST}{C.CYAN}{tag}{C.RST}{invalid}")
        # 显示路径，有转换路径时显示转换后的
        show_path = p.get('display_path') or p['full_path']
        print(f"  {C.GRAY}{show_path}{C.RST}")


# 全局变量：用户指定的路径
CUSTOM_CODE_PATH = None
CUSTOM_DB_PATH = None

def main():
    global CUSTOM_CODE_PATH, CUSTOM_DB_PATH

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('-h', '--help'):
            show_help()
            return 0
        elif arg in ('-l', '--list'):
            list_projects()
            return 0
        elif arg in ('-v', '--version'):
            print('v1.0.0')
            return 0
        elif arg in ('-c', '--code'):
            if i + 1 < len(sys.argv):
                CUSTOM_CODE_PATH = sys.argv[i + 1]
                i += 1
            else:
                print(f'{C.RED}错误: --code 需要指定路径{C.RST}')
                return 1
        elif arg in ('-d', '--db'):
            if i + 1 < len(sys.argv):
                CUSTOM_DB_PATH = sys.argv[i + 1]
                i += 1
            else:
                print(f'{C.RED}错误: --db 需要指定路径{C.RST}')
                return 1
        i += 1

    return App().run()


if __name__ == '__main__':
    sys.exit(main())
