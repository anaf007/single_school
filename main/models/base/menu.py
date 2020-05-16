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

class Menu(SurrogatePK, Model):
    
    __tablename__ = "menu"
    __table_args__ = {'comment': '菜单权限表'}
    
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
        is_url = True if form.get("is_url") else False
        cls.create(
            title = form.get("title"),
            pid = form.get("pid"),
            status = status,
            sort = form.get("sort"),
            is_url = is_url,
            url = form.get("url"),
            blueprint = form.get("blueprint"),
            icon = form.get("icon")
        )


