"""应用视觉基线：几何令牌 + 语义色板。

视图里不出现魔法数字。几何量全部取自本模块的常量（其值来自
``ui`` 的设计令牌，改一处全局生效）；颜色只来自两处：

* 用户可配置的 :class:`~models.ColorSettings`（设置页可改的四色 + 固定色板）；
* ``ui.core.tokens`` 的语义色（成功 / 危险），明暗主题下都满足对比度要求。

:class:`Palette` 把十几项原始配色收敛成视图真正需要的语义角色，
组件因此不必逐处挑字段，换配色时也不会漏掉某个角落。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import ui

from models import ColorSettings

# ── 间距（4pt 栅格，取自 ui 令牌）──────────────────────────────
XS = ui.SPACE["1"]  # 4
SM = ui.SPACE["2"]  # 8
MD = ui.SPACE["3"]  # 12
LG = ui.SPACE["4"]  # 16
XL = ui.SPACE["5"]  # 20
XXL = ui.SPACE["6"]  # 24

# ── 圆角 ───────────────────────────────────────────────────────
RADIUS_XS = ui.RADIUS["xs"]
RADIUS_SM = ui.RADIUS["sm"]
RADIUS_MD = ui.RADIUS["md"]
RADIUS_LG = ui.RADIUS["lg"]
RADIUS_XL = ui.RADIUS["xl"]
RADIUS_FULL = ui.RADIUS["full"]

# ── 字号（对齐 ui 字阶：body=14 是锚点，没有 subtitle 档）───────
FONT_CAPTION = ui.FONT_SIZE["caption"]  # 11
FONT_SMALL = ui.FONT_SIZE["small"]  # 12
FONT_BODY = ui.FONT_SIZE["body"]  # 14
FONT_TITLE = ui.FONT_SIZE["title"]  # 16
FONT_HEADLINE = ui.FONT_SIZE["headline"]  # 20

# ── 窗口骨架 ───────────────────────────────────────────────────
TITLE_BAR_HEIGHT = 40
TAB_HEIGHT = 40
"""标签页高度与标题栏一致：激活标签的底色直接与下方内容连成一体。"""
TAB_CLOSE_SIZE = 18
WINDOW_BUTTON_WIDTH = 46
WINDOW_ICON_SIZE = 14
WINDOW_CLOSE_ICON_SIZE = 16

# ── 侧边导航 ───────────────────────────────────────────────────
RAIL_BUTTON = 44
RAIL_BUTTON_RADIUS = 10
RAIL_ICON = 22
RAIL_AVATAR = 28
RAIL_ACTION_SIZE = 36
RAIL_ACTION_RADIUS = 9
RAIL_ACTION_ICON = 20

# ── 列表与详情 ─────────────────────────────────────────────────
AVATAR_LIST = 40
AVATAR_DETAIL = 36
AVATAR_RESULT = 32
LIST_HEADER_HEIGHT = 56
SEARCH_HEIGHT = 34
SEARCH_RADIUS = 8
UNREAD_DOT = 6
PIN_ICON = 12
DIVIDER_GRAB = 5

# ── 聊天 ───────────────────────────────────────────────────────
BUBBLE_RADIUS = 12
COMPOSER_HEIGHT = 40
SEND_SIZE = 40

# ── 页面 ───────────────────────────────────────────────────────
CONTENT_PADDING = ui.SPACE["8"]  # 32
CONTENT_MAX_WIDTH = 760
SETTINGS_MAX_WIDTH = 620
"""设置页正文上限：表单比阅读型正文更窄，留白才不会吃掉视觉重心。"""
AUTH_CARD_WIDTH = 400
AUTH_FIELD_WIDTH = 320
AUTH_CARD_PADDING = ui.SPACE["10"]  # 40
SEARCH_DIALOG_WIDTH = 560
SEARCH_DIALOG_HEIGHT = 400

_HEX_PATTERN = re.compile(r"^#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def _channels(color: str) -> tuple[int, int, int] | None:
    """把十六进制色串解析为 ``(R, G, B)``；非十六进制（角色名等）返回 ``None``。"""
    text = color.strip()
    if not _HEX_PATTERN.match(text):
        return None
    digits = text.removeprefix("#")
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    if len(digits) == 8:
        digits = digits[2:]  # 忽略 alpha 通道
    return int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16)


def is_light(color: str, *, threshold: float = 0.62) -> bool:
    """判断底色是否为浅色（用于挑选文字 / 图标 / 悬停覆盖层的档位）。

    Args:
        color: 底色。
        threshold: 感知亮度阈值，默认与 :func:`readable_on` 一致。

    Returns:
        浅色返回 ``True``；无法解析时按浅色处理（与默认浅色主题一致）。
    """
    channels = _channels(color)
    if channels is None:
        return True
    return _luminance(channels) > threshold


def _luminance(channels: tuple[int, int, int]) -> float:
    """感知亮度（0..1）。"""
    red, green, blue = channels
    # 人眼对绿最敏感、对蓝最迟钝
    return (0.299 * red + 0.587 * green + 0.114 * blue) / 255


def readable_on(color: str, *, light: str = "#FFFFFF", dark: str = "#14171F") -> str:
    """在给定底色上挑一个可读的前景色（白或近黑）。

    Args:
        color: 底色，``#RGB`` / ``#RRGGBB`` / ``#AARRGGBB``。
        light: 深底上使用的前景色。
        dark: 浅底上使用的前景色。

    Returns:
        对比度更高的那个前景色；无法解析时退化为 ``light``。
    """
    channels = _channels(color)
    if channels is None:
        return light
    return dark if _luminance(channels) > 0.62 else light


@dataclass(frozen=True, slots=True)
class Palette:
    """当前配色派生出的语义色板。

    视图只读这里的角色名，不直接读 :class:`~models.ColorSettings` 的字段，
    这样「某个语义该用哪个色」只需在一处决定。
    """

    accent: str
    """强调色：选中态、主按钮、发送键、链接。"""

    accent_soft: str
    """强调色淡底：选中行、品牌图标底。"""

    on_accent: str
    """强调色实底上的文字色（按对比度自动选白 / 近黑）。"""

    canvas: str
    """内容区背景。"""

    surface: str
    """面板背景（列表、标题栏、输入栏、卡片）。"""

    border: str
    """1px 分隔线 / 面板描边。"""

    field: str
    """输入框与搜索框的填充底色。"""

    text: str
    """主文字。"""

    muted: str
    """次要文字 / 占位图标。"""

    rail: str
    """侧栏底色。"""

    rail_hover: str
    """侧栏按钮悬停底色。"""

    rail_active: str
    """侧栏按钮选中底色。"""

    rail_icon: str
    """侧栏未选中图标色。"""

    bar: str
    """标题栏底色。"""

    bar_text: str
    """标题栏主文字。"""

    bar_muted: str
    """标题栏次要文字 / 未激活标签。"""

    bar_icon: str
    """标题栏窗口控制图标。"""

    bubble: str
    """对方消息气泡底色。"""

    bubble_border: str
    """对方消息气泡描边。"""

    danger: str
    """危险语义色（删除、错误提示、退出登录）。"""

    success: str
    """成功语义色（改密成功等）。"""

    hover: str
    """浅色面板上的悬停覆盖层（主题感知，随明暗自动解析）。"""

    bar_hover: str
    """深色标题栏上的悬停覆盖层。"""

    @classmethod
    def of(cls, colors: ColorSettings) -> Palette:
        """由用户配置派生色板。

        标题栏与侧栏可能是浅色也可能是深色（两者都由配置决定），
        因此栏上的文字 / 图标 / 悬停覆盖层按底色亮度自动换档，
        换配色时不会出现「浅底压浅字」。
        """
        bar_is_light = is_light(colors.title_bar)
        return cls(
            accent=colors.accent,
            accent_soft=colors.accent_soft,
            on_accent=readable_on(colors.accent),
            canvas=colors.content_bg,
            surface=colors.list_bg,
            border=colors.border,
            field=colors.input_bg,
            text=colors.text,
            muted=colors.text_sec,
            rail=colors.sidebar,
            rail_hover=colors.sidebar_hover,
            rail_active=colors.sidebar_active,
            rail_icon=colors.icon_inactive,
            bar=colors.title_bar,
            bar_text=colors.text if bar_is_light else colors.title_text,
            bar_muted=colors.text_sec if bar_is_light else colors.title_subtitle,
            bar_icon=colors.text_sec if bar_is_light else colors.window_btn_icon,
            bubble=colors.chat_self_bg,
            bubble_border=colors.chat_self_border,
            danger=ui.semantic_text("danger"),
            success=ui.semantic_text("success"),
            hover=ui.overlay(0.05),
            bar_hover=(
                ui.overlay(0.07)
                if bar_is_light
                else ui.Colors.with_opacity(0.08, ui.Colors.WHITE)
            ),
        )


__all__ = [
    "AUTH_CARD_PADDING",
    "AUTH_CARD_WIDTH",
    "AUTH_FIELD_WIDTH",
    "AVATAR_DETAIL",
    "AVATAR_LIST",
    "AVATAR_RESULT",
    "BUBBLE_RADIUS",
    "COMPOSER_HEIGHT",
    "CONTENT_MAX_WIDTH",
    "CONTENT_PADDING",
    "DIVIDER_GRAB",
    "FONT_BODY",
    "FONT_CAPTION",
    "FONT_HEADLINE",
    "FONT_SMALL",
    "FONT_TITLE",
    "LG",
    "LIST_HEADER_HEIGHT",
    "MD",
    "PIN_ICON",
    "RADIUS_FULL",
    "RADIUS_LG",
    "RADIUS_MD",
    "RADIUS_SM",
    "RADIUS_XL",
    "RADIUS_XS",
    "RAIL_ACTION_ICON",
    "RAIL_ACTION_RADIUS",
    "RAIL_ACTION_SIZE",
    "RAIL_AVATAR",
    "RAIL_BUTTON",
    "RAIL_BUTTON_RADIUS",
    "RAIL_ICON",
    "SEARCH_DIALOG_HEIGHT",
    "SEARCH_DIALOG_WIDTH",
    "SEARCH_HEIGHT",
    "SEARCH_RADIUS",
    "SEND_SIZE",
    "SETTINGS_MAX_WIDTH",
    "SM",
    "TAB_CLOSE_SIZE",
    "TAB_HEIGHT",
    "TITLE_BAR_HEIGHT",
    "UNREAD_DOT",
    "WINDOW_BUTTON_WIDTH",
    "WINDOW_CLOSE_ICON_SIZE",
    "WINDOW_ICON_SIZE",
    "XL",
    "XS",
    "XXL",
    "Palette",
    "is_light",
    "readable_on",
]
