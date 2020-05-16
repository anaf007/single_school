"""
角色  models
"""

import datetime as dt

from main.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)

from main.models.auth.menu import Access


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), nullable=False)
    pid = Column(db.Integer(),comment="上级")
    remark = Column(db.String(100),comment="描述")
    sort = Column(db.Integer(),server_default='100',comment='排序')
    create_at = Column(db.DateTime(),comment='创建时间',default=dt.datetime.now)
    is_del = Column(db.Boolean(),comment="是否删除",default=False)

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"
    
    @classmethod
    def insert_data(cls,form):
        sort =  form.get("is_url") if form.get("is_url") else 100
        is_url =  True if form.get("is_url") else ''
        pid =  True if form.get("pid") else 0
        is_del =  True if form.get("pid") else False
        cls.create(
            name = form.get("name"),
            pid = pid,
            remark =  form.get("remark"),
            sort = sort,
            is_del = is_del,
        )

    
class RoleAccess(SurrogatePK,Model):
    """
    权限暂定menu菜单表
    """
    
    __tablename__ = "role_access"
    
    role_id = Column(db.Integer(),comment='角色ID')   
    access_id = Column(db.Integer(),comment="权限ID") 
    
    @classmethod
    def insert_data(cls,form):
        access_id = form.getlist("access")
        role_id = form.get("role_id")
        role_access = cls.query.filter_by(role_id=role_id).all()
        for x in role_access:
            cls.delete(x)
            
        for x in access_id:
            cls.create(
                role_id = role_id,
                access_id = x
            )
            
    @classmethod
    def all_access_data(cls,role_id):
        all_access = Access.query.all()
        role_access = RoleAccess.query.with_entities(Access,RoleAccess).join(Access,Access.id==RoleAccess.access_id).filter(RoleAccess.role_id==role_id).all()
        access_data = {}
        for x in all_access:
            access_data[x.id] = [x.id,x.name,0]
        for x in role_access:
            if x[0].id in access_data.keys():
                access_data[x[0].id] = [access_data[x[0].id][0],access_data[x[0].id][1],1]
                
        return access_data
            
        