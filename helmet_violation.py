import functools
import os
from flask import *
from werkzeug.utils import secure_filename
from src.dbconnection import *

app = Flask(__name__)
app.secret_key="1234"

def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "lid" not in session:
            return render_template('login_index.html')
        return func()
    return secure_function

@app.route('/')
def log():
    return render_template('login_index.html')

@app.route('/logincode',methods=['post'])
def logincode():
    un=request.form['textfield']
    ps=request.form['textfield2']
    a="SELECT * FROM `login` WHERE `username`=%s AND `password`=%s"
    val=(un,ps)
    s=selectone(a,val)
    print(s)
    if s is None:
        return '''<script>alert("invalid username or password");window.location='/'</script>'''
    elif s['type']=="principal":
        session['lid']=s['login_id']
        return '''<script>alert("Welcome Principal");window.location='/admin_home'</script>'''
    elif s['type'] == "staff":
        session['lid'] = s['login_id']
        return '''<script>alert("Welcome Staff");window.location='/staff_home'</script>'''
    else:
        return '''<script>alert("invalid!!!!");window.location='/'</script>'''

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')

#==================================================ADMIN================================================================
@app.route('/admin_home')
@login_required
def admin_home():
    return render_template('admin/admin_index.html')

@app.route('/view_course')
@login_required
def view_course():
    q="select * from course"
    res=selectall(q)
    return render_template('admin/view_course.html',data=res)

@app.route('/add_course')
@login_required
def add_course():
    return render_template('admin/add_course.html')

@app.route('/add_course_post', methods=['POST'])
@login_required
def add_course_post():
    course=request.form['textfield']
    q="INSERT INTO `course` VALUES (NULL,%s)"
    iud(q,course)
    return '''<script>alert("Add successfully");window.location='/view_course#about'</script>'''

@app.route('/delete_course')
@login_required
def delete_course():
    cid=request.args.get('id')
    q="DELETE FROM `course` WHERE `cid`=%s"
    iud(q,cid)
    return '''<script>alert("Deleted successfully");window.location='/view_course#about'</script>'''

@app.route('/view_staff')
@login_required
def view_staff():
    q="select * from staff"
    res=selectall(q)
    return render_template('admin/view_staff.html',data=res)

@app.route('/add_staff')
@login_required
def add_staff():
    return render_template('admin/add_staff.html')

@app.route('/add_staff_post', methods=['POST'])
@login_required
def add_staff_post():
    name=request.form['textfield']
    place=request.form['textfield2']
    phone=request.form['textfield3']
    email=request.form['textfield4']
    uname=request.form['textfield5']
    psw=request.form['textfield6']
    q="INSERT INTO `login` VALUES (NULL,%s,%s,'staff')"
    val=(uname,psw)
    res=iud(q,val)

    qry="INSERT INTO `staff` VALUES (NULL,%s,%s,%s,%s,%s)"
    val1=(str(res),name,place,phone,email)
    iud(qry,val1)
    return '''<script>alert("Added successfully");window.location='/view_staff#about'</script>'''

@app.route('/edit_staff')
@login_required
def edit_staff():
    id=request.args.get('id')
    session['sid']=id
    q="select * from staff where staff_lid=%s"
    res=selectone(q,id)
    print(res)
    return render_template('admin/edit_staff.html',data=res)

@app.route('/edit_staff_post', methods=['POST'])
@login_required
def edit_staff_post():
    name=request.form['textfield']
    place=request.form['textfield2']
    phone=request.form['textfield3']
    email=request.form['textfield4']
    q="UPDATE `staff` SET `name`=%s,`place`=%s,`phone`=%s,`email`=%s WHERE `staff_lid`=%s"
    val=(name,place,phone,email,str(session['sid']))
    res=iud(q,val)
    return '''<script>alert("Updated  successfully");window.location='/view_staff#about'</script>'''

@app.route('/delete_staff')
@login_required
def delete_staff():
    cid=request.args.get('id')
    q="DELETE FROM `staff` WHERE `staff_lid`=%s"
    iud(q,cid)
    qry="delete from login where login_id=%s"
    iud(qry,cid)
    return '''<script>alert("Deleted successfully");window.location='/view_staff#about'</script>'''

@app.route('/view_student')
@login_required
def view_student():
    q="SELECT `student`.*,`course`.* FROM `student` JOIN `course` ON `student`.`course_id`=`course`.`cid`"
    res=selectall(q)
    return render_template('admin/view_student.html',data=res)

@app.route('/add_student')
@login_required
def add_student():
    q="select * from course"
    res=selectall(q)
    return render_template('admin/add_student.html',data=res)

@app.route('/add_stud_post', methods=['POST'])
@login_required
def add_stud_post():
    name=request.form['textfield']
    gender=request.form['radiobutton']
    place=request.form['textfield2']
    post=request.form['textfield22']
    phone=request.form['textfield3']
    email=request.form['textfield4']
    course=request.form['select2']
    uname=request.form['textfield5']
    psw=request.form['textfield6']

    q="INSERT INTO `login` VALUES (NULL,%s,%s,'student')"
    val=(uname,psw)
    res=iud(q,val)

    qry="INSERT INTO `student` VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)"
    val1=(str(res),course,name,gender,place,post,phone,email)
    iud(qry,val1)
    return '''<script>alert("Added successfully");window.location='/view_student#about'</script>'''

@app.route('/edit_student')
@login_required
def edit_student():
    id=request.args.get('id')
    session['stud_id']=id
    qry="SELECT * FROM `student` WHERE `lid`=%s"
    res1=selectone(qry,id)
    q="select * from course"
    res=selectall(q)
    return render_template('admin/edit_student.html',data=res,stud=res1)

@app.route('/view_sub')
@login_required
def view_sub():
    q="SELECT `subject`.*,`course`.* FROM `course` JOIN `subject` ON `course`.`cid`=`subject`.`courde_id`"
    res=selectall(q)
    return render_template('admin/view_sub.html',data=res)

@app.route('/add_sub')
@login_required
def add_sub():
    q="select * from course"
    res=selectall(q)
    return render_template('admin/add_sub.html',data=res)

@app.route('/add_sub_post', methods=['POST'])
@login_required
def add_sub_post():
    course=request.form['select']
    sub=request.form['textfield2']
    sem=request.form['select2']
    q="INSERT INTO `subject` VALUES (NULL,%s,%s,%s)"
    val=(course,sub,sem)
    iud(q,val)
    return '''<script>alert("Add successfully");window.location='/view_sub#about'</script>'''

@app.route('/edit_sub')
@login_required
def edit_sub():
    id=request.args.get('id')
    session['subid']=id
    qry="SELECT * FROM `subject` WHERE `sub_id`=%s"
    res1=selectone(qry,id)
    q="select * from course"
    res=selectall(q)
    return render_template('admin/edit_sub.html',data=res,val=res1)

@app.route('/edit_sub_post', methods=['POST'])
@login_required
def edit_sub_post():
    print(request.form)
    course=request.form['select']
    sub=request.form['textfield2']
    sem=request.form['select2']
    q="UPDATE `subject` SET `courde_id`=%s,`subject`=%s,`semester`=%s WHERE `sub_id`=%s"
    val=(course,sub,sem,session['subid'])
    iud(q,val)
    return '''<script>alert("Updated successfully");window.location='/view_sub#about'</script>'''

@app.route('/delete_sub')
@login_required
def delete_sub():
    cid=request.args.get('id')
    q="DELETE FROM `subject` WHERE `sub_id`=%s"
    iud(q,cid)
    return '''<script>alert("Deleted successfully");window.location='/view_sub#about'</script>'''




@app.route('/view_camera')
@login_required
def view_camera():
    q="select * from camera"
    res=selectall(q)
    return render_template('admin/viewcamera.html',data=res)



@app.route('/add_camera')
@login_required
def add_camera():
    return render_template('admin/add_camera.html')

@app.route('/add_camera_post', methods=['POST'])
@login_required
def add_camera_post():
    cam=request.form['textfield2']
    model=request.form['textfield3']
    loc=request.form['textfield4']

    q="INSERT INTO `camera` VALUES (NULL,%s,%s,%s)"
    val=(cam,model,loc)
    iud(q,val)
    return '''<script>alert("Add successfully");window.location='/view_camera#about'</script>'''

@app.route('/delete_camera')
@login_required
def delete_camera():
    cid=request.args.get('id')
    q="DELETE FROM `camera` WHERE `cid`=%s"
    iud(q,cid)
    return '''<script>alert("Deleted successfully");window.location='/view_camera#about'</script>'''


#=====================================================STAFF=============================================================

@app.route('/view_sub1')
@login_required
def view_sub1():
    q="SELECT `subject`.*,`course`.* FROM `course` JOIN `subject` ON `course`.`cid`=`subject`.`courde_id`"
    res=selectall(q)
    return render_template('staff/view_sub.html',data=res)


@app.route('/staff_home')
@login_required
def staff_home():
    return render_template('staff/staff_index.html')



@app.route('/view_student1')
@login_required
def view_student1():
    q="SELECT `student`.*,`course`.* FROM `student` JOIN `course` ON `student`.`course_id`=`course`.`cid`"
    res=selectall(q)
    return render_template('staff/view_student.html',data=res)

@app.route('/add_student1')
@login_required
def add_student1():
    q="select * from course"
    res=selectall(q)
    return render_template('staff/add_student.html',data=res)

@app.route('/add_stud_post1', methods=['POST'])
@login_required
def add_stud_post1():
    name=request.form['textfield']
    gender=request.form['radiobutton']
    place=request.form['textfield2']
    post=request.form['textfield22']
    phone=request.form['textfield3']
    email=request.form['textfield4']
    course=request.form['select2']
    uname=request.form['textfield5']
    psw=request.form['textfield6']

    q="INSERT INTO `login` VALUES (NULL,%s,%s,'student')"
    val=(uname,psw)
    res=iud(q,val)

    qry="INSERT INTO `student` VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)"
    val1=(str(res),course,name,gender,place,post,phone,email)
    iud(qry,val1)
    return '''<script>alert("Added successfully");window.location='/view_student1#about'</script>'''

@app.route('/edit_student1')
@login_required
def edit_student1():
    id=request.args.get('id')
    session['stud_id']=id
    qry="SELECT * FROM `student` WHERE `lid`=%s"
    res1=selectone(qry,id)
    q="select * from course"
    res=selectall(q)
    return render_template('staff/edit_student.html',data=res,stud=res1)

@app.route('/edit_stud_post1', methods=['POST'])
@login_required
def edit_stud_post1():
    name=request.form['textfield']
    gender=request.form['radiobutton']
    place=request.form['textfield2']
    post=request.form['textfield22']
    phone=request.form['textfield3']
    email=request.form['textfield4']
    course=request.form['select2']
    qry="UPDATE `student` SET `course_id`=%s,`name`=%s,`gender`=%s,`place`=%s,`post`=%s,`phone`=%s,`email`=%s WHERE `lid`=%s"
    val1=(course,name,gender,place,post,phone,email,session['stud_id'])
    iud(qry,val1)
    return '''<script>alert("Updated successfully");window.location='/view_student1#about'</script>'''

@app.route('/delete_student1')
@login_required
def delete_student1():
    id=request.args.get('id')
    q="DELETE FROM `student` WHERE `lid`=%s"
    iud(q,id)
    qry="delete from login where login_id=%s"
    iud(qry,id)
    return '''<script>alert("Deleted successfully");window.location='/view_student#about'</script>'''



app.run(debug=True)
