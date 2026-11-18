"""统一的输入框工厂。

把 Flet 1.x 输入控件的边框 / 填充 / 光标 / 内边距配置收敛到一处，
视图里只描述「这是搜索、表单还是消息输入」。

回调一律收「值」而不是控件事件：视图不需要知道 ``event.control.value``
这类细节，交互意图更直白。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import ui

from cstos.view.design import (
    FONT_BODY,
    FONT_SMALL,
    RADIUS_MD,
    SEARCH_HEIGHT,
    SEARCH_RADIUS,
    SM,
    XS,
    Palette,
)


def form_field(
    palette: Palette,
    *,
    value: str = "",
    on_change: Callable[[str], None] | None = None,
    label: str | None = None,
    hint: str | None = None,
    width: int | None = None,
    height: int | None = None,
    expand: bool = False,
    password: bool = False,
    prefix_icon: ui.IconData | None = None,
    autofocus: bool = False,
    on_submit: Callable[[], None] | None = None,
    borderless: bool = False,
) -> ui.TextField:
    """构建表单输入框。

    Args:
        palette: 当前色板。
        value: 初始值。
        on_change: 值变更回调（收新值）。
        label: 浮动标签；``None`` 表示不显示。
        hint: 占位提示。
        width: 固定宽度。
        height: 固定高度。
        expand: 是否在父容器中占满剩余空间。
        password: 是否为密码输入（自带显隐切换）。
        prefix_icon: 前置图标。
        autofocus: 挂载后是否自动聚焦。
        on_submit: 回车提交回调。
        borderless: 无描边（搜索 / 消息这类「填充式」输入）。

    Returns:
        配置好的输入框。
    """
    return ui.TextField(
        value=value,
        label=label,
        hint_text=hint,
        width=width,
        height=height,
        expand=expand or None,
        password=password,
        can_reveal_password=password,
        prefix_icon=prefix_icon,
        autofocus=autofocus,
        filled=borderless,
        fill_color=palette.field if borderless else None,
        cursor_color=palette.accent,
        border=(
            ui.NoInputBorder()
            if borderless
            else ui.outline_input(
                radius=RADIUS_MD, color=palette.border, focused_color=palette.accent
            )
        ),
        content_padding=(
            ui.Padding.symmetric(horizontal=SM, vertical=0) if borderless else None
        ),
        text_size=FONT_BODY if borderless else None,
        on_change=(
            (lambda event: on_change(event.control.value or ""))
            if on_change is not None
            else None
        ),
        on_submit=(lambda _: on_submit()) if on_submit is not None else None,
    )


def labeled_field(palette: Palette, *, label: str, **field: Any) -> ui.Column:
    """纵向字段：小号标签在上、输入框在下。

    Material 的浮动标签在未聚焦时会缩进框内，和已聚焦的邻居排在一起会
    一高一低；表单统一改成外置标签，几行字段才真正对齐。

    Args:
        palette: 当前色板。
        label: 字段名。
        **field: 透传给 :func:`form_field` 的参数。

    Returns:
        标签与输入框组成的列。
    """
    return ui.Column(
        [
            ui.Text(label, size=FONT_SMALL, color=palette.muted),
            form_field(palette, hint=field.pop("hint", f"请输入{label}"), **field),
        ],
        spacing=XS,
        horizontal_alignment=ui.CrossAxisAlignment.START,
    )


@ui.component
def search_field(
    palette: Palette,
    *,
    value: str = "",
    on_change: Callable[[str], None] | None = None,
    hint: str = "搜索",
    height: int = SEARCH_HEIGHT,
    autofocus: bool = False,
    expand: bool = False,
) -> ui.Container:
    """构建搜索框：填充式底 + 前置放大镜 + 聚焦描边。

    不用 ``TextField.prefix_icon``：它会按 Material 规范预留约 44px 的图标槽，
    在窄面板里会把输入文字推得过远。这里自己排图标与输入框，间距可控。

    Args:
        palette: 当前色板。
        value: 当前关键词。
        on_change: 关键词变更回调。
        hint: 占位提示。
        height: 高度。
        autofocus: 挂载后是否自动聚焦。
        expand: 是否在父容器（如 Row）中占满剩余宽度。

    Returns:
        组合好的搜索框容器。
    """
    focused, set_focused = ui.use_state(False)

    return ui.Container(
        height=height,
        expand=expand or None,
        bgcolor=palette.field,
        border_radius=SEARCH_RADIUS,
        border=ui.Border.all(1, palette.accent if focused else ui.Colors.TRANSPARENT),
        padding=ui.Padding.only(left=SM + 2, right=SM),
        clip_behavior=ui.ClipBehavior.ANTI_ALIAS,
        content=ui.Row(
            [
                ui.Icon(
                    ui.Icons.SEARCH,
                    size=16,
                    color=palette.accent if focused else palette.muted,
                ),
                ui.TextField(
                    value=value,
                    hint_text=hint,
                    expand=True,
                    dense=True,
                    border=ui.NoInputBorder(),
                    content_padding=ui.Padding.all(0),
                    text_size=FONT_BODY,
                    cursor_color=palette.accent,
                    autofocus=autofocus,
                    on_focus=lambda _: set_focused(True),
                    on_blur=lambda _: set_focused(False),
                    on_change=(
                        (lambda event: on_change(event.control.value or ""))
                        if on_change is not None
                        else None
                    ),
                ),
            ],
            spacing=SM,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


__all__ = ["form_field", "labeled_field", "search_field"]
