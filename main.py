"""CSTOS 应用入口。

职责仅有两项：

1. 为 src 布局做 ``sys.path`` 引导（打包态必需，见下）；
2. 把控制权交给 :func:`cstos.bootstrap.run`。

界面完全由状态派生，装配与渲染细节在 ``cstos.bootstrap`` 中。
"""

from __future__ import annotations

import sys
from pathlib import Path

# src 布局必需：隔离打包环境（serious_python / PyInstaller 等）不会执行
# pip install -e .，包被编译到 <app>/src/cstos/，而运行时 sys.path 只有
# <app>/ 根、不含 src。这段同时覆盖开发态与打包态；删掉即打包后
# ModuleNotFoundError。
_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path and (_SRC / "cstos").exists():
    sys.path.insert(0, str(_SRC))

from cstos.bootstrap import configure_page, run  # noqa: E402

# 兼容历史调用方：原 ``main:main`` 控制台入口与 ``configure_page`` 旧位置。
main = run

if __name__ == "__main__":
    run()
