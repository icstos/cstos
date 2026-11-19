"""项目资源路径的唯一出口。

src 布局下包从仓库根下沉了三层，任何「从 ``__file__`` 向上数 N 层」的
写法都会失效且不报错（直到运行期找不到文件）。统一在这里按「真实存在的
目录」向上查找，包层级再变也不用改调用方。

资产目录与配置文件都留在仓库根，不随包迁移：字体由 cs-ui 按运行平台统一
选择（主题链路里的 ``ui.apply_fonts``），应用不再自带字体文件，因此字体
配置不依赖本模块，只有按 ``__file__`` 定位的配置路径需要改。
"""

from __future__ import annotations

from pathlib import Path

_ASSETS_NAME = "assets"


def assets_dir() -> Path:
    """返回项目资源目录；不存在时由调用方决定如何降级。"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / _ASSETS_NAME
        if candidate.is_dir():
            return candidate
    # src/<project>/_paths.py 的上三级为项目根；平铺结构通常已在上循环命中
    return here.parents[2] / _ASSETS_NAME


def project_root() -> Path:
    """返回项目根目录（含 ``pyproject.toml`` 的那层）。"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    return here.parents[2]


__all__ = ["assets_dir", "project_root"]
