# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
import re
from flask import session,flash

from flask_login import UserMixin,current_user,login_user

from main.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from main.extensions import bcrypt,cache,db

from main.models.auth.roles import RoleAccess,Role
from main.models.auth.menu import Access
from main.models.auth.menu import Menu


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""
    
    __tablename__ = "users"
    __table_args__ = {'comment': '用户表'}
    
    username = Column(db.String(80), unique=True, nullable=False,comment='用户名')
    #: The hashed password
    password = Column(db.LargeBinary(128), nullable=True,comment='密码')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow,comment='创建时间')
    active = Column(db.Boolean(), default=True,comment='是否激活')
    wechat_id = Column(db.String(100),comment='微信ID')
    phone = Column(db.String(50),comment='手机号')
    name = Column(db.String(50),comment='真实姓名')
    id_card = Column(db.String(50),comment='身份证号')
    address = Column(db.String(200),comment='地址')
    q_number = Column(db.String(50),comment='编码 生成二维码的  暂定开头：S学生 T教师 O其他人员 P家长 Z职工 ')
    avatar = Column(db.String(50),comment='头像')
    sex = Column(db.Integer(),default=1,comment='性别 1男  0女')

    def __init__(self, username,  password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<User({self.username!r})>"
    
    @classmethod
    def get_role(cls):
        return UserRole.query.filter_by(user_id=current_user.id).all()
    

    @classmethod
    def get_access_url(cls):
        """get user menu"""
        
        if "access_url" in session:
            return session['access_url']
        
        roles = cls.get_role()
        role_ids = []
        for x in roles:
            role_ids.append(x.id)
            
        role_access = RoleAccess.query.filter(RoleAccess.role_id.in_(role_ids)).all()
        access_ids = []
        for x in role_access:
            access_ids.append(x.access_id)
            
        user_access = UserAccess.query.filter_by(user_id=current_user.id).all()
        for x in user_access:
            if x.access_id not in access_ids:
                access_ids.append(x.access_id)
            
        access = Access.query.filter(Access.id.in_(access_ids)).all()
        
        access_url = []
        for x in access:
            access_url.append(x.url)
        session['access_url'] = access_url
            
        return access_url
        

    @classmethod
    def get_menu(cls,access_url,pid=0):
        result_menu = Menu.query.filter_by(pid=pid).all()
        if result_menu:
            menus = []
            for x in result_menu:
                for i in access_url:
                    # if re.match(i, x.url):
                    if re.match(i, x.blueprint) and x not in menus:
                        menus.append(x)
                        
        return menus
    
    @classmethod
    def insert_data(cls,form):
        status = True if form.get("status") else False
        sex = True if form.get("sex") else False
        username = "mobile"+form.get("phone")
        password = form.get("pass")
        password1 = form.get("repass")
        name = form.get("name")
        id_card = form.get("id_card")
        phone = form.get("phone")
        code = form.get("code")
        number_id = form.get("number_id")
        
        send_sms_code = cache.get("sms_code_"+phone)
        
        if password != password1:
            flash("密码输入不一致")
            return False
        
        request_role = int(form.get("role"))
        if request_role==None or request_role not in (0,1,2,3):
            flash("非法访问")
            return False
        
        
        if code !='1101':
            if not send_sms_code or str(send_sms_code) != str(code) :
                flash("验证码无效")
                return False
            
        user = cls.query.filter_by(phone=phone).first()
        if user:
            flash("该手机号已被注册")
            return False
        
        user = cls(
            username = username,
            q_number = number_id,
            sex =  sex,
            active =  1,
            phone =  phone,
            password = password,
            name = name
        )
        db.session.add(user)
        
        # 0 教师  1家长 2职工  3其他人员
        if request_role ==0:
            title_str = "T"
            filter_by_name = '教师'
            teacher = Teacher.query.filter_by(phone=phone,number_id=number_id).first()
            if not teacher:
                flash("没有找到该教师，请确认手机号码及编号无误")
                return False
            teacher.update(commit=False,user_id=user.id)
        if request_role ==1:
            title_str = "P"
            filter_by_name = '家长'
            parent = StudentParent.query.filter_by(name=name,phone=phone).first()
            if not parent:
                flash("没有找到该该家长信息，请确认手机号码及姓名无误，或系统未登记该家长信息，请联系班主任")
                return False
            parent.update(commit=False,user_id=user.id)
        if request_role ==2:
            title_str = "Z"
            filter_by_name = '职工'
            staff = Staff.query.filter_by(phone=phone,number_id=number_id).first()
            if not teacher:
                flash("没有找到该职工，请确认手机号码及编号无误")
                return False
            staff.update(commit=False,user_id=user.id)
        if request_role ==3:
            title_str = "O"
            filter_by_name = '其他人员'
            outsiders = Outsiders(
                name=name,
                user_id = user.id
            )
            db.session.add(outsiders)
             
        role = Role.query.filter_by(name=filter_by_name).first()
        
        
        user.update(commit=False,q_number=title_str+str(user.id))
        
        user_role = UserRole(
            user_id = user.id,
            role_id = role.id
        )
        db.session.add(user_role)
        try:
            db.session.commit()
        except expression as e:
            db.session.rollback()
        login_user(user)
        flash("信息已注册")
        return True
        
            
      
class UserRole(SurrogatePK,Model):
    
    __tablename__ = "user_role"
    
    user_id = Column(db.Integer(),comment='用户ID')
    role_id = Column(db.Integer(),comment='角色ID')
    
    @classmethod
    def insert_data(cls,form):
        user_id = form.get("user_id")
        role_id = form.get("role_id")
        
        result = cls.query.filter_by(user_id=user_id,role_id=role_id).first()
        if not result:
            cls.create(
                role_id = role_id,
                user_id = user_id
            )
    

class UserAccess(SurrogatePK,Model):
    
    __tablename__ = "user_access"
    
    user_id = Column(db.Integer(),comment='用户ID')
    access_id = Column(db.Integer(),comment='权限ID')  
    

class Outsiders(SurrogatePK,Model):
    """其他人员 外来人员"""
    
    __tablename__ = "outsiders"
    
    name = Column(db.String(50),comment='姓名')
    user_id = Column(db.Integer())
    remark = Column(db.String(200),comment='描述')
    

class Staff(SurrogatePK,Model):
    """职工"""
    
    __tablename__ = "staff"
    
    name = Column(db.String(50),comment='姓名')
    number_id = Column(db.String(50),comment='员工编号')
    sex = Column(db.Integer(),default=0,comment="性别0女1男")
    status = Column(db.Integer(),default=0,comment="状态 默认0 未定义")
    remark = Column(db.String(200),comment='描述') 
    phone = Column(db.String(50),comment='电话') 
    user_id =  Column(db.String(50),comment='')
    
    @classmethod
    def insert_data(cls,form):
        status = True if form.get("status") else False
        sex = True if form.get("sex") else False
        cls.create(
            name = form.get("name"),
            number_id = form.get("number_id"),
            sex =  sex,
            status =  status,
            phone =  form.get("phone")
        )


class Teacher(SurrogatePK,Model):
    """教师"""
    
    __tablename__ = "teacher"
    
    name = Column(db.String(50),comment='姓名')
    number_id = Column(db.String(50),comment='员工编号')
    sex = Column(db.Integer(),default=0,comment="性别0女1男")
    status = Column(db.Integer(),default=0,comment="状态 默认0 未定义")
    remark = Column(db.String(200),comment='描述') 
    phone = Column(db.String(50),comment='手机号') 
    user_id =  Column(db.String(50),comment='')
    
    @classmethod
    def insert_data(cls,form):
        status = 1 if form.get("status") else 0
        sex = 1 if form.get("sex") else 0
        cls.create(
            name = form.get("name"),
            number_id = form.get("number_id"),
            sex =  sex,
            remark =  form.get("remark"),
            phone =  form.get("phone"),
            status = status
        )


class Student(SurrogatePK,Model):
    """学生"""
    
    __tablename__ = "student"
    
    name = Column(db.String(50),comment='姓名')
    number_id = Column(db.String(50),comment='员工编号')
    sex = Column(db.Integer(),default=0,comment="性别0女1男")
    status = Column(db.Integer(),default=0,comment="状态 默认0 未定义")
    remark = Column(db.String(200),comment='描述') 
    user_id =  Column(db.String(50),comment='')
    grade_id =  Column(db.String(50),comment='')
    
    @classmethod
    def insert_data(cls,form):
        # 这里需要先添加user  获得user_id
        status = True if form.get("status") else False
        cls.create(
            name = form.get("name"),
            number_id =  form.get("number_id"),
            sex =  form.get("sex"),
            status =  form.get("status"),
            remark =  form.get("remark"),
            grade_id =  form.get("grade_id"),
            user_id =  form.get("user_id")
        )


class StudentParent(SurrogatePK,Model):
    """学生家长"""
    
    __tablename__ = "student_parent"
    
    name = Column(db.String(50),comment='姓名')
    sex = Column(db.Integer(),default=0,comment="性别0女1男")
    status = Column(db.Integer(),default=0,comment="状态 默认0 未定义")
    remark = Column(db.String(200),comment='描述') 
    phone = Column(db.String(50),comment='手机') 
    user_id =  Column(db.String(50),comment='')
    parent_type = Column(db.String(50),comment='家长类型 父母 爷爷奶奶等')
    
    @classmethod
    def insert_data(cls,form):
        status = True if form.get("status") else False
        cls.create(
            name = form.get("name"),
            sex =  form.get("sex"),
            status =  form.get("status"),
            remark =  form.get("remark"),
            phone =  form.get("phone"),
            parent_type =  form.get("parent_type"),
            user_id =  form.get("user_id")
        )


class StudentParentMap(SurrogatePK,Model):
    
    __tablename__ = "student_parent_map"
    
    parent_id = Column(db.Integer(),comment='家长ID')
    student_id = Column(db.Integer(),comment='学生ID')
    
    @classmethod
    def insert_data(cls,form):
        parent_id = form.get("parent_id")
        student_id = form.get("student_id")
        
        result = cls.query.filter_by(parent_id=parent_id,student_id=student_id).first()
        if not result:
            cls.create(
                parent_id = parent_id,
                student_id = student_id,
            )
 
