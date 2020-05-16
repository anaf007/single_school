"""
出入记录 models
"""
import datetime as dt
import re

from main.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from main.models.auth.users import User
from main.models.school.ask_leave import AskLeave
from main.models.school.grade import Grade
from main.models.auth.users import Student

class AccessRecords(SurrogatePK,Model):
    
    __tablename__ = "access_records"
    
    user_id:int = Column(db.Integer(),comment='用户ID')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now,comment='创建时间')
    
    @classmethod
    def insert_data(cls,q_number)->dict:
        q_number:str = q_number
        print(q_number)
        # if not re.match('^S\d', q_number):
        #     return {'msg':'输入错误',"code":-1}
        # q_number = q_number.replace('S','').strip()	
        
        user = User.query.filter_by(q_number=q_number).first()
        if not user:
            return {"msg":"信息错误，没有该用户信息","code":-1}
        else:
            user_id = user.id
            
        cls.create(
            user_id = user_id
        )
            
        # 根据编号头位S为学生
        # 查询是否有请假状态
        if q_number[:1]=="S":
            ask_leave:AskLeave = AskLeave.query.filter_by(ask_user=user_id).filter(AskLeave.status.in_([0,1,2,3])).first()
            student = Student.query.with_entities(Student,Grade.name).join(Grade,Grade.id==Student.grade_id).filter(Student.user_id==user.id).first()
            
            if ask_leave:
                
                if ask_leave.status==0:
                    return {"msg":"该学生的请假信息等待审批中。",'code':-1}
                if ask_leave.status==1:
                    return {"msg":"该学生的请假信息正在审批中。",'code':-1}
                if ask_leave.status==2:
                    ask_leave.update(status=3)
                    return {"msg":"学生:"+user.name+"【"+student[1]+"】"+"请假已生效",'code':1,"avatar":user.avatar}
                if ask_leave.status==3:
                    ask_leave.update(status=4)
                    return {"msg":"学生:"+user.name+"【"+student[1]+"】"+"请假已归来",'code':1,"avatar":user.avatar}
                
                
            return {"msg":"【"+student[1]+"】"+user.name+"已扫描","code":1,"avatar":user.avatar}
                
        return {"msg":user.name+"已出入","code":1}
   
    