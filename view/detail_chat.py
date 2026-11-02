"""聊天详情页：消息气泡列表 + 输入工具栏。"""

from __future__ import annotations

import ui

from models import Message, MessageRole
from view.contexts import use_container
from view.design import (
    BUBBLE_RADIUS,
    COMPOSER_HEIGHT,
    FONT_SUBTITLE,
    LG,
    MD,
    RADIUS_MD,
    SEND_SIZE,
    SM,
    XL,
    XXL,
    Palette,
)
from view.hooks import use_palette, use_view_model
from view.widgets.detail_panel import detail_panel, empty_detail_panel
from view.widgets.fields import form_field


def _bubble(message: Message, palette: Palette) -> ui.Control:
    """单条消息气泡：己方右对齐、对方左对齐，靠边一侧的圆角收小。"""
    mine = message.role == MessageRole.ME
    bubble = ui.Container(
        bgcolor=palette.accent if mine else palette.bubble,
        border=(
            None if mine else ui.Border.all(1, palette.bubble_border or palette.border)
        ),
        border_radius=ui.BorderRadius.only(
            top_left=BUBBLE_RADIUS,
            top_right=BUBBLE_RADIUS,
            bottom_left=4 if mine else BUBBLE_RADIUS,
            bottom_right=BUBBLE_RADIUS if mine else 4,
        ),
        padding=ui.Padding.symmetric(horizontal=14, vertical=10),
        content=ui.Text(
            message.text,
            size=FONT_SUBTITLE,
            color=palette.on_accent if mine else palette.text,
            selectable=True,
        ),
    )

    # 前置 / 后置一个弹性空白，把气泡顶到对应一侧
    spacer = ui.Container(expand=True)
    controls = [spacer, bubble] if mine else [bubble, spacer]
    return ui.Row(controls, spacing=0)


@ui.component
def ChatDetail() -> ui.Control:
    """聊天会话详情。

    Returns:
        聊天详情面板。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().chat_detail)

    params = ui.use_route_params()
    item_id = params.get("item_id", "")
    ui.use_effect(lambda: view_model.load(item_id), dependencies=[item_id])

    item = view_model.item
    if item is None:
        return empty_detail_panel(palette)

    body = ui.Column(
        [
            ui.Container(
                expand=True,
                padding=ui.Padding.symmetric(horizontal=XXL, vertical=XL),
                content=ui.Column(
                    [_bubble(message, palette) for message in view_model.messages],
                    spacing=MD,
                    scroll=ui.ScrollMode.AUTO,
                    auto_scroll=True,
                    expand=True,
                ),
            ),
            ui.Container(
                bgcolor=palette.surface,
                border=ui.Border.only(top=ui.BorderSide(1, palette.border)),
                padding=ui.Padding.symmetric(horizontal=LG, vertical=10),
                content=ui.Row(
                    [
                        ui.IconButton(
                            icon=ui.Icons.ATTACH_FILE,
                            icon_size=20,
                            icon_color=palette.muted,
                            tooltip="附件",
                        ),
                        ui.IconButton(
                            icon=ui.Icons.EMOJI_EMOTIONS_OUTLINED,
                            icon_size=20,
                            icon_color=palette.muted,
                            tooltip="表情",
                        ),
                        form_field(
                            palette,
                            value=view_model.draft,
                            on_change=view_model.set_draft,
                            hint="输入消息…",
                            height=COMPOSER_HEIGHT,
                            expand=True,
                            borderless=True,
                            on_submit=view_model.send,
                        ),
                        ui.Container(
                            width=SEND_SIZE,
                            height=SEND_SIZE,
                            border_radius=RADIUS_MD,
                            bgcolor=palette.accent,
                            alignment=ui.Alignment.CENTER,
                            ink=True,
                            tooltip="发送",
                            on_click=lambda _: view_model.send(),
                            content=ui.Icon(
                                ui.Icons.SEND, size=18, color=palette.on_accent
                            ),
                        ),
                    ],
                    spacing=SM,
                    vertical_alignment=ui.CrossAxisAlignment.CENTER,
                ),
            ),
        ],
        expand=True,
        spacing=0,
    )
    return detail_panel(item, item.subtitle, body, palette)


__all__ = ["ChatDetail"]
