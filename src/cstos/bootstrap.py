"""应用启动逻辑。

集中 ``configure_page`` 与 :func:`run`，让根目录的 ``main.py`` 退化成
「sys.path 引导 + 调用 run」的纯入口。这样开发态 ``python main.py``、
可编辑安装的 ``cstos`` 命令、以及隔离打包三条路径共用同一份实现。
"""

from __future__ import annotations

import ui

from cstos.container import AppContainer, build_container
from cstos.view.app import RootWithContainer
from cstos.view.window import apply_window_settings


def configure_page(page: ui.Page, container: AppContainer) -> None:
    """把窗口与主题配置下发到页面。

    字体不在此处配置：由 cs-ui 的主题链路统一管理。``ThemeProvider`` 下发
    主题时会调用 ``ui.apply_fonts``，按运行平台选择系统字体与中文回退字体。

    Args:
        page: 页面对象。
        container: 已装配好的应用容器。
    """
    settings = container.settings_service
    window = settings.window()
    colors = settings.colors()

    apply_window_settings(page, window, bgcolor=colors.content_bg)

    # Material 主题：主色种子取自用户配置的强调色，整套色板由它推导；
    # 明暗固定为浅色——配色配置本身是一套浅色方案。
    theme_state = ui.theme_state()
    theme_state.set_mode("light")
    theme_state.set_primary(colors.accent)


def run() -> None:
    """启动应用。"""
    container = build_container()

    def start(page: ui.Page) -> None:
        configure_page(page, container)
        # @ui.component 组件不能直接调用：page.render 会建立渲染上下文，
        # 且它接收的是组件函数本身，而非已实例化的控件。
        page.render(RootWithContainer, container)

    ui.run(start)
