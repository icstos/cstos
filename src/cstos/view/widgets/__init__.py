"""可复用的纯展示控件。

这些控件不读状态、不依赖视图模型：输入即输出，便于单独渲染与测试。
"""

from __future__ import annotations

from cstos.view.widgets.avatar import avatar
from cstos.view.widgets.buttons import primary_button, text_button
from cstos.view.widgets.detail_panel import detail_panel, empty_detail_panel
from cstos.view.widgets.fields import form_field, labeled_field, search_field

__all__ = [
    "avatar",
    "detail_panel",
    "empty_detail_panel",
    "form_field",
    "labeled_field",
    "primary_button",
    "search_field",
    "text_button",
]
