
# 用户管理系统 API

这是一个 FastAPI、SQLAlchemy 异步 ORM、MySQL 和 Alembic 组成的示例项目。当前应用入口、依赖、测试状态和开发约束请阅读 [开发与维护流程](docs/ai/development-workflow.md)。

## 数据库迁移

项目已包含 `alembic/` 迁移仓库，**不要重复执行**以下初始化命令：

```bash
alembic init alembic --template async
```

以下命令会创建仓库文件或改变数据库结构；当前项目没有已验证的隔离测试数据库配置，未经确认不得执行：

```bash
# 生成迁移文件：会写入仓库，生成后必须人工审核
alembic revision --autogenerate -m "<message>"

# 升级数据库：会改变目标数据库
alembic upgrade head
```

执行迁移前必须确认 `config.py` 指向隔离测试数据库，准备备份与回滚方案，并在变更后验证关键业务流程。请勿在生产或来源不明的数据库上直接执行迁移。
