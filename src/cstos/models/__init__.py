"""模型层。

定义核心数据结构、状态枚举与常量，并提供响应式状态原语。
本层**不含任何业务逻辑**，也**不做任何 IO**，因此可被其它所有层依赖。
"""

from __future__ import annotations

from cstos.models.constants import (
    COLOR_PRESETS,
    FONT_ASSET_PATH,
    FONT_FAMILY,
    LOGIN_ROUTE,
    REGISTER_ROUTE,
    ROOT_ROUTE,
    SETTINGS_ROUTE,
)
from cstos.models.entities import (
    DEFAULT_AVATAR_COLOR,
    Item,
    Message,
    Module,
    User,
)
from cstos.models.enums import MessageRole, ModuleId
from cstos.models.reactive import Listener, Observable
from cstos.models.route import DEFAULT_MODULE_ID, WorkspaceRoute
from cstos.models.settings import (
    AppSettings,
    ColorSettings,
    DatabaseSettings,
    LayoutSettings,
    WindowSettings,
)

__all__ = [
    "COLOR_PRESETS",
    "DEFAULT_AVATAR_COLOR",
    "DEFAULT_MODULE_ID",
    "FONT_ASSET_PATH",
    "FONT_FAMILY",
    "LOGIN_ROUTE",
    "REGISTER_ROUTE",
    "ROOT_ROUTE",
    "SETTINGS_ROUTE",
    "AppSettings",
    "ColorSettings",
    "DatabaseSettings",
    "Item",
    "LayoutSettings",
    "Listener",
    "Message",
    "MessageRole",
    "Module",
    "ModuleId",
    "Observable",
    "User",
    "WindowSettings",
    "WorkspaceRoute",
]
