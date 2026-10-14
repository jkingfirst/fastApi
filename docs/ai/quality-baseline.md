# 项目质量基线

## 1. 基本信息

- 检查日期：2026-10-14（Asia/Shanghai）
- 项目：用户管理系统 API（FastAPI 应用；名称来自 `main.py`）
- Git：`master` 分支，当前提交 `8cfdeec`（`first commit`）
- Python：CPython 3.13.14；虚拟环境由 virtualenv 20.38.0 创建。
- 主要技术栈：FastAPI 0.141.1、Pydantic 2.13.4、SQLAlchemy 2.0.52、aiomysql 0.3.2、Alembic、Uvicorn、Scalar API 文档。版本依据为 `requirements.txt`，未逐项验证已安装版本。
- 依赖管理：仅发现 `requirements.txt`；未发现 `pyproject.toml`、锁文件、Poetry、uv 或 Pipenv 配置。

本报告不记录数据库凭据、JWT 密钥、Token 或其他敏感配置值。

## 2. 检查结果汇总

| 检查项 | 执行命令 | 状态 | 结果与证据 | 备注 |
| --- | --- | --- | --- | --- |
| 单元测试 | `.venv/bin/python -B -m pytest --collect-only -q` | BLOCKED | 退出码 1：`No module named pytest`。未发现 `test_*.py`、`*_test.py` 或 pytest 配置。 | 未安装 pytest；未执行任何测试。 |
| 集成测试 | 未执行 | BLOCKED | 仅发现 `test_main.http`，其中包含 `POST /user/add`。该请求可能写入配置的数据库。 | 未确认测试数据库隔离，不能安全运行。 |
| 测试覆盖率 | 未执行 | N/A | 未发现测试框架、覆盖率工具或覆盖率配置。 | 建立自动化测试后再配置。 |
| Ruff / 代码检查 | 未执行 | N/A | `.venv/bin/ruff` 不存在；未发现 Ruff 配置。 | 不代表源码符合风格或质量要求。 |
| Black / 格式检查 | 未执行 | N/A | 未发现 Black 可执行文件或配置。 | 不代表格式已验证。 |
| 类型检查 | 未执行 | N/A | `.venv/bin/mypy`、`.venv/bin/pyright` 不存在；未发现相关配置。 | 不代表类型安全已验证。 |
| 源码语法解析 | `.venv/bin/python -B -c "<AST 解析脚本>"` | PASS | 退出码 0：`AST_PARSE_OK files=26`。脚本只在内存中解析项目 `.py` 文件，排除 `.git`、`.venv`、`__pycache__`。 | 只验证语法，不验证导入、类型或运行行为。 |
| 已安装包元数据 | `.venv/bin/python -B -m pip check` | PASS | 退出码 0：`No broken requirements found`。 | 仅验证当前环境已安装包的元数据关系，不能证明 `requirements.txt` 包含所有源码直接依赖。 |
| 应用导入验证 | `.venv/bin/python -B -c "import main; print('APP_IMPORT_OK')"` | PASS | 退出码 0，输出 `APP_IMPORT_OK`。 | 未启动 ASGI 服务、未发送 HTTP 请求；SQLAlchemy 引擎创建是惰性的，本次未执行 SQL。导入时有示例 `print` 输出。 |
| 文档端点 HTTP 验证 | 受控启动 `.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001`，再对 `/docs`、`/openapi.json`、`/scalar` 执行 GET | PASS | 2026-10-14：三个端点均返回 HTTP 200。 | 仅请求文档端点；未调用业务 API、未执行迁移或数据库操作。 |
| 数据库连接 / 迁移 | 未执行 | NOT RUN | 项目使用 MySQL、SQLAlchemy 和 Alembic，但未确认配置是否指向隔离测试库。 | 未连接数据库，未执行 `alembic` 命令。 |
| CI 检查 | 未执行 | N/A | 未发现 `.github/` 工作流或其他 CI 配置。 | 无法建立远程流水线基线。 |

`-B` 用于避免生成 Python 字节码。`pip check` 曾输出 pip 缓存目录不可写的警告并禁用缓存；该警告未影响检查退出码，也没有安装或变更依赖。

## 3. 已知问题

### 已证实

1. **自动化测试与检查工具缺失**：未发现 Python 测试文件、pytest 配置、pytest/Ruff/Black/mypy/pyright 可执行文件或 CI 配置。证据见本报告“检查结果汇总”。
2. **依赖清单与源码直接导入不一致**：`core/auth.py` 导入 `jwt`，`models/user.py` 导入 `pwdlib`，认证路由使用 `OAuth2PasswordRequestForm`；`requirements.txt` 未声明 PyJWT/jwt、pwdlib 或 python-multipart。`pip check` 通过不能覆盖这一问题，因为它不检查源码导入。可能影响干净环境安装、应用导入或表单登录。
3. **应用导入含无业务示例输出**：`main.py:97-121` 在模块导入期间构造示例对象并执行 `print`；本次导入验证已观察到这些输出。该问题不阻断导入，但会污染启动日志。
4. **HTTP 测试文件不能作为安全的自动化基线直接执行**：`test_main.http` 含 `POST /user/add`，没有测试数据库、清理逻辑或隔离配置证据。

### 已在第二阶段静态审计发现，尚未通过运行验证

1. `routers/user.py:67-76` 的用户删除接口未声明认证或授权依赖，并按请求中的 `userId` 执行删除；是否可被外部匿名访问仍需隔离 API 测试确认。
2. `main.py:53` 引用未在 `core/errorCode.py` 定义的 `ErrorCode.UNKNOWN`；进入该 HTTP 异常处理器的实际响应行为尚未通过请求测试确认。
3. `models/user.py` 未对 `username` 建立唯一约束，而 `routers/authority.py:56-60` 使用 `scalar_one_or_none()` 按用户名登录查询；重复用户名时的运行行为需要数据库测试确认。
4. `alembic/versions/04cb628fe7e5_修改密码字段.py` 未呈现既有密码数据回填策略；迁移对已有用户数据的影响未验证。

## 4. 当前质量风险

### 已证实风险

- 项目目前没有可执行的自动化测试、覆盖率、代码格式/静态检查或 CI 基线，关键逻辑无法防回归。
- 本地环境可以导入应用，但这一结果不代表 HTTP 路由、认证、数据库事务或迁移正确。
- `requirements.txt` 不能独立证明可复现安装，因为源码直接依赖与清单存在静态不一致。
- 生产或非隔离数据库连接风险未被排除，因此数据库测试和迁移验证不能在当前条件下安全执行。

### 待验证风险

- 用户删除权限、HTTP 异常响应、重复用户名登录、密码迁移和关联数据删除的实际行为。
- ORM 响应序列化、JWT 过期/错误 Token 分支、注册冲突与并发写入。
- 部署环境的配置注入、密钥轮换、日志脱敏、优雅停止和数据库连接释放。

## 5. 建议的下一步

1. 确认并提供完全隔离的测试数据库配置；明确禁止测试访问真实或生产数据库。
2. 在批准后补齐并锁定直接运行依赖，使用新虚拟环境验证安装、应用导入和 OAuth2 表单登录。
3. 建立 pytest 基础设施与最小 fixture，优先覆盖未鉴权删除、HTTP 异常处理、注册重复值、登录、Token 校验和数据库事务回滚。
4. 明确用户唯一标识、`disabled` 字段语义和删除关联数据策略，再制定数据迁移、备份与回滚方案。
5. 在测试可重复运行后，增加覆盖率、Ruff/格式检查、类型检查和 CI；不要将这些建议的检查视为已通过。

## 6. 更新记录

### 2026-10-14

- 新建本质量基线报告。
- 记录了已有真实执行证据：`pip check`、pytest 收集探测、26 个 Python 文件 AST 解析和 `import main` 验证。
- 明确标记了未执行、被环境安全条件阻断或经项目配置确认不适用的检查。
- 未修改应用代码、测试代码、依赖配置、数据库配置或迁移文件。
- 受控启动本地服务并验证 `/docs`、`/openapi.json`、`/scalar` 均返回 HTTP 200；服务随后已停止。
