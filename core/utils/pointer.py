# core/utils/pointer.py
from __future__ import annotations

import time
from typing import Optional, Tuple

from core.controllers.adb import ADBController
from core.controllers.android import ScrcpyController  # type check only
try:
    from core.controllers.bluestacks import BlueStacksController
except Exception:
    BlueStacksController = None  # type: ignore
from core.controllers.base import IController
from core.controllers.steam import SteamController
from core.utils.logger import logger_uma


def smart_scroll_small(
    ctrl: IController,
    *,
    steps_pc: int = 4,
    delay_pc: float = 0.02,
    steps_android: int = 2,
    fraction_android: float = 0.10,
    settle_pre_s: float = 0.05,
    settle_mid_s: float = 0.10,
    settle_post_s: float = 0.15,
    anchor_xy: Optional[Tuple[int, int]] = None,
    end_hold_range_android: Optional[Tuple[float, float]] = None,
) -> None:
    """
    Small, device-aware scroll:
      • On Android (scrcpy): slight cursor nudge to mid/lower area, short drag with end-hold to kill inertia.
      • On PC: a few wheel ticks with short delays.

    Tunables:
      - steps_pc:    number of wheel ticks on PC
      - delay_pc:    delay between wheel ticks
      - steps_android: number of short drags on Android
      - fraction_android: drag distance as a fraction of client height (e.g., 0.10 = 10%)
    """
    time.sleep(settle_pre_s)

    xywh = ctrl._client_bbox_screen_xywh()
    if xywh:
        x, y, w, h = xywh
        auto_anchor = (x + w // 2, int(y + h * 0.66))
    else:
        auto_anchor = None

    target_anchor = anchor_xy or auto_anchor

    logger_uma.debug(
        "[pointer] smart_scroll_small ctrl=%s xywh=%s anchor_xy=%s auto_anchor=%s",
        type(ctrl).__name__,
        xywh,
        anchor_xy,
        auto_anchor,
    )

    # For mouse-based controllers we can move the cursor; ADB move_to is a no-op.
    if target_anchor is not None and not isinstance(ctrl, ADBController):
        ctrl.move_to(*target_anchor)
        time.sleep(settle_mid_s)

    if isinstance(ctrl, ScrcpyController) or (
        BlueStacksController is not None and isinstance(ctrl, BlueStacksController)
    ):
        if not xywh:
            logger_uma.debug("[pointer] no client bbox for Scrcpy/BlueStacks scroll; skipping")
            time.sleep(settle_post_s)
            return

        _, _, _, h = xywh
        drag_px = max(20, int(h * fraction_android))
        logger_uma.debug(
            "[pointer] smart_scroll_small Scrcpy drag_px=%d steps_android=%d",
            drag_px,
            max(1, steps_android),
        )
        ctrl.scroll(
            -drag_px,
            steps=max(1, steps_android),
            duration_range=(0.20, 0.40),
            end_hold_range=end_hold_range_android or (0.10, 0.20),
        )
    elif isinstance(ctrl, ADBController):
        if not xywh and target_anchor is None:
            logger_uma.debug(
                "[pointer] ADB scroll: no bbox/anchor, falling back to default center scroll"
            )
            
            ctrl.scroll(
                -max(20, int(200 * fraction_android)),
                steps=max(1, steps_android),
                duration_range=(0.20, 0.40),
                end_hold_range=end_hold_range_android or (0.10, 0.20),
            )
            time.sleep(settle_post_s)
        else:
            if target_anchor is None and xywh:
                x, y, w, h = xywh
                target_anchor = (x + w // 2, int(y + h * 0.66))

            if target_anchor is None:
                logger_uma.debug(
                    "[pointer] ADB scroll: could not compute anchor even with bbox; skipping"
                )
                time.sleep(settle_post_s)
                return

            ax, ay = int(target_anchor[0]), int(target_anchor[1])
            if xywh:
                _, _, _, h = xywh
                drag_px = max(20, int(h * fraction_android))
            else:
                drag_px = max(20, int(400 * fraction_android))

            half = drag_px // 2
            y1 = ay + half
            y2 = ay - half
            xyxy = (ax, y1, ax, y2)
            logger_uma.debug(
                "[pointer] smart_scroll_small ADB drag_px=%d steps_android=%d xyxy=%s",
                drag_px,
                max(1, steps_android),
                xyxy,
            )
            ctrl.scroll(
                xyxy,
                steps=1,
                duration_range=(0.20, 0.40),
                end_hold_range=end_hold_range_android or (0.20, 0.40),
                max_pixels_ratio=0.35
            )
    else:
        logger_uma.debug(
            "[pointer] smart_scroll_small PC-like scroll steps_pc=%d anchor=%s",
            max(1, steps_pc),
            target_anchor,
        )
        for _ in range(max(1, steps_pc)):
            ctrl.scroll(-1)
            time.sleep(max(0.0, delay_pc))

    time.sleep(settle_post_s)
