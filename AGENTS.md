# AGENTS.md — 游戏自动刷代币脚本

## 项目概述

基于 pyautogui + opencv-python 的游戏自动化脚本，通过屏幕图片识别和鼠标点击实现自动刷代币。

## 运行

```powershell
python auto_farm.py              # 交互菜单选择模式
python auto_farm.py --skip-setup # 跳过菜单，直接从战斗循环开始
python auto_farm.py --debug      # 调试模式
```

无命令行参数时，`main()` 会弹出交互菜单让用户选择 `[1] 完整流程` 或 `[2] 跳过选英雄`。

停止：`Ctrl+C` 或鼠标移到屏幕左上角（FAILSAFE）。

## 依赖

```
pyautogui==0.9.54
opencv-python==4.10.0.84
Pillow>=10.0.0
```

## 架构：状态机驱动

**核心机制**：`state` 变量（0~38）通过 `if/elif` 分发，每步完成后直接设 `state = 下个步骤编号`。

```python
while True:
    if state == 0:
        if 成功: state = 1
        else:    state = 0   # 超时重启
    elif state == 1:
        ...
```

## 统一步骤模式

大多数步骤遵循：

```python
time.sleep(STEP_WAIT)                          # 等1s
step_click_center(st.saved_center)             # 点击上一步识别的目标
center = step_detect("image.png", timeout=10)  # 循环识别（不含额外sleep）
if center:                                      # 成功
    st.saved_center = center
    state = 下个步骤
else:                                           # 超时
    state = 当前步骤（重启）
```

### 全局状态

所有状态变量封装在 `State` dataclass 中，全局实例 `st`：

```python
@dataclass
class State:
    saved_center   # 存上一步识别到的图片中心，供下一步点击
    hero_coord     # 步骤16记录
    feifei_coord   # 步骤22记录
```

### 关键函数

| 函数 | 作用 |
|------|------|
| `detect_until(filename, timeout)` | 循环识别，返回 center Point 或 None。`timeout=None` 无限等待 |
| `locate_center(filename)` | 单次识别，返回 Point 或 None（无循环） |
| `locate_center_in_screenshot(filename, screenshot)` | 在已有截图中查找，用于步骤5/16/22 的截图缓存 |
| `step_click_center(center)` | 点击图片中心 |
| `step_click_pos(x, y)` | 点击固定坐标 |
| `step_double_click_center(center)` | 双击 |
| `step_detect(filename, timeout)` | 循环识别（不含前置sleep，由调用方自行sleep） |
| `step_multi_detect(images, timeout)` | 截图+轮询多张图，返回 `(center, filename)` 或 `(None, None)` |

## 特殊步骤

### 步骤5：7 分支检测
使用 `locate_center_in_screenshot()` 在 `while True` 内同一帧按优先级轮询，命中即 `state = 目标值 + break`。超时 `STEP5_TIMEOUT`(30s) 直接退出脚本。优先顺序：
(1) challenge_icon → (2) shop_baqing/shop_lvbuwei → (3) pet_feifei → (4) pet_kaka → (5) wujiang_scs → (6) wujiang_zgl → (7) stop_challenge

### 步骤9：内嵌点击
先识别 `close_refresh.png` 并点击，再识别 `host.png`。

### 步骤11：无点击
仅识别，不点击。

### 步骤14：三级嵌套超时
select_token_hero 超时 → 检测 get_rewards → 成功则 state=30，超时 → 检测 start_QL → 成功则 state=5，超时则重启步骤14。

### 步骤16 & 22：截图缓存 + 子检测
`pyautogui.screenshot()` + `locate_center_in_screenshot()` 同一帧按优先级匹配多张图，命中即记录坐标。步骤16存 `hero_coord`，步骤22存 `feifei_coord`。

### 步骤18：双击
`step_double_click_center()` 而非单击。

### 步骤0：3s 等待
步骤0 等待 3s（非 STEP_WAIT），其余步骤等 1s。

## 配置

`config.py` 是所有可调参数的唯一来源：

- `STEP_WAIT` — 步骤前等待秒数（1s）
- `DETECT_TIMEOUT` — 单步识别超时秒数（10s）
- `STEP5_TIMEOUT` — 步骤5分支检测超时秒数（30s），超时退出脚本
- `CURSOR_CENTER` — 屏幕中心坐标 `(960, 540)`
- `POS_STEP19` — 步骤19固定坐标 `(1840, 60)`
- `POS_STEP34` — 步骤34固定坐标 `(350, 350)`
- `POS_STEP37` — 步骤37固定坐标 `(1450, 500)`
- `POS_STEP38` — 步骤38固定坐标 `(1000, 1000)`

修改任何参数只需改 `config.py`，无需动 `auto_farm.py`。

## 添加新步骤

1. 在 `config.py` 添加坐标（如需要）
2. 在 `auto_farm.py` 的 `while True:` 内插入一个新的 `elif state == N:` 块
3. 成功时 `state = 下个步骤`，失败时 `state = 回退步骤`

## 打包为 .exe

使用 PyInstaller 打包为独立可执行文件：

```powershell
# 双击 build_exe.bat 或手动执行：
pip install pyinstaller
pyinstaller --clean auto_farm.spec
```

产物在 `dist/QL_AutoFarm.exe`（约67MB），发给他人无需 Python 环境。

### 关键点

- `config.py` 使用 `sys._MEIPASS` 适配 frozen 环境，确保 `image/` 目录在打包后仍能正确定位
- `auto_farm.spec` 通过 `Tree('image', prefix='image')` 将全部模板图片打入包内
- `hiddenimports` 显式列出 opencv、numpy、PIL 等隐式依赖，防止遗漏
