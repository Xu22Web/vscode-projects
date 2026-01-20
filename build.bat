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

REM 清理旧文件
echo [2/4] 清理旧文件...
if exist dist\vscode-projects.exe del /f /q dist\vscode-projects.exe >nul 2>&1
if exist vscode-projects.exe del /f /q vscode-projects.exe >nul 2>&1

REM 编译
echo [3/4] 正在编译 Windows 版本...
cd /d "%~dp0"
%PYTHON_EXE% -m PyInstaller ^
    --onefile ^
    --console ^
    --name vscode-projects ^
    --clean ^
    --noconfirm ^
    --distpath dist/windows ^
    --workpath build/windows ^
    vscode-projects.py

if errorlevel 1 (
    echo [错误] 编译失败
    pause
    exit /b 1
)

REM 完成
echo.
echo [4/4] 编译完成!
echo.
echo ========================================
echo  编译结果
echo ========================================
echo.
echo Windows 可执行文件:
echo   %~dp0dist\windows\vscode-projects.exe
echo.
echo 文件大小:
for %%F in (dist\windows\vscode-projects.exe) do echo   %%~zF bytes
echo.
echo 使用方法:
echo   vscode-projects.exe        交互模式
echo   vscode-projects.exe -l     列出项目
echo   vscode-projects.exe -h     显示帮助
echo.

REM 复制到根目录（可选）
if exist dist\windows\vscode-projects.exe (
    copy /y dist\windows\vscode-projects.exe . >nul
    echo 已复制到: %~dp0vscode-projects.exe
)
echo.
pause
