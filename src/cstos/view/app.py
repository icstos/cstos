"""路由树与应用根视图。

路由结构：

* ``/login``、``/register`` —— 独立全屏页（无外壳）；
* 其余路由挂在外壳下：``/`` 重定向、``/settings`` 设置页，
  以及 ``chat`` / ``contacts`` / ``email`` 三个工作区；
* 未匹配路由回落到根重定向。

根视图用 ``Router(manage_views=False)`` + ``page.render`` 的「根视图模式」：
只有这条路径下 ``page.overlay`` / ``show_dialog`` 才真正渲染，
全局搜索弹窗与各类下拉面板因此可以悬浮在内容之上。
"""

from __future__ import annotations

import ui

from cstos.view.auth import LoginView, RegisterView
from cstos.view.contexts import provide_container, use_container
from cstos.view.detail_chat import ChatDetail
from cstos.view.detail_generic import GenericDetail
from cstos.view.hooks import use_navigate, use_palette, use_view_model
from cstos.view.settings import SettingsView
from cstos.view.shell import ShellLayout
from cstos.view.workspace import WorkspaceLayout


@ui.component
def IndexRedirect() -> ui.Control:
    """根路径重定向到默认会话。

    未登录时不做跳转——登录守卫由外壳统一处理，避免两处跳转相互竞争。

    Returns:
        空容器。
    """
    shell = use_view_model(use_container().shell)
    navigate = use_navigate()

    def redirect() -> None:
        if shell.is_authenticated:
            navigate(shell.default_route())

    ui.use_effect(redirect, dependencies=[])
    return ui.Container()


@ui.component
def App() -> ui.Control:
    """应用路由树。

    Returns:
        路由器控件。
    """
    return ui.Router(
        [
            ui.Route(path="login", component=LoginView),
            ui.Route(path="register", component=RegisterView),
            ui.Route(
                component=ShellLayout,
                children=[
                    ui.Route(index=True, component=IndexRedirect),
                    ui.Route(path="settings", component=SettingsView),
                    ui.Route(
                        path="chat",
                        component=WorkspaceLayout,
                        children=[ui.Route(path=":item_id", component=ChatDetail)],
                    ),
                    ui.Route(
                        path="contacts",
                        component=WorkspaceLayout,
                        children=[ui.Route(path=":item_id", component=GenericDetail)],
                    ),
                    ui.Route(
                        path="email",
                        component=WorkspaceLayout,
                        children=[ui.Route(path=":item_id", component=GenericDetail)],
                    ),
                ],
            ),
        ],
        not_found=IndexRedirect,
        manage_views=False,
    )


@ui.component
def RootView() -> ui.Control:
    """应用根视图。

    Flet 1.x 中 ``page.bgcolor`` 不属于 ``Page``，页面级背景由本容器承载。

    Returns:
        根容器。
    """
    palette = use_palette()
    return ui.Container(expand=True, bgcolor=palette.canvas, content=App())


@ui.component
def RootWithContainer(container) -> ui.Control:
    """把应用容器与主题注入组件树。

    ``ThemeProvider`` 订阅全局主题状态，换主色时只重新下发 ``page.theme``，
    不会重建控件树（表单里已输入的内容不会丢）。

    Args:
        container: 组合根装配出的应用容器。

    Returns:
        根视图。
    """
    return provide_container(
        container,
        lambda: ui.ThemeProvider(build=RootView),
    )


__all__ = ["App", "IndexRedirect", "RootView", "RootWithContainer"]
