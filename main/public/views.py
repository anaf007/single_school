# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import json
import qrcode,os
import requests
import random

from PIL import Image

from io import StringIO,BytesIO

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    session
)
from flask import make_response,send_from_directory,current_app
from flask_login import login_required, login_user, logout_user

from main.extensions import login_manager,cache
from main.models.auth.users import User
from main.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET"])
@login_required
def home():
    return render_template("public/home.html")

@blueprint.route("/main")
@login_required
def main():
    return render_template("public/main.html")


@blueprint.route("/menu")
@login_required
def menu():
    
    if "menu" in session:
        return jsonify(session["menu"])
    
    access_url = User.get_access_url()
    user_menu = User.get_menu(access_url)
    menu_data = []
    for x in user_menu:
        menu_data.append({'id':x.id,"name":x.title,"icon":x.icon,"url":x.url,"children":[]})
    
    session['menu'] = {
		"status": 0,
		"msg": "ok",
		"data": menu_data
	}
    return jsonify(session['menu'])


@blueprint.route("/get_rq")
def get_rq():
    rq_str = request.args.get("rq_str")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(f'{rq_str}')
    qr.make(fit=True)
    img = qr.make_image()
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    response = make_response(img_io.read())
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Description'] = 'attachment; filename=%s.png' % rq_str
    return response


#获取学生头像
@blueprint.route('/get_student_img')
@blueprint.route('/get_student_img/<path:student_img>')
def get_student_img(student_img='0'):
    path = os.getcwd()+'/'+current_app.config['STUDENTS_IMG']
    return send_from_directory(path, student_img)


# 短信验证码
@blueprint.route("/sms_code")
def sms_code():
    mobile:str = request.args.get("mobile",'0')
    code = random.randint(1000,9999)
    cache.set("sms_code_"+mobile,code,timeout=30)
    sms_code_url:str = current_app.config['SMS_CODE_URL']
    tpl_id:str = current_app.config['SMS_CODE_TPLID']
    data = {
        "mobile":mobile,
        "tpl_id":int(tpl_id),
        "tpl_value":"#code#="+str(code),
        "key":current_app.config['SMS_KEY']
    }
    if User.query.filter_by(phone=mobile).first():
        return jsonify({"msg":"该手机号已被注册"})
    send_result = requests.get(sms_code_url,data)
    return jsonify({"msg":"验证码已发送，有效期为10分钟。"+str(code)})


@blueprint.route("/verify_sms_code")
def verify_sms_code():  
    mobile:str = request.args.get("mobile",'0')
    code = cache.get("sms_code_"+mobile)  
    print(code)
    return str(code)
