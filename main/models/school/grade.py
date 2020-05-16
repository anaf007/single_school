"""
年级 models
"""
from flask  import flash

import datetime as dt
from main.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from main.models.auth.users import Teacher


class Grade(SurrogatePK,Model):
    
    __tablename__ = 'grade'
    __table_args__ = {'comment': '年级班级表'}
    
    name = Column(db.String(100),comment='班级名称')
    remark = Column(db.String(200),comment='描述')
    teacher_id = Column(db.Integer(),comment='教师ID')
    sort = Column(db.Integer(),default=100)
    
    @classmethod
    def insert_data(cls,form):
        teacher_id = form.get("teacher_id") if form.get("teacher_id") else  0
        sort = form.get("sort") if form.get("sort") else  100
        phone = form.get('phone')
        teacher = Teacher.query.filter_by(phone=phone).first()
        if not teacher:
            flash("该手机号不正确，没有对应的教师")
            return False
        cls.create(
            name = form.get("name"),
            remark =  form.get("remark"),
            teacher_id =  teacher.id,
            sort =  sort,
        )
