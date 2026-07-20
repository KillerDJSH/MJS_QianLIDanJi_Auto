@echo off
chcp 65001 >nul
echo ====================================
echo   QL_AutoFarm - PyInstaller 构建
echo ====================================
echo.
echo [1/2] 安装 PyInstaller...
pip install pyinstaller
echo.
echo [2/2] 构建 QL_AutoFarm.exe...
pyinstaller --clean auto_farm.spec
echo.
echo ====================================
echo   构建完成！
echo   输出文件: dist\QL_AutoFarm.exe
echo ====================================
echo.
echo 发给别人直接用，无需安装 Python。
pause
