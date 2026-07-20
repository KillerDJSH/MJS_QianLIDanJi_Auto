import os
import sys
import time
from dataclasses import dataclass

import pyautogui

import config

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

DEBUG = "--debug" in sys.argv
SKIP_SETUP = "--skip-setup" in sys.argv


@dataclass
class State:
    saved_center: object = None
    hero_coord: object = None
    feifei_coord: object = None


st = State()


def img_path(filename: str) -> str:
    return os.path.join(config.IMAGE_DIR, filename)


def locate_center(filename: str):
    path = img_path(filename)
    try:
        return pyautogui.locateCenterOnScreen(
            path, confidence=config.CONFIDENCE, grayscale=config.GRAYSCALE)
    except FileNotFoundError:
        print(f"  [错误] 图片缺失: {filename}")
        return None
    except Exception:
        return None


def locate_center_in_screenshot(filename: str, screenshot):
    path = img_path(filename)
    try:
        box = pyautogui.locate(
            path, screenshot,
            confidence=config.CONFIDENCE, grayscale=config.GRAYSCALE)
        if box is not None:
            return pyautogui.center(box)
        return None
    except Exception:
        return None


def do_click(x: int, y: int):
    pyautogui.moveTo(x, y, duration=config.CLICK_MOVE_DURATION)
    time.sleep(config.CLICK_STABILIZE_DELAY)
    pyautogui.mouseDown()
    time.sleep(config.CLICK_PRESS_DURATION)
    pyautogui.mouseUp()


def do_double_click(x: int, y: int):
    pyautogui.moveTo(x, y, duration=config.CLICK_MOVE_DURATION)
    time.sleep(config.CLICK_STABILIZE_DELAY)
    pyautogui.mouseDown()
    time.sleep(config.CLICK_PRESS_DURATION)
    pyautogui.mouseUp()
    time.sleep(config.CLICK_PRESS_DURATION)
    pyautogui.mouseDown()
    time.sleep(config.CLICK_PRESS_DURATION)
    pyautogui.mouseUp()


def detect_until(filename: str, timeout: float = None):
    start = time.time()
    while True:
        center = locate_center(filename)
        if center is not None:
            return center
        if timeout is not None and time.time() - start > timeout:
            return None
        time.sleep(config.RETRY_INTERVAL)


def step_click_center(center):
    print(f"  [点击] ({center.x}, {center.y})")
    do_click(center.x, center.y)


def step_click_pos(x: int, y: int):
    print(f"  [点击] 坐标 ({x}, {y})")
    do_click(x, y)


def step_double_click_center(center):
    print(f"  [双击] ({center.x}, {center.y})")
    do_double_click(center.x, center.y)


def step_detect(filename: str, timeout: float = config.DETECT_TIMEOUT):
    print(f"  [识别] {filename}")
    return detect_until(filename, timeout)


def step_multi_detect(images, timeout=config.DETECT_TIMEOUT):
    """截图+轮询多张图，返回 (center, filename) 或 (None, None)"""
    start_time = time.time()
    while True:
        screenshot = pyautogui.screenshot()
        for filename in images:
            center = locate_center_in_screenshot(filename, screenshot)
            if center is not None:
                return center, filename
        if time.time() - start_time > timeout:
            return None, None
        if DEBUG:
            print("  [调试] 本帧无匹配")
        time.sleep(config.RETRY_INTERVAL)


# ===================== 步骤辅助函数 =====================

def step_standard(state, label, filename, next_state):
    """单击saved_center → 识别filename → 成功=next_state / 超时=state"""
    global st
    print(f"\n[步骤{state}] {label}")
    time.sleep(config.STEP_WAIT)
    step_click_center(st.saved_center)
    center = step_detect(filename)
    if center is not None:
        st.saved_center = center
        return next_state
    print(f"  [超时] {filename} 重启步骤{state}")
    return state


def step_standard_pos(state, label, pos, filename, next_state):
    """单击固定坐标pos → 识别filename → 成功=next_state / 超时=state"""
    global st
    print(f"\n[步骤{state}] {label}")
    time.sleep(config.STEP_WAIT)
    step_click_pos(*pos)
    center = step_detect(filename)
    if center is not None:
        st.saved_center = center
        return next_state
    print(f"  [超时] {filename} 重启步骤{state}")
    return state


def step_standard_double(state, label, filename, next_state):
    """双击saved_center → 识别filename → 成功=next_state / 超时=state"""
    global st
    print(f"\n[步骤{state}] {label}")
    time.sleep(config.STEP_WAIT)
    step_double_click_center(st.saved_center)
    center = step_detect(filename)
    if center is not None:
        st.saved_center = center
        return next_state
    print(f"  [超时] {filename} 重启步骤{state}")
    return state


def step_standard_noclick(state, label, filename, next_state):
    """仅识别filename（不点击）→ 成功=next_state / 超时=state"""
    global st
    print(f"\n[步骤{state}] {label}")
    time.sleep(config.STEP_WAIT)
    center = step_detect(filename)
    if center is not None:
        st.saved_center = center
        return next_state
    print(f"  [超时] {filename} 重启步骤{state}")
    return state


def main():
    global st, SKIP_SETUP

    has_args = "--skip-setup" in sys.argv or "--debug" in sys.argv

    if not has_args:
        print("=" * 50)
        print("  游戏自动刷代币脚本 v3")
        print("  按 Ctrl+C 停止 / 鼠标左上角紧急停止")
        print("=" * 50)
        print("\n  请选择启动模式：")
        print("  [1] 完整流程    - 从选择英雄开始")
        print("  [2] 跳过选英雄  - 直接从战斗循环开始")
        print()
        while True:
            choice = input("  请输入 1 或 2 后按回车: ").strip()
            if choice == "1":
                SKIP_SETUP = False
                break
            elif choice == "2":
                SKIP_SETUP = True
                break
            else:
                print("  无效输入，请重新输入 1 或 2")

    state = 5 if SKIP_SETUP else 0

    print("=" * 50)
    print("  游戏自动刷代币脚本 v3")
    print("  按 Ctrl+C 停止 / 鼠标左上角紧急停止")
    if SKIP_SETUP:
        print("  模式：跳过阶段A，从步骤5开始")
    if DEBUG:
        print("  调试模式：开启")
    print("=" * 50)

    while True:
        # ==================== 步骤0：选择英雄 ====================
        if state == 0:
            print("\n[步骤0] 选择英雄")
            time.sleep(3)
            center = detect_until("select_hero.png", config.DETECT_TIMEOUT)
            if center is not None:
                st.saved_center = center
                state = 1
            else:
                print(f"  [超时] select_hero 重启步骤0")
                state = 0

        # ==================== 步骤1 ====================
        elif state == 1:
            state = step_standard(1, "选吕布", "hero_lvbu.png", 2)

        # ==================== 步骤2 ====================
        elif state == 2:
            state = step_standard(2, "确认吕布", "select_lvbu.png", 3)

        # ==================== 步骤3 ====================
        elif state == 3:
            state = step_standard_pos(3, "开始挑战", config.CURSOR_CENTER, "start_challenge.png", 4)

        # ==================== 步骤4 ====================
        elif state == 4:
            state = step_standard(4, "确认挑战", "start_QL.png", 5)

        # ==================== 步骤5：7分支检测 ====================
        elif state == 5:
            print("\n[步骤5] 千里面页-分支检测")
            if SKIP_SETUP:
                print("  等待3s...")
                time.sleep(3)
                SKIP_SETUP = False
            else:
                time.sleep(config.STEP_WAIT)
            start_time = time.time()
            while True:
                screenshot = pyautogui.screenshot()

                center = locate_center_in_screenshot("challenge_icon.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-挑战] challenge_icon")
                    state = 6; break

                center = locate_center_in_screenshot("shop_baqing.png", screenshot)
                if center is None:
                    center = locate_center_in_screenshot("shop_lvbuwei.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-商店]")
                    state = 18; break

                center = locate_center_in_screenshot("pet_feifei.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-飞飞] pet_feifei")
                    state = 21; break

                center = locate_center_in_screenshot("pet_kaka.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-卡卡] pet_kaka")
                    state = 24; break

                center = locate_center_in_screenshot("wujiang_scs.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-十常侍] wujiang_scs")
                    state = 32; break

                center = locate_center_in_screenshot("wujiang_zgl.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-诸葛亮] wujiang_zgl")
                    state = 35; break

                center = locate_center_in_screenshot("stop_challenge.png", screenshot)
                if center is not None:
                    st.saved_center = center
                    print(f"  [分支-停止] stop_challenge")
                    state = 28; break

                if time.time() - start_time > config.STEP5_TIMEOUT:
                    print(f"\n  [超时] 步骤5 超时({config.STEP5_TIMEOUT}s)，脚本退出")
                    sys.exit(1)

                if DEBUG:
                    print("  [调试] 步骤5 本帧无匹配")
                time.sleep(config.RETRY_INTERVAL)

        # ==================== 步骤6-8：战斗准备 ====================
        elif state == 6:
            state = step_standard(6, "开始战斗", "start_battle.png", 7)
        elif state == 7:
            state = step_standard(7, "设置", "setting.png", 8)
        elif state == 8:
            state = step_standard(8, "设置图标", "setting_icon.png", 9)

        # ==================== 步骤9：关闭刷新 → 房主 ====================
        elif state == 9:
            print("\n[步骤9] 关闭刷新 → 房主")
            time.sleep(config.STEP_WAIT)
            center = detect_until("close_refresh.png", config.DETECT_TIMEOUT)
            if center is not None:
                step_click_center(center)
            else:
                print(f"  [超时] close_refresh 重启步骤9")
                state = 9
                continue
            center = step_detect("host.png")
            if center is not None:
                st.saved_center = center
                state = 10
            else:
                print(f"  [超时] host 重启步骤9")
                state = 9

        # ==================== 步骤10-13 ====================
        elif state == 10:
            state = step_standard(10, "房主确认", "hosting.png", 11)
        elif state == 11:
            state = step_standard_noclick(11, "战斗结算-点击", "battle_end_click.png", 12)
        elif state == 12:
            state = step_standard(12, "战斗结算-下一步", "battle_end_next_step.png", 13)
        elif state == 13:
            state = step_standard(13, "战斗结算-确认", "battle_end_confirm.png", 14)

        # ==================== 步骤14：选择代币英雄（嵌套超时） ====================
        elif state == 14:
            print("\n[步骤14] 选择代币英雄")
            time.sleep(config.STEP_WAIT)
            step_click_center(st.saved_center)
            center = step_detect("select_token_hero.png")
            if center is not None:
                st.saved_center = center
                state = 15
            else:
                print(f"  [超时] select_token_hero，尝试 get_rewards")
                center = detect_until("get_rewards.png", config.DETECT_TIMEOUT)
                if center is not None:
                    st.saved_center = center
                    state = 30
                else:
                    print(f"  [超时] get_rewards，尝试 start_QL")
                    center = detect_until("start_QL.png", config.DETECT_TIMEOUT)
                    if center is not None:
                        st.saved_center = center
                        state = 5
                    else:
                        print(f"  [超时] start_QL 重启步骤14")
                        state = 14

        # ==================== 步骤15 ====================
        elif state == 15:
            state = step_standard_pos(15, "选择代币", config.CURSOR_CENTER, "select_token.png", 16)

        # ==================== 步骤16：选择英雄类型 ====================
        elif state == 16:
            print("\n[步骤16] 选择英雄类型")
            time.sleep(config.STEP_WAIT)
            HERO_IMAGES = [
                "hero_buff.png", "hero_funding.png", "hero_token.png",
                "hero_card.png", "hero_join.png",
            ]
            center, filename = step_multi_detect(HERO_IMAGES)
            if center is not None:
                st.hero_coord = (center.x, center.y)
                print(f"  [识别] {filename} -> 记录坐标 ({center.x}, {center.y})")
                state = 17
            else:
                print(f"  [超时] 英雄类型 重启步骤16")
                state = 16

        # ==================== 步骤17：回到主界面（嵌套超时） ====================
        elif state == 17:
            print("\n[步骤17] 回到主界面")
            time.sleep(config.STEP_WAIT)
            step_click_pos(*st.hero_coord)
            center = step_detect("start_QL.png")
            if center is not None:
                st.saved_center = center
                state = 5
            else:
                print(f"  [超时] start_QL，尝试 wujiangjineng")
                center = detect_until("wujiangjineng.png", config.DETECT_TIMEOUT)
                if center is not None:
                    st.saved_center = center
                    state = 38
                else:
                    print(f"  [超时] wujiangjineng 重启步骤17")
                    state = 17

        # ==================== 步骤18-20：商店 ====================
        elif state == 18:
            state = step_standard_double(18, "商店-双击", "shop_check.png", 19)
        elif state == 19:
            state = step_standard_pos(19, "关闭商店提示", config.POS_STEP19, "close_shop.png", 20)
        elif state == 20:
            state = step_standard(20, "关闭商店→回主界面", "start_QL.png", 5)

        # ==================== 步骤21-23：飞飞 ====================
        elif state == 21:
            state = step_standard(21, "飞飞-点击", "pet_select.png", 22)

        elif state == 22:
            print("\n[步骤22] 飞飞-选择类型")
            time.sleep(config.STEP_WAIT)
            step_click_center(st.saved_center)
            FEIFEI_IMAGES = [
                "feifei_sleep.png", "feifei_help.png", "feifei_money.png",
            ]
            center, filename = step_multi_detect(FEIFEI_IMAGES)
            if center is not None:
                st.feifei_coord = (center.x, center.y)
                print(f"  [识别] {filename} -> 记录坐标 ({center.x}, {center.y})")
                state = 23
            else:
                print(f"  [超时] 飞飞类型 重启步骤22")
                state = 22

        elif state == 23:
            state = step_standard_pos(23, "飞飞-回到主界面", st.feifei_coord, "start_QL.png", 5)

        # ==================== 步骤24-27：卡卡 ====================
        elif state == 24:
            state = step_standard(24, "卡卡-点击", "pet_select.png", 25)
        elif state == 25:
            state = step_standard(25, "卡卡-选择", "kaka_refuse.png", 26)
        elif state == 26:
            state = step_standard(26, "卡卡-拒绝", "kaka_stop.png", 27)
        elif state == 27:
            state = step_standard(27, "卡卡-回到主界面", "start_QL.png", 5)

        # ==================== 步骤28-31：结束 ====================
        elif state == 28:
            state = step_standard(28, "停止挑战", "close_shop.png", 29)
        elif state == 29:
            state = step_standard(29, "领取奖励", "get_rewards.png", 30)
        elif state == 30:
            state = step_standard(30, "关闭挑战", "close_challenge.png", 31)
        elif state == 31:
            state = step_standard(31, "回到选英雄", "select_hero.png", 0)

        # ==================== 步骤32-34：十常侍 ====================
        elif state == 32:
            state = step_standard_double(32, "十常侍-双击", "pet_select.png", 33)
        elif state == 33:
            state = step_standard(33, "十常侍-选择", "scs_check.png", 34)
        elif state == 34:
            state = step_standard_pos(34, "十常侍-回到设置", config.POS_STEP34, "setting.png", 8)

        # ==================== 步骤35-36 ====================
        elif state == 35:
            state = step_standard_double(35, "诸葛亮-双击", "wujiang_select.png", 36)
        elif state == 36:
            state = step_standard(36, "诸葛亮-选择", "zgl_check.png", 37)

        # ==================== 步骤37：诸葛亮-启动 ====================
        elif state == 37:
            print("\n[步骤37] 诸葛亮-启动")
            time.sleep(config.STEP_WAIT)
            step_click_pos(*config.POS_STEP37)
            time.sleep(config.STEP_WAIT)
            step_click_pos(*config.POS_STEP37)
            center = step_detect("wujiangjineng.png")
            if center is not None:
                st.saved_center = center
                state = 38
            else:
                print(f"  [超时] wujiangjineng 重启步骤37")
                state = 37

        # ==================== 步骤38 ====================
        elif state == 38:
            state = step_standard_pos(38, "回到主界面", config.POS_STEP38, "start_QL.png", 5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n脚本已手动停止。")
    except pyautogui.FailSafeException:
        print("\n\n紧急停止：鼠标移至屏幕左上角触发。")
