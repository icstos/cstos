"""架构约束测试：验证分层、依赖方向与「不直接依赖 Flet」。

规则：
    * 单向依赖 View -> ViewModel -> Service -> Infra；
    * 所有层可依赖 Models；
    * 界面一律经 ``ui`` 组件库间接使用 Flet，**任何业务代码不得 import flet**；
    * ViewModel 不依赖任何 UI 组件库。

实现方式：静态解析各层的 import 语句，断言不存在违规依赖。
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PROJECT = "cstos"
PKG_ROOT = SRC / PROJECT

# 层 -> 允许直接导入的顶层包（一律为剥离 cstos. 前缀后的「有效根」）
ALLOWED_IMPORTS: dict[str, frozenset[str]] = {
    "models": frozenset({"models"}),
    "infra": frozenset({"models", "infra"}),
    "service": frozenset({"models", "infra", "service"}),
    "viewmodel": frozenset({"models", "service", "viewmodel"}),
    "view": frozenset({"models", "viewmodel", "view", "ui"}),
}

# 组合根与入口可以引用任意层
ROOT_MODULES: frozenset[str] = frozenset({"container", "main", "_paths", "bootstrap"})

# 界面技术栈：只有视图层可以用，且必须经 ui 组件库
UI_PACKAGE = "ui"
FORBIDDEN_UI_IMPORTS: frozenset[str] = frozenset({"flet"})

LAYERS = tuple(ALLOWED_IMPORTS)


def _python_files(package: str) -> list[Path]:
    return sorted((PKG_ROOT / package).rglob("*.py"))


def _all_project_files() -> list[Path]:
    """项目自身的全部 Python 文件（不含 vendored 的 projects/ 目录）。"""
    files = [
        path
        for path in SRC.rglob("*.py")
        if "__pycache__" not in path.parts
    ]
    files.append(ROOT / "main.py")
    return sorted(files)


def _effective_root(name: str) -> str:
    """剥离本项目的 ``cstos.`` 前缀，得到「有效根」包名。

    第三方库（如 ``ui``、``flet``）原样返回。这样分层规则用简明的一级
    包名表达，与 src 布局的物理层级解耦。
    """
    parts = name.split(".")
    if parts[0] == PROJECT and len(parts) > 1:
        return parts[1]
    return parts[0]


def _imported_roots(path: Path) -> set[str]:
    """返回文件顶层 import 的有效根包名。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(_effective_root(alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # 相对导入，忽略
                continue
            if node.module:
                roots.add(_effective_root(node.module))
    return roots


@pytest.mark.parametrize("layer", LAYERS)
def test_layer_dependency_direction(layer: str) -> None:
    """每层只能依赖自身与更低层（或 models）。"""
    allowed = ALLOWED_IMPORTS[layer]
    other_layers = {name for name in LAYERS if name != layer}
    violations: list[str] = []

    for path in _python_files(layer):
        for root in _imported_roots(path):
            if root in other_layers and root not in allowed:
                violations.append(f"{path.relative_to(ROOT)} 导入了 {root}")

    assert not violations, "违反依赖方向:\n" + "\n".join(violations)


def test_no_direct_flet_import_anywhere() -> None:
    """界面必须经 ui 组件库使用，业务代码不得直接 import flet。

    直接依赖会让「换 UI 技术栈」从一次适配退化成全项目搜索替换，
    也让组件库的默认值、令牌与主题失效。
    """
    violations = [
        str(path.relative_to(ROOT))
        for path in _all_project_files()
        if FORBIDDEN_UI_IMPORTS & _imported_roots(path)
    ]
    assert not violations, "以下文件直接导入了 flet，请改用 ui 组件库:\n" + "\n".join(
        violations
    )


def test_viewmodel_has_no_ui_dependency() -> None:
    """视图模型层必须是纯 Python，不得触碰任何 UI 组件库。"""
    violations: list[str] = []
    for path in _python_files("viewmodel"):
        forbidden = _imported_roots(path) & (FORBIDDEN_UI_IMPORTS | {UI_PACKAGE})
        if forbidden:
            violations.append(f"{path.relative_to(ROOT)} 导入了 {sorted(forbidden)}")
    assert not violations, "视图模型层不得依赖 UI:\n" + "\n".join(violations)


def test_only_view_layer_uses_ui_library() -> None:
    """ui 组件库只允许出现在视图层（以及入口的组合根）。"""
    offenders: list[str] = []
    for layer in ("models", "infra", "service", "viewmodel"):
        for path in _python_files(layer):
            if UI_PACKAGE in _imported_roots(path):
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, "仅视图层可使用 ui 组件库，违规文件:\n" + "\n".join(offenders)


def test_service_does_not_import_concrete_infra() -> None:
    """业务层只能依赖抽象接口，不得引用基础设施的具体实现模块。"""
    concrete = {
        "config_store",
        "database",
        "auth_store",
        "password_hasher",
        "user_repository",
        "workspace_repository",
        "seed",
    }
    violations: list[str] = []
    for path in _python_files("service"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[0] == PROJECT:
                    parts = parts[1:]
                if parts and parts[0] == "infra" and len(parts) > 1 and parts[1] in concrete:
                    violations.append(
                        f"{path.relative_to(ROOT)} 导入了具体实现 {node.module}"
                    )
    assert not violations, "业务层不得依赖具体技术实现:\n" + "\n".join(violations)


def test_models_is_dependency_free() -> None:
    """模型层不得依赖任何其它业务层。"""
    violations: list[str] = []
    consumers = {"infra", "service", "viewmodel", "view", "ui"}
    for path in _python_files("models"):
        for root in _imported_roots(path):
            if root in consumers:
                violations.append(f"{path.relative_to(ROOT)} 导入了 {root}")
    assert not violations, "模型层必须保持无依赖:\n" + "\n".join(violations)


def test_view_layer_only_imports_ui_for_widgets() -> None:
    """视图层只能经 ``import ui`` 使用组件库，不得引用其内部私有模块。

    统一入口保证组件 API 变更只需在一处适配；同时避免视图绕过组件库
    直接摸到 Flet 的底层实现。
    """
    violations: list[str] = []
    for path in _python_files("view"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.split(".")[0] == UI_PACKAGE
            ):
                violations.append(
                    f"{path.relative_to(ROOT)} 从 {node.module} 直接导入名字"
                )
    assert not violations, "视图层请统一使用 `import ui`:\n" + "\n".join(violations)
