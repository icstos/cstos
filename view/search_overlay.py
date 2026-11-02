"""全局搜索弹窗（Ctrl+Shift+F 唤起）。

弹窗的显隐由 :class:`~viewmodel.search_overlay.SearchOverlayViewModel` 持有，
快捷键在 :mod:`view.shell` 注册；这里只负责渲染与事件分发。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from models import Item
from view.contexts import use_container
from view.design import (
    AVATAR_RESULT,
    FONT_BODY,
    FONT_CAPTION,
    FONT_SMALL,
    MD,
    RADIUS_LG,
    RADIUS_SM,
    SEARCH_DIALOG_HEIGHT,
    SEARCH_DIALOG_WIDTH,
    SM,
    XS,
    Palette,
)
from view.hooks import use_navigate, use_palette, use_view_model
from view.widgets.avatar import avatar
from view.widgets.fields import search_field


@ui.component
def _result_row(
    *,
    item: Item,
    module_label: str,
    palette: Palette,
    on_open: Callable[[Item], None],
) -> ui.Container:
    """单条搜索结果：悬停高亮、回车 / 单击跳转。"""
    hovered, set_hovered = ui.use_state(False)
    return ui.Container(
        ink=True,
        border_radius=RADIUS_LG,
        bgcolor=palette.hover if hovered else None,
        padding=ui.Padding.symmetric(horizontal=SM + XS, vertical=SM),
        on_click=lambda _: on_open(item),
        on_hover=lambda event: set_hovered(event.data == "true"),
        content=ui.Row(
            [
                avatar(item.name, item.color, AVATAR_RESULT),
                ui.Column(
                    [
                        ui.Row(
                            [
                                ui.Text(
                                    item.name,
                                    size=FONT_BODY,
                                    weight=ui.FontWeight.W_500,
                                    color=palette.text,
                                    max_lines=1,
                                    overflow=ui.TextOverflow.ELLIPSIS,
                                    expand=True,
                                ),
                                ui.Text(
                                    module_label,
                                    size=FONT_CAPTION,
                                    color=palette.muted,
                                ),
                            ],
                            vertical_alignment=ui.CrossAxisAlignment.CENTER,
                        ),
                        ui.Text(
                            item.preview,
                            size=FONT_SMALL,
                            color=palette.muted,
                            max_lines=1,
                            overflow=ui.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


@ui.component
def SearchOverlay() -> ui.Container:
    """跨模块搜索弹窗。

    Returns:
        占位容器（弹窗通过 ``use_dialog`` 挂载到页面浮层）。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().search_overlay)
    navigate = use_navigate()

    def open_item(item: Item) -> None:
        """跳转到选中条目并关闭弹窗。"""
        navigate(f"/{item.module_id}/{item.id}")
        view_model.close()

    labels = view_model.module_labels
    results = view_model.results

    if results:
        body: ui.Control = ui.ListView(
            [
                _result_row(
                    item=item,
                    module_label=labels.get(item.module_id, ""),
                    palette=palette,
                    on_open=open_item,
                )
                for item in results
            ],
            spacing=2,
            expand=True,
        )
    else:
        body = ui.Container(
            alignment=ui.Alignment.CENTER,
            content=ui.Text(
                "无搜索结果" if view_model.query.strip() else "开始输入以搜索",
                size=FONT_BODY,
                color=palette.muted,
            ),
        )

    content = ui.Container(
        width=SEARCH_DIALOG_WIDTH,
        height=SEARCH_DIALOG_HEIGHT,
        content=ui.Column(
            [
                ui.Container(
                    padding=ui.Padding.only(
                        left=SM + XS, right=SM + XS, top=MD, bottom=SM
                    ),
                    border=ui.Border.only(bottom=ui.BorderSide(1, palette.border)),
                    content=ui.Row(
                        [
                            search_field(
                                palette,
                                value=view_model.query,
                                on_change=view_model.set_query,
                                hint="搜索条目…",
                                autofocus=True,
                                expand=True,
                            ),
                            ui.Container(
                                padding=ui.Padding.symmetric(horizontal=6, vertical=2),
                                border_radius=RADIUS_SM,
                                border=ui.Border.all(1, palette.border),
                                content=ui.Text(
                                    "Esc", size=FONT_CAPTION, color=palette.muted
                                ),
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ui.CrossAxisAlignment.CENTER,
                    ),
                ),
                ui.Container(
                    expand=True,
                    padding=ui.Padding.only(
                        left=SM + XS, right=SM, top=XS + 2, bottom=SM
                    ),
                    content=body,
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )

    ui.use_dialog(
        ui.AlertDialog(
            modal=True,
            bgcolor=palette.surface,
            barrier_color=ui.scrim(),
            content=content,
            on_dismiss=lambda _: view_model.close(),
        )
        if view_model.is_open
        else None
    )
    return ui.Container()


__all__ = ["SearchOverlay"]
