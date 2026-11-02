"""圆形文字头像。

纯展示控件：不读取任何状态，全部输入经由参数传入。
"""

from __future__ import annotations

import ui

from view.design import AVATAR_LIST, readable_on


def avatar(name: str, color: str, size: int = AVATAR_LIST) -> ui.Container:
    """构建圆形文字头像。

    Args:
        name: 名称，取首字作为头像文字。
        color: 头像底色。
        size: 头像边长。

    Returns:
        圆形头像容器。
    """
    initial = name[:1] if name else "?"
    return ui.Container(
        width=size,
        height=size,
        border_radius=size / 2,
        bgcolor=color,
        alignment=ui.Alignment.CENTER,
        content=ui.Text(
            initial,
            size=round(size * 0.42),
            weight=ui.FontWeight.W_600,
            color=readable_on(color),
        ),
    )


__all__ = ["avatar"]
