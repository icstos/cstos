"""应用外壳：标题栏 + 侧边导航 + 路由出口 + 全局搜索。"""

from __future__ import annotations

from collections.abc import Callable

import ui

from view.contexts import use_container
from view.hooks import use_navigate, use_view_model
from view.nav_rail import NavRail
from view.search_overlay import SearchOverlay
from view.title_bar import TitleBar

_SEARCH_KEY = "F"


@ui.component
def ShellLayout() -> ui.Control:
    """主应用骨架。

    外壳承担三件事：把路由位置同步给视图模型（含登录守卫）、注册全局快捷键、
    拼装固定布局。业务状态一律留在视图模型里。

    Returns:
        外壳布局容器。
    """
    container = use_container()
    shell = use_view_model(container.shell)
    search = use_view_model(container.search_overlay)
    navigate = use_navigate()
    location = ui.use_route_location()

    def sync_route() -> None:
        """同步标签页，并在未登录时跳转登录页。"""
        target = shell.sync_location(location)
        if target:
            navigate(target)

    ui.use_effect(sync_route, dependencies=[location])

    def bind_shortcuts() -> Callable[[], None]:
        """注册全局快捷键，返回卸载清理函数。"""
        page = ui.context.page

        def on_keyboard(event: ui.KeyboardEvent) -> None:
            if event.ctrl and event.shift and event.key == _SEARCH_KEY:
                search.open()
            elif event.key == "Escape":
                search.close()

        page.on_keyboard_event = on_keyboard

        def cleanup() -> None:
            page.on_keyboard_event = None

        return cleanup

    ui.use_effect(bind_shortcuts, dependencies=[])

    def close_tab(route: str) -> None:
        """关闭标签，必要时跳到相邻标签。"""
        target = shell.close_tab(route)
        if target:
            navigate(target)

    outlet = ui.use_route_outlet()

    return ui.Column(
        [
            TitleBar(
                tabs=shell.tabs,
                active_route=location,
                on_select=navigate,
                on_close=close_tab,
            ),
            ui.Row(
                [NavRail(), ui.Container(content=outlet, expand=True)],
                expand=True,
                spacing=0,
                vertical_alignment=ui.CrossAxisAlignment.STRETCH,
            ),
            SearchOverlay(),
        ],
        expand=True,
        spacing=0,
    )


__all__ = ["ShellLayout"]
