"""工作区布局：列表面板 + 详情出口。"""

from __future__ import annotations

import ui

from cstos.view.list_panel import ListPanel


@ui.component
def WorkspaceLayout() -> ui.Row:
    """左列表 / 右详情的双栏布局。

    Returns:
        工作区容器。
    """
    outlet = ui.use_route_outlet()
    return ui.Row(
        [
            ListPanel(),
            ui.Container(content=outlet, expand=True),
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ui.CrossAxisAlignment.STRETCH,
    )


__all__ = ["WorkspaceLayout"]
