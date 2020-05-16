from flask import render_template,request,flash,jsonify,current_app,redirect,url_for
from flask_login import current_user,login_required
from sqlalchemy import desc
from werkzeug.utils import secure_filename


from main.models.auth.users import Teacher
from main.models.auth.users import Staff
from main.models.auth.users import StudentParent
from main.models.auth.users import Student
from main.models.auth.users import User
from main.models.school.grade import Grade
from main.models.base.access_records import AccessRecords
from main.models.base.car import Car
from main.models.school.ask_leave import AskApproved
from main.models.school.ask_leave import AskLeave

from main.utils import create_file_name,allowed_file,allowed_img_lambda,gen_rnd_filename

from main.extensions import csrf_protect

from . import bp

import os,xlrd,random
import datetime as dt

@bp.route("/student")
def student():
    if request.method == "GET":
        return render_template("/school/student.html")
    try:
        Student.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
    return render_template("/school/student.html")


@bp.route("/stud_parents")
def stud_parents():
    if request.method == "GET":
        return render_template("/school/stud_parents.html")
    try:
        StudentParent.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
    return render_template("/school/stud_parents.html")


@bp.route("/teacher",methods=["POST","GET"])
def teacher():
    if request.method == "GET":
        result = Teacher.query.order_by(desc(Teacher.id)).all()
        return render_template("/school/teacher.html",result=result)
    try:
        Teacher.insert_data(request.form)
        return '<a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;">添加成功，请点击右上角关闭</a>'
    except Exception as e:
        flash("添加失败："+str(e))
    return render_template("/school/teacher.html")


@bp.route("/staff",methods=["POST","GET"])
def staff():
    if request.method == "GET":
        result = Staff.query.order_by(desc(Staff.id)).all()
        return render_template("/school/staff.html",result=result)
    try:
        Staff.insert_data(request.form)
        flash("添加完成")
        return '<a class="layui-layer-ico layui-layer-close layui-layer-close1" href="javascript:;">添加成功，请点击右上角关闭</a>'
    except Exception as e:
        flash("添加失败："+str(e))
    


@bp.route("/outsiders")
def outsiders():
    return render_template("/school/outsiders.html")



@bp.route("/student_parent_map")
def student_parent_map():
    return render_template("/school/student_parent_map.html")


@bp.route("/grade",methods=["POST","GET"])
def grade():
    if request.method == "GET":
        result = Grade.query.order_by(desc('sort')).all()
        return render_template("/school/grade.html",result=result)
    try:
        Grade.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
    return render_template("/school/grade.html")

@bp.route("/add_grade")
def add_grade():
    return render_template("/school/add_grade.html")


@bp.route("/car",methods=["POST","GET"])
def car():
    if request.method == "GET":
        return render_template("/school/car.html")
    try:
        Car.insert_data(request.form)
        flash("添加完成")
    except Exception as e:
        flash("添加失败："+str(e))
    return render_template("/school/car.html")

@csrf_protect.exempt
@bp.route("/access_records",methods=["POST","GET"])
def access_records():
    """出入记录  如果是学生  需要查询是否有请假的"""
    if request.method == "GET":
        return render_template("/school/access_records.html")
    try:
        msg = AccessRecords.insert_data(request.args.get('s'))
        return jsonify(msg)
    except Exception as e:
        return jsonify({"msg":"扫描失败："+str(e),"code":-1})
    


@bp.route("/ask_leave",methods=["POST","GET"])
def ask_leave():
    if request.method == "GET":
        return render_template("/school/ask_leave.html")
    try:
        AskLeave.insert_data(request.form)
    except Exception as e:
        flash("添加失败："+str(e))
    return render_template("public/main.html")


@csrf_protect.exempt
@bp.route("/update_ask_leave",methods=["POST","GET"])
def update_ask_leave():
    if request.method == "GET":
        ask = AskApproved.get_by_list()
        return render_template("/school/update_ask_leave.html",ask=ask)
    try:
        result = AskApproved.update_data(request.args)
        if not result:
            msg = "更新失败"
        else:
            msg = "更新完成"
    except Exception as e:
        msg = "更改失败："+str(e)
    return jsonify({"msg":msg})


@bp.route("/show_student")
def show_student():
    grade_id = request.args.get("grade_id")
    result = Student.query\
            .with_entities(Student,User)\
            .join(User,User.id==Student.user_id)\
            .filter(Student.grade_id==grade_id).all()
    return render_template('school/show_student.html',result=result,grade_id=grade_id)


@bp.route("/add_student",methods=["POST","GET"])
def add_student():
    if request.method=="GET":
        grade_id = request.args.get("grade_id")
        result = Student.query.filter_by(grade_id=grade_id).all()
        return render_template('school/show_student.html',result=result)
    
    files = request.files['file']
    grade_id = request.form.get('grade_id','0')
    if not files:
        flash(u'请选择文件')
        return redirect(url_for('.add_student',grade_id=grade_id))
    # grade = Grade.query.get_or_404(grade_id)

    try:
        filename = secure_filename(files.filename)
        filename = create_file_name(files)
        dataetime = dt.datetime.today().strftime('%Y%m%d')
        file_dir = 'admin/excel/%s/'%dataetime
        if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
        	os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)
        if  allowed_file(files.filename):
        	files.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)
              

        filedata = xlrd.open_workbook(current_app.config['UPLOADED_PATH'] +file_dir+filename)
        table = filedata.sheets()[0]

        message = ""
        try:
            if table.col(0)[0].value.strip() != u'学号':
                message = "第一行名称必须叫‘学号’，请返回修改"
            
            if table.col(1)[0].value.strip() != u'姓名':
                message = "第二行名称必须叫‘姓名’，请返回修改"
                
            if table.col(2)[0].value.strip() != u'性别':
                message = "第三行名称必须叫‘性别’，请返回修改"
                
            if message != "":
                flash(message)
                return redirect(url_for('school.show_student',grade_id=grade_id))
            
        	
        except Exception as e:
        	flash(u'excel文件操作错误：%s'%str(e))
        	return redirect(url_for('school.show_student',grade_id=grade_id))
        
        nrows = table.nrows #行数
        table_data_list =[]
        for rownum in range(1,nrows):
            if table.row_values(rownum):
                table_data_list.append(table.row_values(rownum))
                
        
        # grade = Grade.query.get_or_404(grade_id)
        if table_data_list:
            for i in table_data_list:
                sex = (True if i[2]=='男' else False)
                user = User.create(
                    username = "STD"+str(random.randint(10000,99999)),
                    password = str(random.randint(100000,999999)),
                    name = i[1],
                    q_number = i[0],
                    sex = sex
                )

                Student.create(
                    name = i[1],
                    number_id = i[0],
                    user_id = user.id,
                    grade_id = grade_id,
                    sex = sex
                )
        
        flash(u'添加完成')
        return redirect(url_for('school.show_student',grade_id=grade_id))
    
    except Exception as e:
        flash(u'文件提交读取错误11：%s'%str(e))
        return redirect(url_for('school.show_student',grade_id=grade_id))
	
  
@csrf_protect.exempt	   
@bp.route("/submit_students_img",methods=["POST","GET"])     
@login_required
def submit_students_img():
    f = request.files.get('file')
    filename = allowed_img_lambda(f.filename)
    filename = gen_rnd_filename()+'.'+f.filename.rsplit('.', 1)[1]

    dataetime = dt.datetime.today().strftime('%Y%m%d')
    file_dir = '%s/%s/'%('0',dataetime)
    
    if not os.path.isdir(current_app.config['STUDENTS_IMG']+file_dir):
        os.makedirs(current_app.config['STUDENTS_IMG']+file_dir)
    
    f.save(current_app.config['STUDENTS_IMG'] +file_dir+filename)
    filename = file_dir+filename

    student = Student.query.get(request.form.get('id'))
    if student:
        user = User.query.get(student.user_id)
        user.update(avatar=filename)
    return jsonify({'success':[filename,request.form.get('id')]})
    
    
@bp.route("/teacher_handle")
@login_required
def teacher_handle():
    return render_template("school/teacher_handle.html")
    

@bp.route("/staff_handle")  
@login_required  
def staff_handle():
    return render_template("school/staff_handle.html")