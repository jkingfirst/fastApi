from . import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import INTEGER,String,ForeignKey
from typing import List
#文章表
class Article(Base):
    __tablename__ = 'article'
    id:Mapped[int] = mapped_column(INTEGER,primary_key=True,autoincrement=True)
    title:Mapped[str] = mapped_column(String(100))
    content:Mapped[str] = mapped_column(String(500))
    author_id:Mapped[int] = mapped_column(INTEGER,ForeignKey('user.id'))
    author:Mapped['User'] = relationship('User',back_populates='articles')
    tags:Mapped[List['Tag']] = relationship('Tag', secondary='article_tag')
# 文章标签
class Tag(Base):
    __tablename__ = 'tag'
    id:Mapped[int] = mapped_column(INTEGER,primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(100))
    articles:Mapped[List['Article']] = relationship('Article', back_populates='tags',secondary='article_tag')
#多对多关联表
class ArticleTag(Base):
    __tablename__ = 'article_tag'
    tag_id:Mapped[int] = mapped_column(INTEGER,ForeignKey('tag.id'),primary_key=True)
    article_id:Mapped[int] = mapped_column(INTEGER,ForeignKey('article.id'),primary_key=True)
