# 开发与维护流程

> 本文仅记录当前仓库可以确认的流程。标注“未验证”的命令是基于现有入口或文档推导，不应视为已在本项目成功运行。任何数据库写入、迁移或清理均须先确认目标为隔离环境。

## 环境要求

- 当前本地虚拟环境：CPython 3.13.14。仓库没有 `.python-version` 或 `pyproject.toml`，团队最低/最高 Python 版本为**待确认**。
- 依赖来源：`requirements.txt`，没有锁文件。
- 数据库：代码使用 MySQL 异步驱动 `aiomysql` 和 SQLAlchemy；连接 URI 由本地 `config.py` 提供。不要提交、打印或在文档中填写真实凭据。

创建虚拟环境的通用示例（**未验证**）：

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

安装会改变本地环境。并且当前清单缺少源码直接使用的若干依赖，详见 [审计报告](audit-report.md)；在批准补齐前，干净环境安装不应被视为可复现。

## 本地运行

ASGI 入口是 `main:app`。以下启动命令基于该入口和已声明的 Uvicorn（**未验证**）：

```bash
.venv/bin/uvicorn main:app --reload
```

该命令会加载本地数据库配置；应用启动后首次数据库访问可能连接该数据库。仅在确认配置指向安全本地环境后执行。

应用代码注册 Scalar 文档路径 `/scalar`。FastAPI 默认 `/docs`、`/openapi.json` 和 `/redoc` 未在代码中覆盖。2026-10-14 的受控本地验证中，`/docs`、`/openapi.json` 和 `/scalar` 均返回 HTTP 200；`/redoc` 未请求，仍属未验证。

已实际验证的非服务启动检查：

```bash
.venv/bin/python -B -c "import main; print('APP_IMPORT_OK')"
```

该命令在 2026-10-13 实际退出码为 0；它只验证模块可导入，不启动服务器或验证数据库/API。导入会打印 `main.py` 中的示例输出。

## 测试与质量检查

当前没有 Python 测试文件、pytest 配置或 pytest 安装。以下收集命令曾实际执行并返回退出码 1：

```bash
.venv/bin/python -B -m pytest --collect-only -q
# No module named pytest
```

不要把该结果记录为业务测试失败；它表示测试工具不可用。`test_main.http` 仅是 HTTP 客户端样例，含 `POST /user/add`，可能写数据库；不得直接作为无副作用测试运行。

已实际通过的安全检查：

```bash
.venv/bin/python -B -m pip check
# 退出码 0：No broken requirements found
```

```bash
# 内存 AST 解析项目 Python 文件（排除 .git、.venv、__pycache__）
.venv/bin/python -B -c "import ast, pathlib; files=[p for p in pathlib.Path('.').rglob('*.py') if not any(part in {'.git','.venv','__pycache__'} for part in p.parts)]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'AST_PARSE_OK files={len(files)}')"
# 退出码 0：AST_PARSE_OK files=26
```

`pip check` 不会检查源码直接导入是否都列在 `requirements.txt`。项目未配置 Ruff、Black、mypy、pyright、覆盖率或 CI；不要执行或宣称这些检查已通过。建议在获批后先建立隔离测试环境，再引入并固定相应工具。

## 数据库与迁移

现有 README 记录了以下 Alembic 命令：

```bash
alembic init alembic --template async
alembic revision --autogenerate -m "<message>"
alembic upgrade head
```

这些命令均**未验证**；其中 `init`/`revision` 会写入仓库，`upgrade head` 会改变数据库结构或数据。当前已有 Alembic 目录，因此通常不应重复执行 `init`。在执行 `revision`、`upgrade` 或 `downgrade` 前必须：

1. 确认 `config.py` 指向隔离测试数据库，绝不指向生产；
2. 检查当前迁移版本和备份/恢复方案；
3. 审核自动生成脚本，尤其是密码字段和用户状态相关变更；
4. 在匿名化副本演练升级、核心登录流程和回滚。

这些步骤均为建议流程，当前没有测试数据库或迁移演练记录。

## Git 与提交前检查

在开始和提交前运行 `git status --short --branch`、`git diff --check` 与 `git diff -- <changed-files>`。它们只读检查 Git 状态/文本格式。提交前还应运行与变更相关的测试；当前自动化测试体系缺失，因此不能以“未运行”替代通过。不得重置、清理或覆盖他人的未提交修改。

## 当前未实现或待确认流程

- 无 Docker、Compose、CI/CD、部署清单或生产启动参数。
- 无测试数据库切换、fixture、数据清理和外部服务 mock 机制。
- 无锁定依赖、代码格式、类型检查、覆盖率阈值或发布检查规则。
- 无密钥注入、JWT 轮换、日志采集与告警的可验证运行手册。

这些是待补充的工程能力，不是当前已实现的流程。任何新增依赖、迁移、CI/CD 或部署修改都应先获得批准。

## 常见问题排查

- **`No module named pytest`**：当前虚拟环境未安装 pytest；不要在未经批准时自行安装。
- **干净环境无法导入 JWT/密码哈希/表单相关模块**：检查 [审计报告](audit-report.md) 的 P1-03；先确认并补齐直接依赖后再验证。
- **数据库或迁移命令风险不明**：停止执行，先确认 `config.py` 的目标库和备份策略。
- **启动时出现示例输出**：由 `main.py` 底部的顶层示例代码导致；已记录为 P3-01，未在本任务中修改。
