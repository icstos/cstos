"""详情面板骨架。

头部（头像 + 标题 / 副标题 + 操作）+ 内容主体。纯展示组件：
配色由调用方传入，不自行读取状态。
"""

from __future__ import annotations

import ui

from models import Item
from view.design import (
    AVATAR_DETAIL,
    FONT_SMALL,
    FONT_TITLE,
    LIST_HEADER_HEIGHT,
    MD,
    SM,
    Palette,
)
from view.widgets.avatar import avatar

HEADER_HEIGHT = LIST_HEADER_HEIGHT
"""头部栏高度。"""


def detail_panel(
    item: Item,
    subtitle: str,
    body: ui.Control,
    palette: Palette,
) -> ui.Container:
    """构建详情面板。

    Args:
        item: 条目数据。
        subtitle: 副标题文本。
        body: 内容主体控件。
        palette: 当前色板。

    Returns:
        详情面板容器。
    """
    header = ui.Container(
        height=HEADER_HEIGHT,
        bgcolor=palette.surface,
        border=ui.Border.only(bottom=ui.BorderSide(1, palette.border)),
        padding=ui.Padding.symmetric(horizontal=ui.SPACE["5"], vertical=0),
        content=ui.Row(
            [
                avatar(item.name, item.color, AVATAR_DETAIL),
                ui.Column(
                    [
                        ui.Text(
                            item.name,
                            size=FONT_TITLE,
                            weight=ui.FontWeight.W_600,
                            color=palette.text,
                            max_lines=1,
                            overflow=ui.TextOverflow.ELLIPSIS,
                        ),
                        ui.Text(
                            subtitle,
                            size=FONT_SMALL,
                            color=palette.muted,
                            max_lines=1,
                            overflow=ui.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=1,
                    alignment=ui.MainAxisAlignment.CENTER,
                    expand=True,
                ),
                ui.IconButton(
                    icon=ui.Icons.VIDEOCAM_OUTLINED,
                    icon_size=20,
                    icon_color=palette.muted,
                    tooltip="视频通话",
                ),
                ui.IconButton(
                    icon=ui.Icons.MORE_VERT,
                    icon_size=20,
                    icon_color=palette.muted,
                    tooltip="更多",
                ),
            ],
            spacing=SM,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )

    return ui.Container(
        expand=True,
        bgcolor=palette.canvas,
        content=ui.Column([header, body], expand=True, spacing=0),
    )


def empty_detail_panel(palette: Palette) -> ui.Container:
    """条目不存在时的占位面板。

    Args:
        palette: 当前色板。

    Returns:
        居中的空状态容器。
    """
    return ui.Container(
        expand=True,
        bgcolor=palette.canvas,
        alignment=ui.Alignment.CENTER,
        content=ui.Column(
            [
                ui.Icon(
                    ui.Icons.FORUM_OUTLINED,
                    size=44,
                    color=ui.Colors.with_opacity(0.35, palette.muted),
                ),
                ui.Text("从左侧选择一个条目", size=FONT_SMALL, color=palette.muted),
            ],
            spacing=MD,
            horizontal_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


__all__ = ["HEADER_HEIGHT", "detail_panel", "empty_detail_panel"]
