# 状态机工作流程 v3

> 随 auto_farm.py 同步更新。状态 0~38。

## 运行

```
python auto_farm.py              # 从步骤0开始
python auto_farm.py --skip-setup # 跳过选英雄，从步骤5开始
python auto_farm.py --debug      # 调试模式
```

## 架构

**状态机**：state 变量（0~38）通过 if/elif 分发，每步完成后设 state = 下个步骤。

## 统一操作模式

```
等 STEP_WAIT(1s) → 点击上一步识别的目标 → 识别下一目标 → 成功→ state=下步 / 超时(10s)→ state=当前步
```

## 步骤5 / 16 / 22：截图缓存

每轮迭代截一张图，同一帧匹配所有模板，确保优先级严格。

## 全局状态

`State` dataclass 封装三个全局变量：
- `st.saved_center` — 上一步识别到的图片中心
- `st.hero_coord` — 步骤16记录英雄类型坐标
- `st.feifei_coord` — 步骤22记录飞飞类型坐标

## 状态转换表

| 步骤 | 点击 | 识别 | 成功 | 超时 | 备注 |
|------|------|------|------|------|------|
| 0 | — | select_hero | 1 | 0 | 等3s |
| 1 | select_hero 中心 | hero_lvbu | 2 | 1 | |
| 2 | hero_lvbu 中心 | select_lvbu | 3 | 2 | |
| 3 | (960,540) | start_challenge | 4 | 3 | |
| 4 | start_challenge 中心 | start_QL | 5 | 4 | |
| **5** | — | **7分支轮询** | **见下** | **sys.exit** | 截图缓存，30s超时退出 |
| 6 | challenge_icon 中心 | start_battle | 7 | 6 | |
| 7 | start_battle 中心 | setting | 8 | 7 | |
| 8 | setting 中心 | setting_icon | 9 | 8 | |
| 9 | 识别 close_refresh→点击 | host | 10 | 9 | 内嵌点击 |
| 10 | host 中心 | hosting | 11 | 10 | |
| 11 | — | battle_end_click | 12 | 11 | 无点击 |
| 12 | battle_end_click 中心 | battle_end_next_step | 13 | 12 | |
| 13 | battle_end_next_step 中心 | battle_end_confirm | 14 | 13 | |
| **14** | battle_end_confirm 中心 | token_hero→get_rewards→start_QL | 15/30/5 | 14 | 三级嵌套超时 |
| 15 | (960,540) | select_token | 16 | 15 | |
| 16 | — | 5英雄图→记录坐标 | 17 | 16 | 截图缓存 |
| 17 | 步骤16记录坐标 | start_QL→wujiangjineng | 5/38 | 17 | 嵌套超时 |
| **18** | **双击** shop 中心 | shop_check | 19 | 18 | |
| 19 | (1840,60) | close_shop | 20 | 19 | |
| 20 | close_shop 中心 | start_QL | 5 | 20 | |
| 21 | pet_feifei 中心 | pet_select | 22 | 21 | |
| 22 | pet_select 中心 | 3飞飞图→记录坐标 | 23 | 22 | 截图缓存 |
| 23 | 步骤22记录坐标 | start_QL | 5 | 23 | |
| 24 | pet_kaka 中心 | pet_select | 25 | 24 | |
| 25 | pet_select 中心 | kaka_refuse | 26 | 25 | |
| 26 | kaka_refuse 中心 | kaka_stop | 27 | 26 | |
| 27 | kaka_stop 中心 | start_QL | 5 | 27 | |
| 28 | stop_challenge 中心 | close_shop | 29 | 28 | |
| 29 | close_shop 中心 | get_rewards | 30 | 29 | |
| 30 | get_rewards 中心 | close_challenge | 31 | 30 | |
| 31 | close_challenge 中心 | select_hero | 0 | 31 | |
| **32** | **双击** wujiang_scs 中心 | pet_select | 33 | 32 | 十常侍 |
| 33 | pet_select 中心 | scs_check | 34 | 33 | |
| 34 | (350,350) | setting | 8 | 34 | 回到设置 |
| **35** | **双击** wujiang_zgl 中心 | wujiang_select | 36 | 35 | 诸葛亮 |
| 36 | wujiang_select 中心 | zgl_check | 37 | 36 | |
| 37 | (1450,500) 双击 | wujiangjineng | 38 | 37 | |
| 38 | (1000,1000) | start_QL | 5 | 38 | 回到主界面 |

## 步骤5 7分支检测

| 优先级 | 识别 | 动作 | 跳转 |
|--------|------|------|------|
| (1) | challenge_icon | 记录中心 | 6 |
| (2) | shop_baqing / shop_lvbuwei | 记录中心 | 18 |
| (3) | pet_feifei | 记录中心 | 21 |
| (4) | pet_kaka | 记录中心 | 24 |
| (5) | wujiang_scs | 记录中心 | 32 |
| (6) | wujiang_zgl | 记录中心 | 35 |
| (7) | stop_challenge | 记录中心 | 28 |

超时(30s)：无匹配 → `sys.exit(1)` 退出脚本

## 步骤14 嵌套超时（三级）

```
detect_until("select_token_hero.png")
  成功 → state=15
  超时 → detect_until("get_rewards.png")
           成功 → state=30
           超时 → detect_until("start_QL.png")
                    成功 → state=5
                    超时 → state=14（重启）
```

## 步骤16 / 22 子检测

截图缓存 + 轮询按优先级依次匹配，命中第一个记录坐标。

## 函数速查

| 函数 | 作用 |
|------|------|
| detect_until(filename, timeout) | 循环识别，返回 Point 或 None |
| locate_center(filename) | 单次识别，返回 Point 或 None |
| locate_center_in_screenshot(filename, screenshot) | 在已有截图中查找 |
| step_click_center / step_click_pos | 单击 |
| step_double_click_center | 双击 |
| step_detect(filename) | 循环识别（不含sleep） |
| step_multi_detect(images) | 截图+轮询多图，返回 (center, filename) 或 (None, None) |

## 配置参数

| 参数 | 值 | 说明 |
|------|-----|------|
| STEP_WAIT | 1s | 步骤内等待 |
| DETECT_TIMEOUT | 10s | 单步识别超时 |
| STEP5_TIMEOUT | 30s | 步骤5分支检测超时 |
| RETRY_INTERVAL | 0.5s | 重试间隔 |
| CURSOR_CENTER | (960,540) | 屏幕中心 |
| POS_STEP19 | (1840,60) | 商店返回按钮 |
| POS_STEP34 | (350,350) | 十常侍点击位置 |
| POS_STEP37 | (1450,500) | 诸葛亮卜卦位置 |
| POS_STEP38 | (1000,1000) | 从属性面板返回千里 |
