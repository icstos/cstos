"""列表面板：条目列表 + 搜索 + 右键菜单 + 宽度调整。"""

from __future__ import annotations

from collections.abc import Callable

import ui

from cstos.models import Item
from cstos.view.contexts import use_container
from cstos.view.design import (
    AVATAR_LIST,
    DIVIDER_GRAB,
    FONT_BODY,
    FONT_CAPTION,
    FONT_HEADLINE,
    FONT_SMALL,
    LG,
    MD,
    PIN_ICON,
    SM,
    UNREAD_DOT,
    XS,
    Palette,
)
from cstos.view.hooks import use_navigate, use_palette, use_view_model
from cstos.view.widgets.avatar import avatar
from cstos.view.widgets.fields import search_field

_MENU_ITEM_HEIGHT = 40
_MENU_ICON = 18


def _menu_item(
    *,
    label: str,
    icon: ui.IconData,
    on_click: Callable[[], None],
    palette: Palette,
    danger: bool = False,
) -> ui.PopupMenuItem:
    """菜单项：统一图标尺寸与行高，危险动作用危险色。"""
    color = palette.danger if danger else palette.muted
    return ui.PopupMenuItem(
        content=ui.Text(
            label,
            size=FONT_BODY,
            color=palette.danger if danger else palette.text,
        ),
        icon=ui.Icon(icon, size=_MENU_ICON, color=color),
        height=_MENU_ITEM_HEIGHT,
        on_click=lambda _: on_click(),
    )


def _row_menu(
    item: Item,
    on_action: Callable[[str, str], None],
    palette: Palette,
) -> list[ui.PopupMenuItem]:
    """构建条目的右键菜单。

    Args:
        item: 目标条目。
        on_action: 动作回调，接收 ``(动作名, 条目 ID)``。
        palette: 当前色板。

    Returns:
        菜单项列表。
    """
    return [
        _menu_item(
            label="标记为未读",
            icon=ui.Icons.MARK_AS_UNREAD,
            palette=palette,
            on_click=lambda: on_action("mark_unread", item.id),
        ),
        _menu_item(
            label="取消置顶" if item.is_pinned else "置顶",
            icon=ui.Icons.PUSH_PIN if item.is_pinned else ui.Icons.PUSH_PIN_OUTLINED,
            palette=palette,
            on_click=lambda: on_action("toggle_pin", item.id),
        ),
        ui.PopupMenuItem(
            height=9,
            padding=ui.Padding.symmetric(horizontal=0, vertical=4),
            content=ui.Divider(height=1, thickness=1, color=palette.border),
        ),
        _menu_item(
            label="隐藏",
            icon=ui.Icons.HIDE_SOURCE_OUTLINED,
            palette=palette,
            on_click=lambda: on_action("hide", item.id),
        ),
        _menu_item(
            label="删除",
            icon=ui.Icons.DELETE_OUTLINED,
            palette=palette,
            danger=True,
            on_click=lambda: on_action("delete", item.id),
        ),
    ]


@ui.component
def _list_row(
    *,
    item: Item,
    selected: bool,
    palette: Palette,
    on_open: Callable[[], None],
    on_action: Callable[[str, str], None],
) -> ui.ContextMenu:
    """单个列表条目：悬停高亮、选中竖条、未读圆点、置顶图钉、右键菜单。"""
    hovered, set_hovered = ui.use_state(False)

    if selected:
        bgcolor = palette.accent_soft
    elif hovered:
        bgcolor = palette.hover
    else:
        bgcolor = None

    meta: list[ui.Control] = []
    if item.is_pinned:
        meta.append(ui.Icon(ui.Icons.PUSH_PIN, size=PIN_ICON, color=palette.muted))
    if item.time:
        meta.append(
            ui.Text(item.time, size=FONT_CAPTION, color=palette.muted, max_lines=1)
        )

    preview_meta: list[ui.Control] = [
        ui.Text(
            item.preview,
            size=FONT_SMALL,
            color=palette.accent if selected else palette.muted,
            max_lines=1,
            overflow=ui.TextOverflow.ELLIPSIS,
            expand=True,
        )
    ]
    if item.is_unread:
        preview_meta.append(
            ui.Container(
                width=UNREAD_DOT,
                height=UNREAD_DOT,
                border_radius=UNREAD_DOT / 2,
                bgcolor=palette.accent,
            )
        )

    row = ui.Container(
        bgcolor=bgcolor,
        border=ui.Border.only(
            left=ui.BorderSide(3, palette.accent if selected else ui.Colors.TRANSPARENT)
        ),
        padding=ui.Padding.only(left=10, right=14, top=10, bottom=10),
        ink=True,
        on_click=lambda _: on_open(),
        on_hover=lambda event: set_hovered(event.data == "true"),
        content=ui.Row(
            [
                avatar(item.name, item.color, AVATAR_LIST),
                ui.Column(
                    [
                        ui.Row(
                            [
                                ui.Text(
                                    item.name,
                                    size=FONT_BODY,
                                    weight=(
                                        ui.FontWeight.W_600
                                        if selected or item.is_unread
                                        else ui.FontWeight.W_500
                                    ),
                                    color=palette.text,
                                    max_lines=1,
                                    overflow=ui.TextOverflow.ELLIPSIS,
                                    expand=True,
                                ),
                                *meta,
                            ],
                            spacing=SM,
                            vertical_alignment=ui.CrossAxisAlignment.CENTER,
                        ),
                        ui.Row(
                            preview_meta,
                            spacing=SM,
                            vertical_alignment=ui.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=XS,
                    expand=True,
                ),
            ],
            spacing=MD,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )

    return ui.ContextMenu(
        secondary_items=_row_menu(item, on_action, palette),
        secondary_trigger=ui.ContextMenuTrigger.DOWN,
        content=row,
    )


@ui.component
def _resize_handle(
    *,
    palette: Palette,
    on_drag: Callable[[ui.DragUpdateEvent], None],
) -> ui.GestureDetector:
    """列表与详情之间的拖拽分隔条。

    只有 5px 宽的可点区域、本身透明，靠面板自身的 1px 描边作视觉分隔；
    悬停时给出淡底，提示「这里可以拖」。
    """
    hovered, set_hovered = ui.use_state(False)
    return ui.GestureDetector(
        mouse_cursor=ui.MouseCursor.RESIZE_LEFT_RIGHT,
        drag_interval=8,
        on_horizontal_drag_update=on_drag,
        content=ui.Container(
            width=DIVIDER_GRAB,
            bgcolor=palette.hover if hovered else ui.Colors.TRANSPARENT,
            on_hover=lambda event: set_hovered(event.data == "true"),
        ),
    )


@ui.component
def ListPanel() -> ui.Row:
    """当前模块的条目列表。

    Returns:
        列表面板容器（列表 + 可拖拽的宽度分隔条）。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().list_panel)
    navigate = use_navigate()
    location = ui.use_route_location()

    def sync_route() -> None:
        """路由变化时重载列表，必要时跳到首个条目。"""
        target = view_model.sync_route(location)
        if target:
            navigate(target)

    ui.use_effect(sync_route, dependencies=[location])

    def activate(action: str, item_id: str) -> None:
        """执行右键菜单动作，必要时跟随跳转。"""
        target = view_model.activate(action, item_id)
        if target:
            navigate(target)

    def resize(event: ui.DragUpdateEvent) -> None:
        """拖动分隔条调整列表宽度。"""
        if event.local_delta:
            view_model.resize_by(event.local_delta.x)

    items = view_model.items

    if items:
        body: ui.Control = ui.ListView(
            [
                _list_row(
                    item=item,
                    selected=view_model.is_selected(item.id),
                    palette=palette,
                    on_open=lambda item_id=item.id: navigate(
                        view_model.item_route(item_id)
                    ),
                    on_action=activate,
                )
                for item in items
            ],
            spacing=0,
            padding=0,
            expand=True,
        )
    else:
        body = ui.Container(
            expand=True,
            alignment=ui.Alignment.CENTER,
            content=ui.Text(
                "没有匹配的条目" if view_model.query.strip() else "暂无内容",
                size=FONT_SMALL,
                color=palette.muted,
            ),
        )

    return ui.Row(
        [
            ui.Container(
                width=view_model.width,
                bgcolor=palette.surface,
                border=ui.Border.only(right=ui.BorderSide(1, palette.border)),
                content=ui.Column(
                    [
                        ui.Container(
                            padding=ui.Padding.only(
                                left=LG, right=LG, top=LG - 2, bottom=10
                            ),
                            content=ui.Column(
                                [
                                    ui.Text(
                                        view_model.module_label,
                                        size=FONT_HEADLINE,
                                        weight=ui.FontWeight.W_700,
                                        color=palette.text,
                                    ),
                                    search_field(
                                        palette,
                                        value=view_model.query,
                                        on_change=view_model.set_query,
                                        hint="搜索",
                                    ),
                                ],
                                spacing=10,
                            ),
                        ),
                        ui.Container(expand=True, content=body),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
            _resize_handle(palette=palette, on_drag=resize),
        ],
        spacing=0,
        vertical_alignment=ui.CrossAxisAlignment.STRETCH,
    )


__all__ = ["ListPanel"]
