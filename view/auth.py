"""认证视图：登录、注册、修改密码。

视图只做两件事：把状态渲染成控件、把交互转成视图模型调用。
表单校验与业务判定全部位于视图模型与业务服务。

认证页是独立全屏页（无主外壳），因此自带一条「拖动条 + 窗口按钮」，
无边框窗口下依然可以移动与关闭。
"""

from __future__ import annotations

import ui

from view.contexts import use_container
from view.design import (
    AUTH_CARD_PADDING,
    AUTH_CARD_WIDTH,
    AUTH_FIELD_WIDTH,
    FONT_BODY,
    FONT_HEADLINE,
    FONT_SMALL,
    LG,
    MD,
    RADIUS_XL,
    TITLE_BAR_HEIGHT,
    XS,
    Palette,
)
from view.hooks import use_navigate, use_palette, use_view_model
from view.widgets.buttons import primary_button, text_button
from view.widgets.fields import labeled_field
from view.window import WindowActions, use_window, window_controls


def _brand(icon: ui.IconData, palette: Palette) -> ui.Container:
    """品牌图标：柔和强调色底 + 强调色图标。"""
    return ui.Container(
        width=56,
        height=56,
        border_radius=16,
        bgcolor=palette.accent_soft,
        alignment=ui.Alignment.CENTER,
        content=ui.Icon(icon, size=28, color=palette.accent),
    )


def _feedback(message: str, color: str) -> ui.Control | None:
    """提示文本；无内容时不占位。"""
    if not message:
        return None
    return ui.Text(message, size=FONT_BODY, color=color)


def _card(
    *,
    icon: ui.IconData,
    title: str,
    subtitle: str,
    controls: list[ui.Control | None],
    footer: ui.Control,
    palette: Palette,
) -> ui.Container:
    """认证卡片：品牌 + 标题 + 表单 + 页脚。"""
    body: list[ui.Control] = [c for c in controls if c is not None]
    return ui.Container(
        width=AUTH_CARD_WIDTH,
        padding=ui.Padding.all(AUTH_CARD_PADDING),
        border_radius=RADIUS_XL,
        bgcolor=palette.surface,
        border=ui.Border.all(1, palette.border),
        content=ui.Column(
            [
                _brand(icon, palette),
                ui.Column(
                    [
                        ui.Text(
                            title,
                            size=FONT_HEADLINE,
                            weight=ui.FontWeight.W_700,
                            color=palette.text,
                        ),
                        ui.Text(subtitle, size=FONT_SMALL, color=palette.muted),
                    ],
                    spacing=XS,
                    horizontal_alignment=ui.CrossAxisAlignment.CENTER,
                ),
                ui.Column(
                    body,
                    spacing=MD,
                    horizontal_alignment=ui.CrossAxisAlignment.CENTER,
                ),
                footer,
            ],
            spacing=LG,
            tight=True,
            horizontal_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )


def _auth_page(card: ui.Control, palette: Palette, actions: WindowActions) -> ui.Column:
    """认证页骨架：顶部拖动条 + 居中的认证卡片。"""
    return ui.Column(
        [
            ui.Row(
                [
                    ui.WindowDragArea(
                        expand=True,
                        content=ui.Container(height=TITLE_BAR_HEIGHT),
                    ),
                    window_controls(
                        palette=palette,
                        actions=actions,
                        on_light=True,
                        show_maximize=False,
                        height=TITLE_BAR_HEIGHT,
                    ),
                ],
                spacing=0,
            ),
            ui.Column(
                [card],
                expand=True,
                spacing=0,
                alignment=ui.MainAxisAlignment.CENTER,
                horizontal_alignment=ui.CrossAxisAlignment.CENTER,
            ),
        ],
        expand=True,
        spacing=0,
        horizontal_alignment=ui.CrossAxisAlignment.STRETCH,
    )


@ui.component
def LoginView() -> ui.Control:
    """登录页。

    Returns:
        登录页容器。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().login)
    navigate = use_navigate()
    window = use_window()

    def submit() -> None:
        target = view_model.submit()
        if target:
            navigate(target)

    card = _card(
        icon=ui.Icons.LOCK_OUTLINE,
        title="CSTOS 登录",
        subtitle="登录企业协作工作台",
        palette=palette,
        controls=[
            labeled_field(
                palette,
                label="用户名",
                value=view_model.username,
                on_change=view_model.set_username,
                width=AUTH_FIELD_WIDTH,
                autofocus=True,
            ),
            labeled_field(
                palette,
                label="密码",
                value=view_model.password,
                on_change=view_model.set_password,
                width=AUTH_FIELD_WIDTH,
                password=True,
                on_submit=submit,
            ),
            _feedback(view_model.error, palette.danger),
            primary_button(palette, "登录", submit, width=AUTH_FIELD_WIDTH, height=42),
        ],
        footer=ui.Row(
            [
                ui.Text("还没有账号？", size=FONT_BODY, color=palette.muted),
                text_button(palette, "注册", lambda: navigate("/register"), height=28),
            ],
            spacing=0,
            alignment=ui.MainAxisAlignment.CENTER,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )
    return _auth_page(card, palette, window)


@ui.component
def RegisterView() -> ui.Control:
    """注册页。

    Returns:
        注册页容器。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().register)
    navigate = use_navigate()
    window = use_window()

    def submit() -> None:
        target = view_model.submit()
        if target:
            navigate(target)

    card = _card(
        icon=ui.Icons.PERSON_ADD_OUTLINED,
        title="注册账号",
        subtitle="创建一个新的协作账号",
        palette=palette,
        controls=[
            labeled_field(
                palette,
                label="用户名",
                value=view_model.username,
                on_change=view_model.set_username,
                width=AUTH_FIELD_WIDTH,
                autofocus=True,
            ),
            labeled_field(
                palette,
                label="密码",
                value=view_model.password,
                on_change=view_model.set_password,
                width=AUTH_FIELD_WIDTH,
                password=True,
            ),
            labeled_field(
                palette,
                label="确认密码",
                value=view_model.confirm,
                on_change=view_model.set_confirm,
                width=AUTH_FIELD_WIDTH,
                password=True,
                on_submit=submit,
            ),
            _feedback(view_model.error, palette.danger),
            primary_button(palette, "注册", submit, width=AUTH_FIELD_WIDTH, height=42),
        ],
        footer=ui.Row(
            [
                ui.Text("已有账号？", size=FONT_BODY, color=palette.muted),
                text_button(palette, "登录", lambda: navigate("/login"), height=28),
            ],
            spacing=0,
            alignment=ui.MainAxisAlignment.CENTER,
            vertical_alignment=ui.CrossAxisAlignment.CENTER,
        ),
    )
    return _auth_page(card, palette, window)


@ui.component
def ChangePasswordView() -> ui.Column:
    """修改密码表单（嵌入设置页）。

    Returns:
        表单列。
    """
    palette = use_palette()
    view_model = use_view_model(use_container().change_password)

    def submit() -> None:
        view_model.submit()

    controls: list[ui.Control] = [
        labeled_field(
            palette,
            label="旧密码",
            value=view_model.old_password,
            on_change=view_model.set_old_password,
            width=AUTH_FIELD_WIDTH,
            password=True,
        ),
        labeled_field(
            palette,
            label="新密码",
            value=view_model.new_password,
            on_change=view_model.set_new_password,
            width=AUTH_FIELD_WIDTH,
            password=True,
        ),
        labeled_field(
            palette,
            label="确认新密码",
            value=view_model.confirm,
            on_change=view_model.set_confirm,
            width=AUTH_FIELD_WIDTH,
            password=True,
            on_submit=submit,
        ),
    ]
    for message, color in (
        (view_model.error, palette.danger),
        (view_model.message, palette.success),
    ):
        feedback = _feedback(message, color)
        if feedback is not None:
            controls.append(feedback)
    controls.append(primary_button(palette, "确认修改", submit, width=AUTH_FIELD_WIDTH))

    return ui.Column(
        controls,
        spacing=MD,
        horizontal_alignment=ui.CrossAxisAlignment.START,
    )


__all__ = ["ChangePasswordView", "LoginView", "RegisterView"]
