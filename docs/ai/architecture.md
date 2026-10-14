# 当前架构说明

> 本文描述仓库当前已实现的代码结构，不是目标架构设计。静态审查基准：`master` / `8cfdeec`；检查日期：2026-10-14。

## 项目与技术栈

这是一个标题为“用户管理系统 API”的 FastAPI 应用（`main.py`）。`requirements.txt` 声明 FastAPI、Pydantic v2、SQLAlchemy 2 异步接口、aiomysql、Alembic、Uvicorn 和 Scalar。当前本地虚拟环境元数据为 CPython 3.13.14；仓库没有 `pyproject.toml`、锁文件或 Python 版本声明文件，因此它不是仓库层面的强制版本约束。

依赖管理仅使用 `requirements.txt`。依赖清单与源码直接导入的一致性存在已知问题，详见 [审计报告](audit-report.md)。

## 目录与职责

| 路径 | 当前职责 |
| --- | --- |
| `main.py` | 创建 `FastAPI` 实例、注册 Scalar、路由、中间件和异常处理器。 |
| `routers/` | API 路由：`authority.py` 为认证，`user.py` 为用户，`product.py` 为商品示例。路由函数直接协调 ORM。 |
| `schemas/` | Pydantic 请求、响应和统一响应包装模型。 |
| `models/` | SQLAlchemy 异步引擎、会话工厂、声明式基类及用户、文章、标签模型。 |
| `dependencies.py` | `get_session`：每请求创建并最终关闭 `AsyncSession`。 |
| `core/` | JWT、错误码、应用异常和成功响应工厂。 |
| `middleware/` | 路由命中与响应状态日志中间件。 |
| `utils/` | 分页查询参数依赖。 |
| `alembic/` | 异步 Alembic 环境和迁移版本。 |
| `test_main.http` | IDE HTTP 客户端请求样例；不是自动化测试套件。 |

当前没有独立 service/repository 层：用户、认证相关路由直接发起 SQLAlchemy 查询和事务。这是当前实现事实，不代表该分层模式本身必然错误。

## 应用创建、入口与生命周期

- ASGI 对象：`main:app`（`main.py:22`）。
- 应用注册了 Scalar 文档路由 `/scalar`（`main.py:47`）；FastAPI 默认 OpenAPI/Swagger 路径未在代码中覆盖。2026-10-14 的受控本地验证中，`/docs`、`/openapi.json` 和 `/scalar` 均返回 HTTP 200。
- 注册顺序：路由日志中间件、三类异常处理器、`userRouter`、`productRouter`、`AuthorityRouter` 和根路由（`main.py:49-95`）。
- 未发现 `lifespan`、`startup` 或 `shutdown` 处理器；数据库引擎未在应用关闭路径显式 `dispose()`。
- 导入 `main` 会执行文件底部的 Pydantic 示例和 `print`（`main.py:97-121`）。应用导入曾实际通过，但会产生控制台输出。

## API、校验与响应

路由前缀分别为 `/authority`、`/user` 和 `/product`。已实现的路径包括：`/authority/getToken`、`/authority/token`、`/user/list`、`/user/login`、`/user/add`、`/user/delete`、`/user/info`、`/product/list` 和 `/`。

`schemas/user.py` 的 `AddUserRequest` 使用 `EmailStr`、密码长度 6–30、手机号最大长度 20；分页依赖将 `page` 限为最小 1、`size` 限为 1–100（`utils/paginationQuery.py`）。`schemas/response.py` 定义泛型 `ApiResponse` 和校验失败模型；但并非全部路由声明或返回该统一模型，当前响应契约并不完全一致。

## 数据访问与迁移

`models/__init__.py` 由 `config.DB_URI` 创建 SQLAlchemy `AsyncEngine` 与 `async_sessionmaker`。`get_session` 在 `finally` 中关闭会话（`dependencies.py`）。写操作在部分路由中通过 `async with session.begin()` 提交；读操作直接使用会话执行查询。

模型关系：`User` 与 `UserProfile` 一对一；`User` 与 `Article` 一对多；`Article` 与 `Tag` 经 `ArticleTag` 多对多。Alembic 的 `env.py` 从项目配置读取 URL，使用 `Base.metadata`，并以异步引擎执行在线迁移。迁移链为初始建表、添加 `mobile`、添加 `disabled`、将 `password` 改为 `hashed_password`。当前数据库版本、数据状态和迁移可执行性均为**待确认**，因为未连接数据库。

## 配置、安全与可观测性

- 数据库 URI 存在于本地 `config.py`，该文件被 `.gitignore` 忽略；未发现环境变量读取、配置模型或多环境分层。
- JWT 使用 HS256，包含 access/refresh token 创建与解析逻辑（`core/auth.py`）。签名密钥为源码中的静态配置，本文不记录其值。
- OAuth2 Bearer 方案定义在 `routers/authority.py`。`/user/info` 自行解析 access token 并比较 token 内用户 ID 与查询参数；删除接口没有认证依赖。完整风险见 [审计报告](audit-report.md)。
- `main.py` 注册 HTTP、请求校验和 `AppException` 处理器；`RouteLoggerMiddleware` 记录方法、路径、路由、端点和状态码。引擎配置 `echo=True`，且部分路径使用 `print`；日志脱敏、结构化格式、请求 ID 和生产日志策略均为**待确认**。

## 典型调用链：读取当前用户

```text
GET /user/info?userId={id}
  → OAuth2PasswordBearer 从 Authorization 头取 token
  → core.auth.decode_token(token, "access")
  → 路由比较 token.user_id 与 userId
  → Depends(get_session) 创建 AsyncSession
  → select(User).where(User.id == userId)
  → success_response(User) → ApiResponse[UserInfoResponse]
  → RouteLoggerMiddleware 记录响应
```

实现位置：`routers/user.py:81-100`、`core/auth.py:25-34`、`dependencies.py:2-7`、`middleware/routerLogger.py:14-47`。该链路仅完成静态追踪，未对真实数据库或 HTTP 响应执行验证。

## 测试、外部依赖与限制

未发现 Python 自动化测试、pytest 配置、Ruff/Black/类型检查配置、CI 或容器部署文件。质量基线已实际验证源码 AST 解析、已安装包元数据和 `import main`；pytest 收集因未安装 pytest 被阻断。详情见 [质量基线](quality-baseline.md)。

当前技术债务与待确认事项包括：缺少隔离测试数据库、依赖可复现性不足、响应模型不一致、认证/授权路径尚未集成验证、迁移对存量数据的影响未演练，以及部署与生产配置未记录。
