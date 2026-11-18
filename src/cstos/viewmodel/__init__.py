"""视图模型层。

连接视图与业务：持有界面状态、调用业务服务，并在状态变化时通知订阅者。
本层是**纯 Python 类**，不依赖 Flet 或任何 UI 组件，也不直接操作界面。
"""

from __future__ import annotations

from cstos.viewmodel.auth import (
    ChangePasswordViewModel,
    LoginViewModel,
    RegisterViewModel,
)
from cstos.viewmodel.base import RouteTarget, ViewModel
from cstos.viewmodel.chat_detail import ChatDetailViewModel
from cstos.viewmodel.generic_detail import GenericDetailViewModel
from cstos.viewmodel.list_panel import ListPanelViewModel
from cstos.viewmodel.nav_rail import NavRailViewModel
from cstos.viewmodel.search_overlay import SearchOverlayViewModel
from cstos.viewmodel.settings import SettingsViewModel
from cstos.viewmodel.shell import ShellViewModel, TabData
from cstos.viewmodel.theme import ThemeState

__all__ = [
    "ChangePasswordViewModel",
    "ChatDetailViewModel",
    "GenericDetailViewModel",
    "ListPanelViewModel",
    "LoginViewModel",
    "NavRailViewModel",
    "RegisterViewModel",
    "RouteTarget",
    "SearchOverlayViewModel",
    "SettingsViewModel",
    "ShellViewModel",
    "TabData",
    "ThemeState",
    "ViewModel",
]
