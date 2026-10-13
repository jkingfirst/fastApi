from . import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, true
from typing import List
from pwdlib import PasswordHash


# 使用推荐的配置（默认即为 Argon2）
password_hash = PasswordHash.recommended()
def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
# 用户
class User(Base):
    __tablename__ = 'user'
    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True) #ID主键，自增长
    email:Mapped[String] = mapped_column(String(100),unique=True,index=True) #邮箱字符最大长度100,唯一标识,index 方便使用email查找速度更快
    username:Mapped[String] = mapped_column(String(100))
    hashed_password: Mapped[String] = mapped_column(String(300))
    mobile:Mapped[String] = mapped_column(String(100))
    disabled:Mapped[bool] = mapped_column(Boolean,default=True,nullable=False,server_default=true(),comment='是否激活')
    user_profile:Mapped['UserProfile'] = relationship(back_populates='user',uselist=False)
    articles:Mapped[List['Article']] = relationship('Article',back_populates='author',)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
       self.hashed_password = get_password_hash(password)
#表user和user_profile的一对一
#个人资料，保存一些非常用字段
class UserProfile(Base):
    __tablename__ = 'user_profile'
    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,index=True)
    university:Mapped[str] = mapped_column(String(100))
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('user.id'),unique=True) #用户ID关联user表内id
    user:Mapped[User] = relationship(User,back_populates='user_profile') #反向关联user表