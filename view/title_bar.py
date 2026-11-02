"""自定义标题栏（无边框窗口）。

包含应用图标、标签页栏与窗口控制按钮。窗口的最小化 / 最大化 / 关闭
属于操作系统交互，统一由 :mod:`view.window` 处理；本模块只负责排布。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from view.design import Palette
from view.hooks import use_theme
from view.tab_bar import TabBar
from view.window import use_window, window_controls
from viewmodel import TabData


@ui.component
def TitleBar(
    *,
    tabs: tuple[TabData, ...],
    active_route: str,
    on_select: Callable[[str], None],
    on_close: Callable[[str], None],
) -> ui.Container:
    """标题栏：图标 + 标签页 + 窗口按钮。

    整条空白区域都是拖动区，双击可在最大化与还原之间切换——
    与 Windows 原生标题栏的手感一致。

    Args:
        tabs: 标签集合。
        active_route: 当前激活路由。
        on_select: 标签选中回调。
        on_close: 标签关闭回调。

    Returns:
        标题栏容器。
    """
    theme = use_theme()
    palette = Palette.of(theme.colors)
    window = use_window()
    height = theme.layout.title_bar_h

    return ui.Container(
        height=height,
        bgcolor=palette.bar,
        content=ui.Row(
            [
                ui.WindowDragArea(
                    expand=True,
                    maximizable=True,
                    content=ui.GestureDetector(
                        on_double_tap=lambda _: window.toggle_maximize(),
                        content=ui.Row(
                            [
                                ui.Container(
                                    padding=ui.Padding.only(left=12, right=6),
                                    content=ui.Icon(
                                        ui.Icons.APPS,
                                        size=16,
                                        color=palette.accent,
                                    ),
                                ),
                                TabBar(
                                    tabs=tabs,
                                    active_route=active_route,
                                    on_select=on_select,
                                    on_close=on_close,
                                ),
                            ],
                            spacing=0,
                            vertical_alignment=ui.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ),
                window_controls(palette=palette, actions=window, height=height),
            ],
            spacing=0,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


__all__ = ["TitleBar"]
