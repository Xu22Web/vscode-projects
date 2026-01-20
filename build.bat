@echo off
chcp 65001 >nul
echo ========================================
echo  VSCode Projects Manager - Build Script
echo ========================================
echo.

REM 使用 PATH 中的 Python
set PYTHON_EXE=python
where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+ 并添加到 PATH
    pause
    exit /b 1
)

echo 使用 Python: %PYTHON_EXE%
%PYTHON_EXE% --version

REM 检查/安装 PyInstaller
echo.
echo [1/3] 检查 PyInstaller...
%PYTHON_EXE% -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo      正在安装 PyInstaller...
    %PYTHON_EXE% -m pip install pyinstaller --quiet
)

REM 编译
echo [2/3] 正在编译...
cd /d "%~dp0"
%PYTHON_EXE% -m PyInstaller ^
    --onefile ^
    --console ^
    --name vscode-projects ^
    --clean ^
    --noconfirm ^
    vscode-projects.py

if errorlevel 1 (
    echo [错误] 编译失败
    pause
    exit /b 1
)

REM 完成
echo.
echo [3/3] 编译完成!
echo.
echo 可执行文件位置: %~dp0dist\vscode-projects.exe
echo.
echo 使用方法:
echo   vscode-projects.exe        交互模式
echo   vscode-projects.exe -l     列出项目
echo   vscode-projects.exe -h     显示帮助
echo.

REM 复制到当前目录
copy /y dist\vscode-projects.exe . >nul
echo 已复制到: %~dp0vscode-projects.exe
echo.
pause
