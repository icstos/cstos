"""设置页：外观（主题色）+ 账号安全（改密）+ 账号操作（退出登录）。

页面按「分组卡片」组织：每组一句话说明做什么，控件本身保持单列，
避免桌面端设置页常见的长表单疲劳。
"""

from __future__ import annotations

from collections.abc import Callable

import ui

from cstos.view.auth import ChangePasswordView
from cstos.view.contexts import use_container
from cstos.view.design import (
    AUTH_FIELD_WIDTH,
    CONTENT_PADDING,
    FONT_BODY,
    FONT_CAPTION,
    FONT_HEADLINE,
    FONT_SMALL,
    FONT_TITLE,
    LG,
    MD,
    RADIUS_FULL,
    RADIUS_SM,
    RADIUS_XL,
    SETTINGS_MAX_WIDTH,
    SM,
    XL,
    XS,
    Palette,
)
from cstos.view.hooks import use_navigate, use_palette, use_view_model
from cstos.view.widgets.buttons import primary_button, text_button
from cstos.view.widgets.fields import form_field

_SWATCH = 30


def _section(
    *,
    title: str,
    hint: str,
    controls: list[ui.Control],
    palette: Palette,
) -> ui.Container:
    """分组卡片：标题 + 说明 + 内容。"""
    return ui.Container(
        bgcolor=palette.surface,
        border=ui.Border.all(1, palette.border),
        border_radius=RADIUS_XL,
        padding=ui.Padding.all(XL),
        content=ui.Column(
            [
                ui.Column(
                    [
                        ui.Text(
                            title,
                            size=FONT_TITLE,
                            weight=ui.FontWeight.W_600,
                            color=palette.text,
                        ),
                        ui.Text(hint, size=FONT_SMALL, color=palette.muted),
                    ],
                    spacing=XS,
                ),
                *controls,
            ],
            spacing=LG,
            horizontal_alignment=ui.CrossAxisAlignment.STRETCH,
        ),
    )


def _swatch(value: str, palette: Palette) -> ui.Container:
    """颜色预览小方块。"""
    return ui.Container(
        width=_SWATCH,
        height=_SWATCH,
        border_radius=RADIUS_SM,
        bgcolor=value,
        border=ui.Border.all(1, palette.border),
    )


def _color_row(
    *,
    label: str,
    value: str,
    on_change: Callable[[str], None],
    palette: Palette,
) -> ui.Row:
    """一行「标签 + 输入框 + 预览」。"""
    return ui.Row(
        [
            ui.Text(label, size=FONT_BODY, color=palette.text, width=76),
            form_field(
                palette,
                value=value,
                on_change=on_change,
                width=190,
                height=36,
                borderless=True,
            ),
            _swatch(value, palette),
        ],
        spacing=MD,
        vertical_alignment=ui.CrossAxisAlignment.CENTER,
    )


def _preset(
    value: str,
    *,
    selected: bool,
    palette: Palette,
    on_click: Callable[[str], None],
) -> ui.Container:
    """常用颜色预设圆点；当前主色加一圈描边以示选中。"""
    return ui.Container(
        width=_SWATCH,
        height=_SWATCH,
        border_radius=RADIUS_FULL,
        bgcolor=value,
        border=ui.Border.all(2, palette.text if selected else palette.border),
        tooltip=value,
        ink=True,
        on_click=lambda _: on_click(value),
    )


@ui.component
def SettingsView() -> ui.Control:
    """设置页。

    Returns:
        设置页容器。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().settings)
    navigate = use_navigate()

    def go_back() -> None:
        navigate(view_model.back_route)

    def logout() -> None:
        target = view_model.logout()
        if target:
            navigate(target)

    def save() -> None:
        """保存配色，并让 Material 主题的色板同步重算。"""
        view_model.apply_and_save()
        ui.theme_state().set_primary(view_model.accent)

    def restore() -> None:
        """恢复为磁盘上的配置，并同步主题色板。"""
        view_model.restore_defaults()
        ui.theme_state().set_primary(view_model.accent)

    appearance = _section(
        title="外观",
        hint="主色会推导出整套界面色板，明暗与描边随之协调。",
        palette=palette,
        controls=[
            ui.Column(
                [
                    _color_row(
                        label="主颜色",
                        value=view_model.accent,
                        on_change=view_model.set_accent,
                        palette=palette,
                    ),
                    _color_row(
                        label="侧栏色",
                        value=view_model.sidebar,
                        on_change=view_model.set_sidebar,
                        palette=palette,
                    ),
                    _color_row(
                        label="内容背景",
                        value=view_model.content_bg,
                        on_change=view_model.set_content_bg,
                        palette=palette,
                    ),
                    _color_row(
                        label="文字色",
                        value=view_model.text_color,
                        on_change=view_model.set_text_color,
                        palette=palette,
                    ),
                ],
                spacing=SM,
            ),
            ui.Row(
                [
                    ui.Text("常用颜色", size=FONT_CAPTION, color=palette.muted),
                    *(
                        _preset(
                            value,
                            selected=value.lower() == view_model.accent.lower(),
                            palette=palette,
                            on_click=view_model.set_accent,
                        )
                        for value in view_model.presets
                    ),
                ],
                spacing=SM,
                vertical_alignment=ui.CrossAxisAlignment.CENTER,
            ),
            ui.Row(
                [
                    primary_button(palette, "保存", save),
                    text_button(palette, "恢复为默认", restore),
                ],
                spacing=MD,
            ),
        ],
    )

    security = _section(
        title="账号安全",
        hint="修改后请用新密码重新登录。",
        palette=palette,
        controls=[ChangePasswordView()],
    )

    account = _section(
        title="账号",
        hint="退出后需要重新登录才能继续使用。",
        palette=palette,
        controls=[
            # 卡片内容列是拉伸对齐的，按钮要套一层 Row 才不会被拉满整行
            ui.Row(
                [
                    primary_button(
                        palette,
                        "退出登录",
                        logout,
                        danger=True,
                        width=AUTH_FIELD_WIDTH,
                    )
                ]
            )
        ],
    )

    return ui.Container(
        expand=True,
        bgcolor=palette.canvas,
        padding=ui.Padding.all(CONTENT_PADDING),
        content=ui.Column(
            [
                ui.Column(
                    [
                        ui.Row(
                            [
                                ui.IconButton(
                                    icon=ui.Icons.ARROW_BACK,
                                    icon_size=18,
                                    icon_color=palette.muted,
                                    tooltip="返回",
                                    width=32,
                                    height=32,
                                    style=ui.ButtonStyle(
                                        overlay_color=ui.overlay(0.06),
                                        shape=ui.RoundedRectangleBorder(
                                            radius=RADIUS_SM
                                        ),
                                    ),
                                    on_click=lambda _: go_back(),
                                ),
                                ui.Column(
                                    [
                                        ui.Text(
                                            "设置",
                                            size=FONT_HEADLINE,
                                            weight=ui.FontWeight.W_700,
                                            color=palette.text,
                                        ),
                                        ui.Text(
                                            "应用偏好与账号管理",
                                            size=FONT_SMALL,
                                            color=palette.muted,
                                        ),
                                    ],
                                    spacing=XS,
                                ),
                            ],
                            spacing=XS,
                            vertical_alignment=ui.CrossAxisAlignment.CENTER,
                        ),
                        appearance,
                        security,
                        account,
                    ],
                    width=SETTINGS_MAX_WIDTH,
                    spacing=LG,
                    horizontal_alignment=ui.CrossAxisAlignment.STRETCH,
                ),
            ],
            spacing=0,
            scroll=ui.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


__all__ = ["SettingsView"]
