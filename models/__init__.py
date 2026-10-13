from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker
# 导入 SQLAlchemy ORM 的基类，所有数据模型都要继承它
from sqlalchemy.orm import DeclarativeBase
from config import DB_URI
# 导入 MetaData，用于管理数据库表结构的元数据（表名、列、约束等）
from sqlalchemy import MetaData


# 创建异步数据库引擎对象，主要负责数据连接、连接池维护、SQL 语句翻译， 异步引擎对象
engine = create_async_engine(
    DB_URI,
    echo=True,            # 打印执行的 SQL，便于调试
    pool_size=5,          # 连接池保持的连接数
    max_overflow=10,      # 连接池满时允许额外创建的连接数
    pool_timeout=30,      # 链接超时时间
    pool_pre_ping=True,   # 取出连接前先检测连接是否有效
    pool_recycle=3600,    # 连接自动回收时间（秒），防止 MySQL 长时间空闲断开 -1代表永不回收
)
#创建会话工厂来操作数据
AsyncSessionFactory = async_sessionmaker(
    engine,
    #session类的替代
    class_=AsyncSession,
    autoflush=True,
    expire_on_commit=False,
)



# 定义自定义的 Base 类，继承自 DeclarativeBase
class Base(DeclarativeBase):
    # 重写 metadata 属性，配置命名约定（自动生成约束和索引的名称规则）
    metadata = MetaData(
        # naming_convention 是一个字典，键为约束/索引类型，值为名称模板字符串
        naming_convention={
            # 索引（Index）的命名规则：ix_列名（通常用列标签，即列名）
            "ix": "ix_%(column_0_label)s",
            # 唯一约束（Unique）的命名规则：uq_表名_列名
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            # 检查约束（Check）的命名规则：ck_表名_约束名（需在模型里指定约束名）
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            # 外键约束（Foreign Key）的命名规则：fk_表名_列名_关联表名
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            # 主键约束（Primary Key）的命名规则：pk_表名
            "pk": "pk_%(table_name)s",
        }
        # MetaData 的括号闭合
    )
# Base 类定义结束
from . import user
from . import article