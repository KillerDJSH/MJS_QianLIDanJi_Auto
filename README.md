# 游戏自动刷代币脚本

基于 pyautogui + opencv-python 的屏幕图片识别自动化脚本，通过识别游戏画面上的按钮并自动点击实现刷代币。

## 方式一：直接使用 .exe（推荐，无需安装 Python）

直接双击 `QL_AutoFarm.exe`，会弹出启动菜单：

```
  请选择启动模式：
  [1] 完整流程    - 从选择英雄开始
  [2] 跳过选英雄  - 直接从战斗循环开始
```

输入 1 或 2 后按回车即可。

也支持命令行参数（右键 .exe → 在终端中打开）：

```powershell
.\QL_AutoFarm.exe --skip-setup   # 跳过菜单，直接战斗循环
.\QL_AutoFarm.exe --debug        # 调试模式
```

`QL_AutoFarm.exe` 位于 `dist/` 目录中，发给别人直接用，无需安装任何环境。

## 方式二：Python 运行（开发者/调试用）

### 前置要求

- Windows 系统（macOS/Linux 未测试）
- Python 3.10+

### 安装

```powershell
pip install -r requirements.txt
```

如果下载慢，使用清华镜像：

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 使用

```powershell
python auto_farm.py              # 交互菜单选择模式
python auto_farm.py --skip-setup # 跳过菜单，直接战斗循环
python auto_farm.py --debug      # 调试模式，输出每帧识别状态
```

**运行前确保游戏窗口完全可见，不被其他窗口遮挡。**

## 停止

- 关闭控制台窗口
- 按 `Ctrl+C`
- 鼠标移到屏幕左上角可紧急停止
- 步骤5 分支检测超时（30s）会自动退出脚本

## 参数调整

如果点击位置不准或图片识别不到，编辑 `config.py`：

| 参数 | 作用 |
|------|------|
| `CURSOR_CENTER` | 屏幕中心坐标，根据你的分辨率调整 |
| `POS_STEP19/34/37/38` | 各步骤固定点击坐标 |
| `CONFIDENCE` | 图片匹配置信度（0~1），越低越宽松，越高越精确 |
| `STEP_WAIT` | 步骤间等待秒数 |
| `DETECT_TIMEOUT` | 单步识别超时秒数 |
| `STEP5_TIMEOUT` | 步骤5分支检测超时秒数，超时退出脚本 |
| `CLICK_MOVE_DURATION` | 鼠标移动速度 |
| `CLICK_PRESS_DURATION` | 按压保持时间，太小可能导致点击无效 |

## 常见问题

### 点击了但游戏没反应

右键 PowerShell 选择"以管理员身份运行"，部分游戏需要管理员权限才能接收模拟点击。同时尝试将 `CLICK_PRESS_DURATION` 调大到 0.25。

### 图片识别不到

- 确认游戏画面没有被遮挡
- 降低 `CONFIDENCE`（如 0.7）
- 如果屏幕分辨率不同，`image/` 目录中的模板图片需要重新截图替换（默认分辨率为1920*1080无缩放）

### 点击位置偏移

修改 `config.py` 中的 `CURSOR_CENTER` 和所有 `POS_*` 坐标为你当前分辨率的对应位置。

## 模板图片

`image/` 目录包含脚本使用的所有识别模板。如果更换设备/分辨率，需要用新分辨率的截图替换这些文件。

## 依赖

- pyautogui==0.9.54 — 屏幕截图、鼠标控制
- opencv-python==4.10.0.84 — 图片模板匹配
- Pillow>=10.0.0 — 图像处理

## 注意事项

1. 已适配以下步骤：战斗、商店、宠物（腓腓/卡卡）、十常侍、诸葛亮。未做墨子、左慈、火堆、行囊的适配，当同时出现其中3个未适配项时，会自动结束千里单骑，开启下一轮千里。
2. 武将赠礼选择时，默认选择中间的武将，选择顺序为：驰援、资助、信物、武将牌、并肩作战。
3. 本脚本使用武将只有吕布，请确保你的吕布在第一页中。
4. 本脚本执行过程中需占用电脑屏幕
5. 如果 .exe 点击了游戏但没反应，以管理员身份运行 PowerShell，进入 .exe 所在目录执行 `.\QL_AutoFarm.exe`

## 开发者：构建 .exe

编辑代码后重新打包：

1. 双击 `build_exe.bat`（自动安装 PyInstaller 并构建）
2. 产物在 `dist/QL_AutoFarm.exe`
