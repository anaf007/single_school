"""
菜单权限 models
"""
from main.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
import datetime as dt
from flask_login import current_user

class Menu(SurrogatePK, Model):
    
    __tablename__ = "menu"
    __table_args__ = {'comment': '菜单表'}
    
    title = Column(db.String(100), nullable=False)
    pid = Column(db.Integer(),comment="上级")
    status = Column(db.Integer(),comment="状态",default=0)
    sort = Column(db.Integer(),comment="排序",default=100)
    is_url = Column(db.Boolean(),comment="是否路由地址",default=False)
    url = Column(db.String(200),comment="路由地址")
    blueprint = Column(db.String(50),comment="蓝图地址")
    icon = Column(db.String(50),comment="图标")
    
    
    @classmethod
    def insert_data(cls,form):
        status = True if form.get("status") else False
        sort =  True if form.get("sort") else None
        is_url =  True if form.get("is_url") else None
        pid =  True if form.get("pid") else 0
        cls.create(
            title = form.get("title"),
            pid = pid,
            status = status,
            sort = sort,
            is_url = is_url,
            url = form.get("url"),
            blueprint = form.get("bp"),
            icon = form.get("icon")
        )


class Access(SurrogatePK,Model):
    
    __tablename____ = "access"
    __table_args__ = {'comment': '权限表'}
    
    url = Column(db.String(200), nullable=False,comment="路由正则匹配")
    name = Column(db.String(100),comment="节点名称")
    status = Column(db.Integer(),comment="状态",default=1)
    sort = Column(db.Integer(),comment="排序",default=100)
    is_del = Column(db.Boolean(),comment="是否删除",default=False)
    create_at = Column(db.DateTime(),default=dt.datetime.now,comment='创建时间')
    user_id = Column(db.Integer(),comment="创建用户")
    
    @classmethod
    def insert_data(cls,form):
        status = True if form.get("status") else False
        sort = form.get("sort") if form.get("sort") else 100
        is_del = True if form.get("is_del") else False
        is_url =  form.get("is_url") if form.get("is_url") else ''
        pid =  form.get("pid") if form.get("pid") else 0
        is_del =  True if form.get("pid") else False
        cls.create(
            name = form.get("name"),
            url = form.get("url"),
            status = status,
            sort = sort,
            is_del = is_del,
            user_id = current_user.id
        )
    
    

