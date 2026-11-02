"""CSTOS 应用入口。

职责仅有两项：

1. 通过组合根装配依赖（:func:`container.build_container`）；
2. 把窗口 / 主题配置下发到页面，再把根视图交给运行时。

界面完全由状态派生，因此 ``start`` 只有一次 ``page.render``。
"""

from __future__ import annotations

import ui

from container import AppContainer, build_container
from models import FONT_ASSET_PATH, FONT_FAMILY
from view.app import RootWithContainer
from view.window import apply_window_settings


def configure_page(page: ui.Page, container: AppContainer) -> None:
    """把字体、窗口与主题配置下发到页面。

    Args:
        page: 页面对象。
        container: 已装配好的应用容器。
    """
    settings = container.settings_service
    window = settings.window()
    colors = settings.colors()

    page.fonts = {FONT_FAMILY: FONT_ASSET_PATH}
    apply_window_settings(page, window, bgcolor=colors.content_bg)

    # Material 主题：主色种子取自用户配置的强调色，整套色板由它推导；
    # 明暗固定为浅色——配色配置本身是一套浅色方案。
    theme_state = ui.theme_state()
    theme_state.font_family = FONT_FAMILY
    theme_state.set_mode("light")
    theme_state.set_primary(colors.accent)


def main() -> None:
    """启动应用。"""
    container = build_container()

    def start(page: ui.Page) -> None:
        configure_page(page, container)
        # @ui.component 组件不能直接调用：page.render 会建立渲染上下文，
        # 且它接收的是组件函数本身，而非已实例化的控件。
        page.render(RootWithContainer, container)

    ui.run(start)


if __name__ == "__main__":
    main()
