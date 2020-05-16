"""
车辆 models

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


class Car(SurrogatePK,Model):
    
    __tablename__ = "car"
    
    number = Column(db.String(100),comment='车牌号')
    car_type = Column(db.String(100),comment='车辆类型')
    brand = Column(db.String(100),comment='品牌')
    colour = Column(db.String(100),comment='颜色')
    status = Column(db.Integer(),default=0,comment='状态默认')
    user_id = Column(db.Integer())
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now,comment='创建时间')
    
    @classmethod
    def insert_data(cls,form):
        status = True if form.get("status") else False
        cls.create(
            number = form.get("number"),
            car_type = form.get("car_type"),
            status = status,
            brand = form.get("brand"),
            colour = form.get("colour"),
            user_id = form.get("user_id"),
        )
   

    