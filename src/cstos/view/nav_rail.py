"""侧边导航栏。

导航栏是一条「窄图标轨」：模块入口居中排列，底部固定用户头像与设置入口。
栏宽、按钮与图标成组缩放（见 :mod:`view.design`），因此收窄栏宽时不会
出现「窄栏配大按钮」的失衡。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from cstos.models import SETTINGS_ROUTE
from cstos.view.contexts import use_container
from cstos.view.design import (
    RAIL_ACTION_ICON,
    RAIL_ACTION_RADIUS,
    RAIL_ACTION_SIZE,
    RAIL_AVATAR,
    RAIL_BUTTON,
    RAIL_BUTTON_RADIUS,
    RAIL_ICON,
    SM,
    XS,
    Palette,
)
from cstos.view.hooks import use_navigate, use_theme, use_view_model
from cstos.view.icons import resolve_icon
from cstos.view.widgets.avatar import avatar


@ui.component
def _rail_button(
    *,
    icon: ui.IconData,
    tooltip: str,
    on_click: Callable[[], None],
    palette: Palette,
    active: bool = False,
    size: int = RAIL_BUTTON,
    radius: int = RAIL_BUTTON_RADIUS,
    icon_size: int = RAIL_ICON,
) -> ui.Container:
    """导航栏按钮：悬停变亮、选中用实心强调色图标。"""
    hovered, set_hovered = ui.use_state(False)

    if active:
        bgcolor = palette.rail_active
    elif hovered:
        bgcolor = palette.rail_hover
    else:
        bgcolor = None

    return ui.Container(
        width=size,
        height=size,
        border_radius=radius,
        bgcolor=bgcolor,
        alignment=ui.Alignment.CENTER,
        ink=True,
        tooltip=tooltip,
        on_click=lambda _: on_click(),
        on_hover=lambda event: set_hovered(event.data == "true"),
        content=ui.Icon(
            icon,
            size=icon_size,
            color=palette.accent if active else palette.rail_icon,
        ),
    )


@ui.component
def NavRail() -> ui.Container:
    """左侧垂直导航栏：模块入口 + 用户头像 + 设置入口。

    Returns:
        导航栏容器。
    """
    theme = use_theme()
    palette = Palette.of(theme.colors)
    view_model = use_view_model(use_container().nav_rail)
    navigate = use_navigate()
    location = ui.use_route_location()

    # 登录 / 登出后刷新用户名与头像色
    ui.use_effect(lambda: view_model.refresh(), dependencies=[location])

    session = view_model.session
    avatar_color = session.avatar_color if session else palette.accent

    def module_buttons() -> list[ui.Control]:
        """按模块生成入口按钮；选中态用实心图标 + 强调色。"""
        buttons: list[ui.Control] = []
        for module in view_model.modules:
            active = view_model.is_module_active(module.id, location)
            buttons.append(
                _rail_button(
                    icon=resolve_icon(module.icon_filled if active else module.icon),
                    tooltip=module.label,
                    active=active,
                    palette=palette,
                    on_click=lambda module_id=module.id: navigate(f"/{module_id}"),
                )
            )
        return buttons

    return ui.Container(
        width=theme.layout.nav_width,
        bgcolor=palette.rail,
        padding=ui.Padding.symmetric(vertical=10),
        content=ui.Column(
            [
                ui.Column(
                    module_buttons(),
                    spacing=XS,
                    horizontal_alignment=ui.CrossAxisAlignment.CENTER,
                ),
                ui.Container(expand=True),
                ui.Column(
                    [
                        ui.Container(
                            tooltip=view_model.display_name,
                            content=avatar(
                                view_model.display_name, avatar_color, RAIL_AVATAR
                            ),
                        ),
                        _rail_button(
                            icon=ui.Icons.SETTINGS_OUTLINED,
                            tooltip="设置",
                            palette=palette,
                            on_click=lambda: navigate(SETTINGS_ROUTE),
                            size=RAIL_ACTION_SIZE,
                            radius=RAIL_ACTION_RADIUS,
                            icon_size=RAIL_ACTION_ICON,
                        ),
                    ],
                    spacing=SM,
                    horizontal_alignment=ui.CrossAxisAlignment.CENTER,
                ),
            ],
            expand=True,
            spacing=0,
            # 外层 Column 必须显式居中，否则子列会按各自内容宽度左对齐、贴左缘
            horizontal_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


__all__ = ["NavRail"]
