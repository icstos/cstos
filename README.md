# CSTOS

Enterprise collaboration desktop application built on **cs-ui**, a local declarative UI library that wraps Flet 1.x. Ships chat, contacts, and email modules.

## Features

- **Chat Module**: Real-time messaging with bubble-style chat interface
- **Contacts**: Department and contact browsing
- **Email**: Email list and detail viewing
- **Theme Customization**: Customizable accent color, sidebar color, background, and more
- **Frameless Window**: Custom title bar with drag, minimize, maximize, and close support
- **Responsive Layout**: List panel width can be freely adjusted by dragging

## Tech Stack

- **UI library**: [cs-ui](projects/cs-ui) >= 0.1.1 (local package, built on Flet >= 1.0.5, < 2)
- **Flet usage rule**: application code only does `import ui`; no `import flet` anywhere in the project
- **Database**: SQLite + [SQLModel](https://sqlmodel.tiangolo.com/) >= 0.0.22
- **Configuration**: TOML config file + dataclass typed loading
- **Python Version**: >= 3.12

## Architecture

MVVM with strict layered dependency inversion. Dependencies flow in one
direction only — `View -> ViewModel -> Service -> Infra` — and every layer may
use `Models`. High-level layers depend on **abstractions**, never on concrete
technology.

| Layer | Responsibility | May import |
| --- | --- | --- |
| `models` | Entities, enums, constants, route value objects, reactive primitives. No business logic, no I/O. | `models` |
| `infra` | Wraps technology (TOML, SQLite, JSON, hashing) behind `Protocol` interfaces defined in `infra/protocols.py`. | `models`, `infra` |
| `service` | Orchestrates business use cases against those interfaces. | `models`, `infra.protocols`, `service` |
| `viewmodel` | Pure-Python UI state. Calls services, notifies subscribers. **Zero UI imports.** | `models`, `service`, `viewmodel` |
| `view` | Declarative `ui` components. Renders state, dispatches events. No business logic. | `models`, `viewmodel`, `view`, `ui` |

UI is a pure function of state (`UI = f(state)`). A `ViewModel` extends
`Observable`; `view/hooks.py::use_view_model` subscribes a component to a
view model, and any state change re-renders it. Theme changes therefore apply
instantly without reload hacks.

`src/cstos/container.py` is the composition root (the only place that knows which
concrete implementation satisfies each interface) and root `main.py` is the entry (sys.path bootstrap delegating to `cstos.bootstrap.run`)
point. Neither is part of the five layers.

## Project Structure

```
cstos/
├── src/
│   └── cstos/
│       ├── __init__.py
│       ├── _paths.py            # 资源路径唯一出口
│       ├── bootstrap.py         # 启动入口，暴露 run()
│       ├── container.py         # 组合根
│       ├── models/                  # 第 1 层：数据结构，无逻辑、无 IO
│       │   ├── entities.py  # Module / Item / Message / User（SQLModel）
│       │   ├── enums.py  # ModuleId、MessageRole
│       │   ├── settings.py  # AppSettings 及四个配置节
│       │   ├── route.py  # WorkspaceRoute 值对象
│       │   ├── reactive.py  # Observable（状态 + 通知）
│       │   ├── session.py  # AuthSession 值对象
│       │   └── constants.py  # 预设色、路由、字体常量
│       ├── infra/                  # 第 2 层：抽象接口背后的技术实现
│       │   ├── protocols.py  # SettingsStore / SessionStore / 仓库 / 哈希器
│       │   ├── config_store.py  # TOML 读写
│       │   ├── database.py  # 引擎、会话、结构迁移
│       │   ├── seed.py  # 演示数据 + 默认账号
│       │   ├── workspace_repository.py
│       │   ├── user_repository.py
│       │   ├── auth_store.py  # 登录态 JSON 持久化
│       │   └── password_hasher.py  # PBKDF2-HMAC-SHA256
│       ├── service/                  # 第 3 层：业务用例
│       │   ├── auth_service.py  # 登录 / 注册 / 改密 / 登出
│       │   ├── workspace_service.py  # 模块、条目、消息、搜索、置顶、隐藏、删除
│       │   └── settings_service.py  # 配置读取 / 更新 / 持久化
│       ├── viewmodel/                  # 第 4 层：纯 Python 界面状态
│       │   ├── base.py  # ViewModel 基类 + RouteTarget 约定
│       │   ├── theme.py  # ThemeState（全局响应式配色）
│       │   ├── shell.py  # 标签页 + 登录守卫
│       │   ├── nav_rail.py  # 模块列表、当前用户、激活模块
│       │   ├── list_panel.py  # 条目、搜索词、宽度、右键菜单动作
│       │   ├── chat_detail.py  # 消息与草稿
│       │   ├── generic_detail.py  # 详情正文
│       │   ├── search_overlay.py  # 开关、关键词、结果
│       │   ├── settings.py  # 可编辑配色、保存 / 恢复 / 登出
│       │   └── auth.py  # 登录 / 注册 / 改密表单
│       └── view/                  # 第 5 层：声明式 ui 组件
│           ├── design.py  # 视觉基线：几何令牌 + 语义色板 Palette
│           ├── hooks.py  # use_view_model / use_palette：状态→渲染桥接
│           ├── contexts.py  # 容器注入
│           ├── app.py  # 根视图 + 路由树
│           ├── window.py  # 窗口配置 + use_window() + 窗口按钮组
│           ├── shell.py  # 标题栏 + 导航栏 + 内容区 + 搜索
│           ├── title_bar.py  # 自有标题栏（无边框窗口）
│           ├── tab_bar.py  # 标签条
│           ├── nav_rail.py  # 侧边导航栏
│           ├── workspace.py  # 列表 + 详情双栏布局
│           ├── list_panel.py  # 列表、搜索、右键菜单、拖动调宽
│           ├── detail_chat.py  # 消息气泡 + 输入栏
│           ├── detail_generic.py  # 可滚动详情正文
│           ├── search_overlay.py  # 全局搜索弹窗
│           ├── settings.py  # 设置页
│           ├── auth.py  # 登录 / 注册 / 改密视图
│           ├── icons.py  # 图标名解析
│           └── widgets/  # 纯展示控件（头像、按钮、字段、详情面板）
├── tests/                      # 自动化测试
│   ├── test_architecture.py    # 强制校验上述分层规则
│   ├── test_viewmodel.py       # 业务行为，无需启动 UI
│   ├── test_view_smoke.py      # 离线渲染全部组件
│   └── manual/                 # 真机窗口验证脚本
├── main.py                     # 应用入口（sys.path 引导）
└── config.toml                 # 配置文件
```

The project uses a **src layout**: the five layers live under the top-level
`cstos/` package and are imported as `cstos.models`, `cstos.view`, etc.
`config.toml`, `assets/`, `data/` and `tests/` stay at the repository root;
resource paths are resolved exclusively through `cstos._paths`.


## Installation

### Option 1: pip install (Recommended)

```bash
pip install -e .
```

### Option 2: Manual dependency installation

```bash
pip install -e projects/cs-ui   # local UI library (editable)
pip install sqlmodel>=0.0.22
```

## Running

```bash
python main.py
```

## Configuration

Configuration file is located at [config.toml](config.toml), with the following sections:

### \[layout] - Layout Configuration

| Field          | Type | Default | Description                    |
| -------------- | ---- | ------- | ------------------------------ |
| `nav_width`    | int  | 48      | Side navigation bar width (px) |
| `list_min`     | int  | 200     | List panel minimum width (px)  |
| `list_max`     | int  | 480     | List panel maximum width (px)  |
| `list_default` | int  | 300     | List panel default width (px)  |
| `title_bar_h`  | int  | 40      | Title bar height (px)          |

### \[window] - Window Configuration

| Field        | Type | Default                    | Description           |
| ------------ | ---- | -------------------------- | --------------------- |
| `title`      | str  | "CSTOS"                    | Window title          |
| `subtitle`   | str  | "Enterprise Collaboration" | Window subtitle       |
| `width`      | int  | 1180                       | Default window width  |
| `height`     | int  | 720                        | Default window height |
| `min_width`  | int  | 920                        | Minimum window width  |
| `min_height` | int  | 520                        | Minimum window height |
| `frameless`  | bool | true                       | Use frameless window  |

### \[colors] - Color Theme

| Field              | Description                       |
| ------------------ | --------------------------------- |
| `sidebar`          | Sidebar background color          |
| `sidebar_hover`    | Sidebar hover color               |
| `sidebar_active`   | Sidebar active/selected color     |
| `accent`           | Theme accent color                |
| `accent_soft`      | Soft accent color                 |
| `list_bg`          | List background color             |
| `content_bg`       | Content area background color     |
| `border`           | Border color                      |
| `text`             | Primary text color                |
| `text_sec`         | Secondary text color              |
| `title_bar`        | Title bar background color        |
| `search_bg`        | Search box background color       |
| `icon_inactive`    | Inactive icon color               |
| `window_btn_icon`  | Window button icon color          |
| `title_text`       | Title bar text color              |
| `title_subtitle`   | Title bar subtitle color          |
| `input_bg`         | Input field background color      |
| `chat_self_bg`     | Self chat bubble background color |
| `chat_self_border` | Self chat bubble border color     |

### \[database] - Database Configuration

| Field | Type | Default                   | Description             |
| ----- | ---- | ------------------------- | ----------------------- |
| `url` | str  | "sqlite:///data/cstos.db" | Database connection URL |

## Data Models

### Module (Feature Module)

| Field         | Type | Description              |
| ------------- | ---- | ------------------------ |
| `id`          | str  | Unique module identifier |
| `label`       | str  | Display name             |
| `icon`        | str  | Unselected icon name     |
| `icon_filled` | str  | Selected icon name       |
| `sort_order`  | int  | Sort order               |

### Item (List Entry)

| Field          | Type | Description             |
| -------------- | ---- | ----------------------- |
| `id`           | str  | Unique item identifier  |
| `module_id`    | str  | Parent module ID        |
| `name`         | str  | Item name               |
| `subtitle`     | str  | Subtitle                |
| `preview`      | str  | Preview text            |
| `time`         | str  | Time display            |
| `color`        | str  | Avatar background color |
| `detail_title` | str  | Detail page title       |
| `detail_body`  | str  | Detail page content     |

### Message (Chat Message)

| Field        | Type | Description                  |
| ------------ | ---- | ---------------------------- |
| `id`         | int  | Auto-increment ID            |
| `item_id`    | str  | Parent item ID               |
| `role`       | str  | Message role (`me` / `them`) |
| `text`       | str  | Message content              |
| `sort_order` | int  | Sort order                   |

## Development

### Running Tests

```bash
pytest tests/                      # Architecture rules + view models + component rendering
python tests/manual/startup_check.py   # Launch the real app and report runtime errors
python tests/manual/render_check.py    # Screenshot the window and detect Flutter grey blocks
python tests/manual/theme_check.py     # Drive a real theme change and verify it applies
```

`tests/test_architecture.py` statically enforces the layering rules, so a
layering violation fails the suite instead of silently rotting.

### Adding a New Module

1. Add a `Module` record in `src/cstos/infra/seed.py`
2. Add the route in `src/cstos/view/app.py` and a view model in `src/cstos/viewmodel/`
3. Register the view model in `src/cstos/container.py`

### Customizing Theme

Click the settings button in the bottom-left corner to adjust accent, sidebar,
content background and text colour. Pressing "Save" writes `config.toml` and
pushes the new palette into `ThemeState`, which re-renders every subscribed
view immediately — no restart and no navigation required.

## License

MIT
