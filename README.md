
```bash
alembic init alembic --template async //创建迁移仓库
alembic revision --autogenerate -m "init" //更新数据表
alembic upgrade head // 同步到数据库
```
