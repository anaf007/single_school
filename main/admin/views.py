"""
admin_bp 管理员 views 
"""

from flask import render_template,request,flash
from flask_login import login_required
from sqlalchemy import desc

from main.models.auth.menu import Menu
from main.models.auth.menu import Access
from main.models.auth.users import User
from main.models.auth.roles import Role
from main.models.auth.roles import RoleAccess

from . import admin_bp

@admin_bp.route("/menu",methods=["GET","POST"])
@login_required
def menu():
    if request.method=="GET":
        result = Menu.query.order_by("id").all()
        return render_template("admin/menu.html",menu=result)
    
    try:
        Menu.insert_data(request.form)
    except Exception as e:
        flash("添加失败："+str(e))
    return '<a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;">添加成功，请点击右上角关闭</a>'


@admin_bp.route("/add_menu")
@login_required
def add_menu():
    return render_template("admin/add_menu.html")


@admin_bp.route("/access")
@login_required
def access():
    result = Access.query.order_by("id").all()
    return render_template("admin/access.html",access=result)
    

@admin_bp.route("/access_handle",methods=["GET","POST"])
@login_required
def access_handle():
    if request.method=="GET":
        return render_template("admin/access_handle.html")
    try:
        Access.insert_data(request.form)
    except Exception as e:
        flash("添加失败："+str(e))
    return '<a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;">添加成功，请点击右上角关闭</a>'


@admin_bp.route("/role")
@login_required
def role():
    result = Role.query.order_by(desc(Role.id)).all()
    return render_template("admin/role.html",role=result)
   

@admin_bp.route("/user")
@login_required
def user():
    page = request.args.get("page",'1')
    per_page = request.args.get("per_page",'20')
    paginate = User.query.order_by(desc(User.id)).paginate(int(page), int(per_page))
    return render_template("admin/user.html",user=paginate.items,paginate=paginate,page=int(page))    
    

@admin_bp.route("/role_handle",methods=["GET","POST"])
@login_required
def role_handle():
    if request.method=="GET":
        return render_template("admin/role_handle.html")
    try:
        Role.insert_data(request.form)
    except Exception as e:
        flash("添加失败："+str(e))
    return '<a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;">添加成功，请点击右上角关闭</a>'


@admin_bp.route("/role_join_access",methods=["GET","POST"])
@login_required
def role_join_access():
    if request.method=="GET":
        role_id = request.args.get('role_id')
        all_access_data = RoleAccess.all_access_data(role_id)
        return render_template("admin/role_join_access.html",access=all_access_data,role_id=role_id)
    try:
        RoleAccess.insert_data(request.form)
    except Exception as e:
        flash("添加失败："+str(e))
    return '<a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;">添加成功，请点击右上角关闭</a>'




    

