"""窗口层：无边框窗口配置、窗口状态 hook 与窗口控制按钮。

与操作系统的交互（最小化 / 最大化 / 关闭）只发生在本模块；标题栏与认证页
复用同一组 :func:`window_controls`，因此窗口按钮的外观和行为天然一致。

视图模型不参与窗口状态：最大化与否属于设备状态，按组件本地状态处理即可。
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass

import ui

from cstos.models import WindowSettings
from cstos.view.design import (
    TITLE_BAR_HEIGHT,
    WINDOW_BUTTON_WIDTH,
    WINDOW_CLOSE_ICON_SIZE,
    WINDOW_ICON_SIZE,
    Palette,
)

_CLOSE_HOVER_BG = "#E81123"
"""关闭按钮悬停底色：Windows 惯例，任何配色下都保持同一个警示红。"""

_CLOSE_HOVER_ICON = "#FFFFFF"


def apply_window_settings(
    page: ui.Page, window: WindowSettings, *, bgcolor: str
) -> None:
    """把窗口配置应用到页面。

    Flet 1.x 中 ``page.padding`` / ``page.bgcolor`` 已不是 ``Page`` 的属性，
    直接赋值不会报错但也不会生效；页面背景由根视图容器承载，
    窗口底色则由 ``window.bgcolor`` 承担（避免拖动时露白）。

    Args:
        page: 页面对象。
        window: 窗口配置。
        bgcolor: 窗口底色，通常取内容区背景色。
    """
    page.title = window.title
    page.padding = ui.Padding.all(0)
    page.window.width = window.width
    page.window.height = window.height
    page.window.min_width = window.min_width
    page.window.min_height = window.min_height
    page.window.bgcolor = bgcolor

    if window.frameless:
        page.window.frameless = True
        page.window.title_bar_hidden = True


@dataclass(frozen=True, slots=True)
class WindowActions:
    """窗口状态与操作。

    Attributes:
        maximized: 窗口当前是否最大化。
        minimize: 最小化。
        toggle_maximize: 在最大化与还原之间切换。
        close: 关闭窗口。
    """

    maximized: bool
    minimize: Callable[[], None]
    toggle_maximize: Callable[[], None]
    close: Callable[[], None]


def use_window() -> WindowActions:
    """订阅窗口状态，并返回窗口操作。

    挂载时注册窗口事件监听，卸载时注销；最大化状态随系统事件同步，
    因此外部（快捷键、双击标题栏）改变窗口大小时按钮图标也会跟着变。

    Returns:
        :class:`WindowActions`。
    """
    window = ui.context.page.window
    maximized, set_maximized = ui.use_state(bool(window.maximized))

    def listen() -> Callable[[], None]:
        def on_event(event: ui.WindowEvent) -> None:
            match event.type:
                case ui.WindowEventType.MAXIMIZE:
                    set_maximized(True)
                case ui.WindowEventType.UNMAXIMIZE:
                    set_maximized(False)

        window.on_event = on_event
        set_maximized(bool(window.maximized))

        def cleanup() -> None:
            window.on_event = None

        return cleanup

    ui.use_effect(listen, dependencies=[])

    def minimize() -> None:
        window.minimized = True
        window.update()

    def toggle_maximize() -> None:
        window.maximized = not window.maximized
        window.update()

    def close() -> None:
        asyncio.create_task(window.close())

    return WindowActions(
        maximized=maximized,
        minimize=minimize,
        toggle_maximize=toggle_maximize,
        close=close,
    )


@ui.component
def _window_button(
    *,
    icon: ui.IconData,
    icon_size: int,
    on_click: Callable[[], None],
    icon_color: str,
    hover_bg: str | None,
    hover_icon_color: str | None = None,
    height: int,
) -> ui.Container:
    """单个窗口控制按钮（悬停反馈为组件本地状态）。"""
    hovered, set_hovered = ui.use_state(False)
    return ui.Container(
        width=WINDOW_BUTTON_WIDTH,
        height=height,
        alignment=ui.Alignment.CENTER,
        bgcolor=hover_bg if hovered and hover_bg else None,
        ink=False,
        on_click=lambda _: on_click(),
        on_hover=lambda event: set_hovered(event.data == "true"),
        content=ui.Icon(
            icon,
            size=icon_size,
            color=(hover_icon_color or icon_color) if hovered else icon_color,
        ),
    )


@ui.component
def window_controls(
    *,
    palette: Palette,
    actions: WindowActions,
    on_light: bool = False,
    show_maximize: bool = True,
    height: int = TITLE_BAR_HEIGHT,
) -> ui.Row:
    """窗口控制按钮组：最小化 / 最大化 / 关闭。

    Args:
        palette: 当前色板。
        actions: 窗口状态与操作。
        on_light: 是否位于浅色背景（认证页），用于挑选悬停底色。
        show_maximize: 是否显示最大化按钮。
        height: 按钮高度，与所在标题栏一致。

    Returns:
        按钮行。
    """
    icon_color = palette.muted if on_light else palette.bar_icon
    hover_bg = (
        palette.hover if on_light else ui.Colors.with_opacity(0.10, ui.Colors.WHITE)
    )

    controls: list[ui.Control] = [
        _window_button(
            icon=ui.Icons.REMOVE,
            icon_size=WINDOW_ICON_SIZE,
            on_click=actions.minimize,
            icon_color=icon_color,
            hover_bg=hover_bg,
            height=height,
        )
    ]
    if show_maximize:
        controls.append(
            _window_button(
                icon=(
                    ui.Icons.FILTER_NONE if actions.maximized else ui.Icons.CROP_SQUARE
                ),
                icon_size=WINDOW_ICON_SIZE,
                on_click=actions.toggle_maximize,
                icon_color=icon_color,
                hover_bg=hover_bg,
                height=height,
            )
        )
    controls.append(
        _window_button(
            icon=ui.Icons.CLOSE,
            icon_size=WINDOW_CLOSE_ICON_SIZE,
            on_click=actions.close,
            icon_color=icon_color,
            hover_bg=_CLOSE_HOVER_BG,
            hover_icon_color=_CLOSE_HOVER_ICON,
            height=height,
        )
    )
    return ui.Row(controls, spacing=0)


__all__ = ["WindowActions", "apply_window_settings", "use_window", "window_controls"]
