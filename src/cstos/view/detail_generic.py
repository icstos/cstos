"""通用详情页（通讯录 / 邮箱）：可滚动正文。"""

from __future__ import annotations

import ui

from cstos.view.contexts import use_container
from cstos.view.design import FONT_BODY, XXL
from cstos.view.hooks import use_palette, use_view_model
from cstos.view.widgets.detail_panel import detail_panel, empty_detail_panel


@ui.component
def GenericDetail() -> ui.Control:
    """展示条目的详情正文，缺失时降级为预览文本。

    Returns:
        通用详情面板。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().generic_detail)

    params = ui.use_route_params()
    item_id = params.get("item_id", "")
    ui.use_effect(lambda: view_model.load(item_id), dependencies=[item_id])

    item = view_model.item
    if item is None:
        return empty_detail_panel(palette)

    body = ui.Container(
        expand=True,
        padding=ui.Padding.all(XXL),
        content=ui.Column(
            [
                ui.Text(
                    view_model.body,
                    size=FONT_BODY,
                    color=palette.text,
                    selectable=True,
                )
            ],
            scroll=ui.ScrollMode.AUTO,
        ),
    )
    return detail_panel(item, item.subtitle, body, palette)


__all__ = ["GenericDetail"]
