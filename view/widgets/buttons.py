"""按钮工厂：统一主按钮 / 文字按钮的观感。

强调色底上的前景色按对比度自动选择，用户把主色改成浅色也不会出现
「白字压浅底」读不出来的情况。样式项（底色、叠层、描边、圆角）全部
显式给出，不依赖底层的预设色板。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from view.design import (
    FONT_BODY,
    FONT_SMALL,
    LG,
    MD,
    RADIUS_MD,
    RADIUS_SM,
    Palette,
    readable_on,
)


def primary_button(
    palette: Palette,
    label: str,
    on_click: Callable[[], None],
    *,
    width: int | None = None,
    height: int = 38,
    danger: bool = False,
) -> ui.Button:
    """实心主按钮。

    Args:
        palette: 当前色板。
        label: 按钮文字。
        on_click: 点击回调。
        width: 固定宽度。
        height: 固定高度。
        danger: 是否使用危险色（退出登录、删除）。

    Returns:
        配置好的按钮。
    """
    background = palette.danger if danger else palette.accent
    foreground = readable_on(background)
    return ui.Button(
        content=ui.Text(
            label,
            size=FONT_BODY,
            weight=ui.FontWeight.W_600,
            color=foreground,
            no_wrap=True,
        ),
        width=width,
        height=height,
        style=ui.ButtonStyle(
            bgcolor=background,
            color=foreground,
            overlay_color=ui.Colors.with_opacity(0.14, foreground),
            side=ui.BorderSide(1, background),
            elevation=0,
            padding=ui.Padding.symmetric(horizontal=LG),
            shape=ui.RoundedRectangleBorder(radius=RADIUS_MD),
            alignment=ui.Alignment.CENTER,
        ),
        on_click=lambda _: on_click(),
    )


def text_button(
    palette: Palette,
    label: str,
    on_click: Callable[[], None],
    *,
    height: int = 32,
    color: str | None = None,
) -> ui.TextButton:
    """无底色的文字按钮（次要操作）。

    Args:
        palette: 当前色板。
        label: 按钮文字。
        on_click: 点击回调。
        height: 固定高度。
        color: 文字颜色，默认取次要文字色。

    Returns:
        配置好的文字按钮。
    """
    foreground = color or palette.muted
    return ui.TextButton(
        content=ui.Text(label, size=FONT_SMALL, color=foreground, no_wrap=True),
        height=height,
        style=ui.ButtonStyle(
            color=foreground,
            overlay_color=ui.overlay(0.06),
            padding=ui.Padding.symmetric(horizontal=MD),
            shape=ui.RoundedRectangleBorder(radius=RADIUS_SM),
        ),
        on_click=lambda _: on_click(),
    )


__all__ = ["primary_button", "text_button"]
