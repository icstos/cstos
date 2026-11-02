"""标签页栏（嵌入标题栏使用）。

标签采用「整条与标题栏同高、仅上圆角」的桌面形态：激活标签的底色与
下方内容区连成一体，视觉上能直接读出「当前在哪一页」。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from view.design import (
    FONT_BODY,
    RADIUS_MD,
    SM,
    TAB_CLOSE_SIZE,
    TAB_HEIGHT,
    Palette,
)
from view.hooks import use_palette
from viewmodel import TabData

_MAX_TITLE = 18
"""标签标题的最大字符数，超出部分省略——标签不会因为名字长而撑爆标题栏。"""


def _shorten(title: str) -> str:
    """截断过长的标题。"""
    return title if len(title) <= _MAX_TITLE else f"{title[: _MAX_TITLE - 1]}…"


@ui.component
def _tab(
    tab: TabData,
    *,
    active: bool,
    on_select: Callable[[str], None],
    on_close: Callable[[str], None],
) -> ui.Container:
    """单个标签：点击切换，右侧关闭。"""
    palette: Palette = use_palette()
    hovered, set_hovered = ui.use_state(False)

    if active:
        bgcolor = palette.canvas
    else:
        bgcolor = palette.bar_hover if hovered else None

    return ui.Container(
        height=TAB_HEIGHT,
        bgcolor=bgcolor,
        border_radius=ui.BorderRadius.only(top_left=RADIUS_MD, top_right=RADIUS_MD),
        border=(
            ui.Border.only(top=ui.BorderSide(2, palette.accent)) if active else None
        ),
        padding=ui.Padding.only(left=12, right=6),
        ink=True,
        on_click=lambda _: on_select(tab.route),
        on_hover=lambda event: set_hovered(event.data == "true"),
        content=ui.Row(
            [
                ui.Text(
                    _shorten(tab.title),
                    size=FONT_BODY,
                    weight=ui.FontWeight.W_600 if active else ui.FontWeight.W_400,
                    color=palette.accent if active else palette.bar_muted,
                    max_lines=1,
                ),
                ui.Container(
                    width=TAB_CLOSE_SIZE,
                    height=TAB_CLOSE_SIZE,
                    border_radius=ui.RADIUS["sm"],
                    alignment=ui.Alignment.CENTER,
                    ink=True,
                    tooltip="关闭",
                    on_click=lambda _, route=tab.route: on_close(route),
                    content=ui.Icon(
                        ui.Icons.CLOSE,
                        size=13,
                        color=palette.muted,
                    ),
                ),
            ],
            spacing=SM,
            tight=True,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


@ui.component
def TabBar(
    *,
    tabs: tuple[TabData, ...],
    active_route: str,
    on_select: Callable[[str], None],
    on_close: Callable[[str], None],
) -> ui.Control:
    """水平排列全部标签，末尾留出拖动区。

    Args:
        tabs: 标签集合。
        active_route: 当前激活路由。
        on_select: 选中回调。
        on_close: 关闭回调。

    Returns:
        标签栏控件。
    """
    if not tabs:
        return ui.Container(expand=True)

    return ui.Row(
        [
            *(
                _tab(
                    tab,
                    active=tab.route == active_route,
                    on_select=on_select,
                    on_close=on_close,
                )
                for tab in tabs
            ),
            ui.Container(expand=True),
        ],
        spacing=2,
        vertical_alignment=ui.CrossAxisAlignment.CENTER,
        scroll=ui.ScrollMode.AUTO,
    )


__all__ = ["TabBar"]
