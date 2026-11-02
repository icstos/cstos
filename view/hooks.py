"""视图层与视图模型之间的桥接 hooks。

这是全应用**唯一**把「外部状态对象」接入渲染管线的地方：订阅视图模型 ->
状态变更时自增一个本地计数 -> 触发当前组件重新渲染。
组件因此永远只是「当前状态的纯函数」。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from models.reactive import Observable
from view.contexts import use_container
from view.design import Palette
from viewmodel.theme import ThemeState


def use_view_model[T: Observable](view_model: T) -> T:
    """订阅视图模型并返回它。

    视图模型状态变化时，当前组件会重新渲染。

    Args:
        view_model: 要订阅的视图模型（或任何 :class:`~models.reactive.Observable`）。

    Returns:
        传入的视图模型本身，便于链式书写。
    """
    _, bump = ui.use_state(0)

    def setup() -> Callable[[], None]:
        def on_change() -> None:
            bump(lambda count: count + 1)

        return view_model.subscribe(on_change)

    ui.use_effect(setup, dependencies=[view_model])
    return view_model


def use_theme() -> ThemeState:
    """订阅全局主题状态（配色 + 布局尺寸）。

    Returns:
        :class:`~viewmodel.theme.ThemeState`。
    """
    return use_view_model(use_container().theme)


def use_palette() -> Palette:
    """订阅全局配色并派生语义色板。

    配色变更（设置页保存）后，调用方组件自动重新渲染。

    Returns:
        当前配色对应的 :class:`~view.design.Palette`。
    """
    return Palette.of(use_theme().colors)


def use_navigate() -> Callable[[str], None]:
    """返回一个导航函数。

    视图层只拿这一个入口跳转，避免每个组件各写一遍 ``page.navigate``。

    Returns:
        接收路由路径的函数。
    """
    page = ui.context.page

    def navigate(route: str) -> None:
        page.navigate(route)

    return navigate


__all__ = ["use_navigate", "use_palette", "use_theme", "use_view_model"]
