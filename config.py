import os
import sys


def _get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


IMAGE_DIR = os.path.join(_get_base_dir(), "image")

CONFIDENCE = 0.85
GRAYSCALE = True

STEP_WAIT = 1            # 步骤内等待
DETECT_TIMEOUT = 10      # 识别超时
STEP5_TIMEOUT = 30       # 步骤5分支检测超时
RETRY_INTERVAL = 0.5     # 重试间隔

CURSOR_CENTER = (960, 540)

CLICK_MOVE_DURATION = 0.2
CLICK_PRESS_DURATION = 0.2
CLICK_STABILIZE_DELAY = 0.1

POS_STEP19 = (1840, 60)
POS_STEP34 = (350, 350)
POS_STEP37 = (1450, 500)
POS_STEP38 = (1000, 1000)
