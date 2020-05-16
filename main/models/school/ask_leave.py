"""
请假 models
"""
from flask_login import current_user
from flask import flash
from sqlalchemy import or_
import datetime as dt
from main.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)

from main.models.auth.users import User
from main.models.auth.users import Student
from main.models.school.grade import Grade
from main.models.auth.users import Teacher



class AskLeave(SurrogatePK,Model):
    """请假列表"""
    
    __tablename__ = "ask_leave"
    
    reason = Column(db.String(100),comment='请假事由')
    start_at = Column(db.DateTime, nullable=False, default=dt.datetime.now,comment='请假开始时间')
    end_at = Column(db.DateTime, nullable=False, comment='请假结束时间')
    status = Column(db.Integer(),default=0,comment='状态 0已发起 1审批中 2 完成审批 3已出校门 4请假完成  -1拒绝')
    send_user = Column(db.Integer(),comment='发起人')
    ask_user = Column(db.Integer(),comment='请假用户  谁要请假')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now,comment='创建时间')
    
    @classmethod
    def insert_data(cls,form):
        
        user = User.query.filter(or_(User.name==form.get("ask_user"),User.q_number==form.get("ask_user"))).first()
        if not user:
            flash("没有该用户")
            return False
        result = cls.query.filter_by(ask_user=user.id).filter(AskLeave.status.in_([0,1,2])).first()
        if result:
            flash("该用户已经在请假中了，不能重复申请假期")
            return False
        reason = form.get("reason_check") +"|"+ form.get("reason")
        
        ask_id = cls.create(
            reason = reason,
            start_at =  form.get("start_at"),
            end_at =  form.get("end_at"),
            send_user = current_user.id,
            ask_user = user.id,
        )
        AskApproved.insert_data(ask_id,user.id)
        # 此处应该发起通知 相关用户
        flash("添加完成")
        return {"msg":"已发起请假，请等待审批",'state':1}
    
    
   


class AskApproved(SurrogatePK,Model):
    """请假审批表
    审批为班主任  后期可以扩展成 多人审批
    """
    
    user_id = Column(db.Integer(),comment='审批人')
    ask_id = Column(db.Integer())
    status = Column(db.Integer(),default=0,comment='状态0 未审批  1 已审批   -1 已拒绝 2已转交')
    approved_at = Column(db.DateTime, nullable=False, default=dt.datetime.now,comment='审批时间')
    remark = Column(db.String(100),comment='审批说明')
    
    @classmethod
    def insert_data(cls,ask_id,user_id):
        """ask_id请假ID  user_id请假用户ID """
        print(ask_id)
        print(user_id)
        # 获得班级ID
        grade_id = Student.query.filter_by(user_id=user_id).first().grade_id
        print(grade_id)
        # 班主任 userID
        grade = Grade.get_by_id(grade_id)
        print(grade.teacher_id)
        teacher = Teacher.get_by_id(grade.teacher_id)
        print(teacher)
        app_ask_id = teacher.user_id
        cls.create(
            user_id = app_ask_id,
            ask_id =  ask_id.id
        )
        
        # 此处应该通知班主任
        
    @classmethod
    def update_data(cls,args):
        ask = AskLeave.get_by_id(args.get('id'))
        state = args.get('state')
        if not ask:
            return False
        
        # 判断是否自己的审批
        approved_self = cls.query.filter_by(ask_id=ask.id,user_id=current_user.id).all()
        if not approved_self:
            return False
        
        approved = cls.query.filter_by(ask_id=ask.id).all()
        if not approved:
            return False
        
        if approved[0].status in [0]:
            approved[0].update(status=state,remark='',approved_at=dt.datetime.now())
            if len(approved)==1:
                ask.update(status=state)
            return True
        else:
            return False
        
    @classmethod
    def get_by_list(cls):
        result = AskApproved.query.with_entities(AskLeave,AskApproved,User)\
            .join(AskLeave,AskLeave.id==AskApproved.ask_id)\
            .join(User,User.id==AskLeave.ask_user)\
            .filter(AskApproved.user_id==current_user.id)\
            .filter(AskLeave.status==0)\
            .all()
        return result

    


