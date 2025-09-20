from email import message
from posixpath import splitext
from flask import Flask, render_template, request, flash, url_for, redirect, session
from PIL import Image
import cv2
from psutil import AccessDenied
from datetime import timedelta, date
import pytesseract
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import datetime
import re
import os
from os.path import join, dirname, realpath
import Calcuate_Nutrient
import Compare_Nutrient
import hashlib
import get_flabel



pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

db = SQLAlchemy()
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), UPLOAD_FOLDER)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1) 
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/fyp"
db.init_app(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hasNumber(stringVal):
    return any(elem.isdigit() for elem in stringVal)

def getInt(word):
    int = ""
    char = ["0","1","2","3","4","5","6","7","8","9",]
    for k in word:
        if (k in char):
            int=int+k
    return int

def remove(word):
    words = ""
    char = ["0","1","2","3","4","5","6","7","8","9","."]
    for k in word:
        if (k in char):
            words=words+k
        else:
            break
    return words

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def imageToString(image):
    text = pytesseract.image_to_string(image, lang="chi_tra+eng")
    splitedtext = text.split("\n")
    a = []
    for i in splitedtext:
        for j in range(len(i)):
            if (i[j].encode('UTF-8').isalpha()):
                if (hasNumber(i[j:])):
                    a.append(i[j:])
                break
    return a


def prepareData(data):
    ar = []
    for i in data:
        c = []
        for j in range(len(i)):
            if (i[j].isdigit()):
                c.append(i[:j])
                c.append(i[j:])
                ar.append(c)
                break
    return ar

def getIID():
    sql =text("SELECT * FROM image")
    results = db.session.execute(sql).fetchall()
    if((len(results)-1) == -1):
        IID = "I1"
    else:   
        num = getInt(results[len(results)-1][0])
        n = 3
        while(n>0):
            num = int(num)+1
            IID = "I"+str(num)
            sql =text("SELECT * FROM image WHERE IID='{}'".format(IID))
            result = db.session.execute(sql).fetchall()
            n = len(result)
    return IID

def getFLID():
    sql =text("SELECT * FROM food_label")
    results = db.session.execute(sql).fetchall()
    if((len(results)-1) == -1):
        FLID = "F1"
    else:
        num = getInt(results[len(results)-1][0])
        n = 3
        while(n>0):
            num = int(num)+1
            FLID = "F"+str(num)
            sql =text("SELECT * FROM food_label WHERE FLID='{}'".format(FLID))
            result = db.session.execute(sql).fetchall()
            n = len(result)
    return FLID

def getplaceID():
    sql =text("SELECT * FROM buying_place")
    results = db.session.execute(sql).fetchall()
    if((len(results)-1) == -1):
        PID = "P1"
    else:
        num = getInt(results[len(results)-1][0])
        PID = "P"+str(int(num)+1)
    return PID

def getfoodID():
    sql =text("SELECT * FROM food")
    results = db.session.execute(sql).fetchall()
    if((len(results)-1) == -1):
        FID = "F1"
    else:
        num = getInt(results[len(results)-1][0])
        n = 3
        while(n>0):
            num = int(num)+1
            FID = "F"+str(num)
            sql =text("SELECT * FROM food WHERE FID='{}'".format(FID))
            result = db.session.execute(sql).fetchall()
            n = len(result)
    return FID

#upload the scan image to database
def InsertImage(empPicture,filename,ID,IID):
    if(ID == ""):
        accID = session.get('userID')
    else:
        accID = ID
    date = datetime.date.today()
    sql =text("INSERT INTO image (IID, ImageName, ID, file, upload_date) VALUE (%s, %s, %s, %s, %s)")
    results = db.session.execute(sql,(IID,filename,accID,empPicture,date))

def InsertLabelData(energy,tfat,protein,sodium,carbohydrates,IID):
    FLID = getFLID()
    sql =text("INSERT INTO food_label VALUE('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(FLID,IID,energy,tfat,sodium,carbohydrates,protein))
    db.session.execute(sql)
    
def getSPID():
    sql =text("SELECT * FROM scanningProblem")
    results = db.session.execute(sql).fetchall()
    if((len(results)-1) == -1):
        SPID = "SP1"
    else:
        num = getInt(results[len(results)-1][0])
        n = 3
        while(n>0):
            num = int(num)+1
            SPID = "SP"+str(num)
            sql =text("SELECT * FROM scanningProblem WHERE SPID='{}'".format(SPID))
            result = db.session.execute(sql).fetchall()
            n = len(result)
    return SPID
    
def getSDID():
    sql =text("SELECT * FROM ProblemData")
    results = db.session.execute(sql).fetchall()
    if((len(results)-1) == -1):
        SDID = "SD1"
    else:
        num = getInt(results[len(results)-1][0])
        n = 3
        while(n>0):
            num = int(num)+1
            SDID = "SD"+str(num)
            sql =text("SELECT * FROM scanningProblem WHERE SPID='{}'".format(SDID))
            result = db.session.execute(sql).fetchall()
            n = len(result)
    return SDID
    
def InsertProblemData(image, imageName,date):
    SDID = getSDID()
    sql = text("INSERT INTO problemdata VALUE (%s, %s, %s, %s)")
    db.session.execute(sql,(SDID,imageName,image,date))
    
def InsertProblemInfo(ID, problem, scan,status):
    SPID =getSPID()
    sql =text("SELECT SDID FROM ProblemData")
    results = db.session.execute(sql).fetchall()
    SDID = results[len(results)-1][0]
    sql =text("INSERT INTO scanningProblem (SPID,SDID,Problem,ID,Rescan,Status) VALUE (%s,%s,%s, %s,%s,%s)")
   db.session.execute(sql,(SPID,SDID,problem,ID,scan,status))

@app.route('/')
def home():
    return render_template("index_page.html")

@app.route('/scan')
def scan():
    return render_template("scan.html")

@app.route('/scan', methods=['POST'])
def upload_image():
    file = request.files['image']
    label = []
    value = []
    energy = 0
    tfat = 0
    protein = 0
    sodium = 0
    carbohydrates = 0
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = cv2.imread(r"C:\\Users\\User\\Downloads\\New_fyp\\New_fyp\\static\\uploads\\" + filename)
        text = imageToString(image)
        data = prepareData(text)
        for i in range(len(data)):
            label.append(data[i][0])
            value.append(data[i][1])
        for i in range(len(label)):
            label[i] = re.sub("([^\x00-\x7F])+", " ", label[i])
            label[i] = label[i].replace("/", "")
            label[i] = label[i].replace(" ", "")
        for i in range(len(value)):
            value[i] = value[i].replace(" ", "")
        for i in range(len(label)):
            if ("Energy" in label[i]) or ("Calories" in label[i]):
                energy = remove(value[i])
            if ("Protein" in label[i]) or ("protein" in label[i]):
                protein = remove(value[i])
            if ("Totalft" in label[i]) or ("TotalFat" in label[i]) or ("Totalfat" in label[i]):
                tfat= remove(value[i])
            if ("OtalCarbohydrates" in label[i]) or ("Carbohydrate" in label[i]) or ("TotalCarbohydrates" in label[i]):
                carbohydrates =remove(value[i])
            if ("Sodium" in label[i]) or ("sodium" in label[i]):
                sodium = remove(value[i])
        return render_template("after.html", energy=str(energy)+"kcal", protein=str(protein)+"g",totalfat=str(tfat)+"g", totalcarbohydrates=str(carbohydrates)+"g", sodium=str(sodium)+"mg")
    else:
        flash('Please import the image.')
        return render_template("scan.html")

@app.route('/premium_scan')
def premium_scan():
    return render_template("premium_scan.html")

@app.route('/premium_scan', methods=['POST'])
def upload_image_premium():
    file = request.files['image']
    label = []
    value = []
    energy = 0
    tfat = 0
    protein = 0
    sodium = 0
    carbohydrates = 0
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = cv2.imread("C:\\Users\\User\\Documents\\USB\\FYP_py_db\\fyp_python_v1\\New_fyp\\static\\uploads\\"+filename)
        photo = "C:\\Users\\User\\Documents\\USB\\FYP_py_db\\fyp_python_v1\\New_fyp\\static\\uploads\\"+filename
        empPicture = convertToBinaryData(photo)
        text = imageToString(image)
        data = prepareData(text)
        for i in range(len(data)):
            label.append(data[i][0])
            value.append(data[i][1])
        for i in range(len(label)):
            label[i] = re.sub("([^\x00-\x7F])+", " ", label[i])
            label[i] = label[i].replace("/", "")
            label[i] = label[i].replace(" ", "")
        for i in range(len(value)):
            value[i] = value[i].replace(" ", "")
        for i in range(len(label)):
            if ("Energy" in label[i]) or ("Calories" in label[i]):
                energy = remove(value[i])
            if ("Protein" in label[i]) or ("protein" in label[i]):
                protein = remove(value[i])
            if ("Totalft" in label[i]) or ("TotalFat" in label[i]) or ("Totalfat" in label[i]):
                tfat= remove(value[i])
            if ("OtalCarbohydrates" in label[i]) or ("Carbohydrate" in label[i]) or ("TotalCarbohydrates" in label[i]):
                carbohydrates =remove(value[i])
            if ("Sodium" in label[i]) or ("sodium" in label[i]):
                sodium = remove(value[i])
        IID=getIID()
        InsertImage(empPicture,filename,"",IID)
        InsertLabelData(energy,tfat,protein,sodium,carbohydrates,IID)
        return render_template("after_login.html", energy=str(energy)+"kcal", protein=str(protein)+"g",totalfat=str(tfat)+"g", totalcarbohydrates=str(carbohydrates)+"g", sodium=str(sodium)+"mg")
    else:
        flash('Please import the image.')
        return redirect(url_for('premium_scan'))

@app.route('/login')
def login():
    return render_template("Login(Ming).html")


@app.route('/login', methods=['POST'])
def check_login():
    userType = request.form['radio']
    login_id = request.form['userID']
    userPassword = request.form['userPassword']
    sql = text("SELECT * FROM account WHERE userType='{}' AND ID='{}' AND password='{}'".format(userType,login_id,userPassword))
    results = db.session.execute(sql)
    num_results = results.rowcount
    if (int(num_results) == 0):
        flash('User ID/Password incorrect or invaled usertype, please try again.')
        return redirect(url_for('login'))
    elif(num_results>0 and userType=="Admin"):
        session['userID'] = login_id
        session.permanent = True
        return redirect(url_for('AHP'))
    elif(num_results>0 and userType=="Merchant"):
        session['userID'] = login_id
        session.permanent = True
        return redirect(url_for('MHP'))
    else:
        session['userID'] = login_id
        session.permanent = True
        flash('Welcome Back, ' + session['userID'])
        return redirect(url_for('premium_scan'))

@app.route('/logout')
def logout():
    session['userID'] = False
    return redirect('/')

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def check_register():
    login_id = request.form['userID']
    userPassword = request.form['userPassword']
    date = datetime.date.today()
    sql = text("SELECT * FROM account WHERE ID = '{}'".format(login_id))
    results = db.session.execute(sql)
    num_results = results.rowcount
    if (int(num_results) == 0):
        sql = text("INSERT INTO account (ID, password, CreatedDate, userType) VALUE ('{}','{}','{}','{}')".format(
            login_id, userPassword, date, "User"))
        db.session.execute(sql)
        flash('Account Created Successfully')
        return redirect(url_for('register'))
    elif (int(num_results) > 0):
        flash('Your user ID already exists.')
        return redirect(url_for('register'))

@app.route('/edit')
def edit():
    data = []
    user_id = session.get('userID')
    sql = text("SELECT * FROM account WHERE ID = '{}'".format(user_id))
    data = db.session.execute(sql).fetchall()
    sql = text("SELECT CreatedDate FROM account WHERE ID = '{}'".format(user_id))
    fetchDate = db.session.execute(sql).fetchall()
    today = date.today()
    return render_template("editPersonal.html", data=data, age=fetchDate)

@app.route('/edit', methods=['POST'])
def update():
    user_id = session.get('userID')
    password = request.form['password']
    name = request.form['name']
    email = request.form['email']
    gender = request.form['gender']
    dob = request.form['dob']
    weight = request.form['weight']
    height = request.form['height']
    sql = text("UPDATE account SET password = '{}', name = '{}', email = '{}', Sex = '{}', DateOfBirth = '{}', Height = '{}', Weight = '{}' WHERE ID = '{}'".format(
        password, name, email, gender, dob, height,weight, user_id
    ))
    db.session.execute(sql)
    date1 = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
    today = date.today()
    n = today - date1
    age = int((n.days)/365)
    Calcuate_Nutrient.UploadDB(user_id,gender,weight,height,age);
    flash('Your Personal Information has been updated.')
    return redirect(url_for('edit'))

@app.route('/review')
def review():
    user_id = session.get('userID')
    sql = text("SELECT ImageName, Calories, Total_Fat, Sodium, Total_Carbohydrate, Protein FROM image, food_label WHERE image.ID = '{}' AND image.IID = food_label.IID".format(user_id))
    data = db.session.execute(sql).fetchall()
    return render_template("review.html", data=data)

@app.route('/image')
def showImg():
    return render_template("image.html")

@app.route('/AHP')
def AHP():
    return render_template("Admin_homepage.html")

@app.route('/MHP')
def MHP():
    return render_template("Merchant_homepage.html")

@app.route('/AMG_view')
def AMG_view():
    data=[]
    password = []
    sql="SELECT * FROM account WHERE NOT userType ='Admin';"
    data = db.engine.execute(sql).fetchall()
    for i in range(len(data)):
        password.append(hashlib.md5(data[i][1].encode()))
    return render_template("Admin_accountMG.html",data = data, password = password)

@app.route('/AMG_view',methods=['POST'])
def Admin_Update_user():
    data=[]
    account_id=request.form.get('user_id')
    sql="SELECT * FROM account WHERE ID ='{}'".format(account_id)
    data=db.engine.execute(sql)
    num_results = data.rowcount
    if (int(num_results) == 0):
        flash('User data not found.')
        return redirect(url_for('AMG_view'))
    elif(int(num_results) > 0): 
        data=db.engine.execute(sql).fetchall() 
        return render_template("Admin(edit).html",data=data)

@app.route('/Admin_Delete',methods=['POST'])
def Admin_Delete():
    user_id = request.form.get('user_id_2')
    sql = text("SELECT IID FROM image WHERE ID ='{}'".format(user_id))
    res = db.session.execute(sql).fetchall()
    for i in range(len(res)):
        iid = res[i].IID
        sql = text("DELETE FROM food_label WHERE IID = '{}'".format(iid))
        db.session.execute(sql)
    sql = text("DELETE FROM image WHERE ID ='{}'".format(user_id))
    db.session.execute(sql)
    sql = text("DELETE FROM nutrient_info WHERE ID ='{}'".format(user_id))
    db.session.execute(sql)
    sql = text("DELETE FROM exerciseamount WHERE ID = '{}'".format(user_id))
    db.session.execute(sql)
    sql = text("DELETE FROM account WHERE ID ='{}'".format(user_id))
    db.session.execute(sql)
    return redirect(url_for('AMG_view'))

@app.route('/User_delete',methods=['POST'])
def User_Delete():
    img = request.form.get('img')
    sql = text("SELECT IID FROM image WHERE ImageName = '{}'".format(img))
    res = db.session.execute(sql).fetchall()
    for i in range(len(res)):
        iid = res[i].IID
        sql = text("DELETE FROM food_label WHERE IID = '{}'".format(iid))
        db.session.execute(sql)
    sql = text("DELETE FROM image WHERE ID ='{}'".format(iid))
    db.session.execute(sql)
    return redirect(url_for('review'))

@app.route('/Admin_insert')
def Admin_Create():
    return render_template("Admin(Insert).html")

@app.route('/Admin_insert',methods=['POST'])
def Admin_Created():
    user_type = request.form['utype']
    userID = request.form['userID']
    userPassword = request.form['userPassword']
    uname = request.form['uname']
    uemail = request.form['uemail']
    date = datetime.date.today()
    sql = text("SELECT * FROM account WHERE ID = '{}'".format(userID))
    results = db.session.execute(sql)
    num_results = results.rowcount
    if (int(num_results) == 0):
        sql = text("INSERT INTO account (ID, password, CreatedDate, name, email, userType) VALUE ('{}','{}','{}','{}','{}','{}')".format(
            userID, userPassword, date, uname, uemail, user_type))
        db.session.execute(sql)
        flash('Account Created Successfully')
        return render_template("Admin(Insert).html")
    elif (int(num_results) > 0):
        flash('Your user ID already exists.')
        return render_template("Admin(Insert).html")
        
@app.route('/Admin_edit',methods=['POST'])
def Admin_update():
    user_id = request.form.get('userID')
    password = request.form.get('userPassword')
    name = request.form.get('uname')
    email = request.form.get('uemail')
    sql = text("UPDATE account SET password = '{}', name = '{}', email = '{}' WHERE ID = '{}'".format(
        password, name, email, user_id
    ))
    db.session.execute(sql)
    return redirect(url_for('AMG_view'))

@app.route('/exercise')
def exercise():
    return render_template("AmountOfExercise.html")

@app.route('/exercise',methods=['POST'])
def cal_exerciseAmount():
    exerciseType  = request.form['exercise']
    duration = request.form['duration']
    date = request.form['date']
    sql = text("SELECT Amount FROM exercise WHERE Exercise = '{}'".format(exerciseType))
    result  = db.session.execute(sql).fetchall()
    amount = int(duration)/60.0
    amount = result[0][0] * amount
    sql = "SELECT * FROM exerciseAmount"
    results = db.session.execute(sql).fetchall()
    if(len(results) == 0):
        EAID = "EA1"
    else:
        num = getInt(results[len(results)-1][0])
        n = 3
        while(n>0):
            num = int(num)+1
            EAID = "EA"+str(num)
            sql = text("SELECT * FROM exerciseAmount WHERE EAID = '{}'".format(EAID))
            result = db.session.execute(sql).fetchall()
            n = len(result)
    user_id = session.get('userID')
    sql = text("INSERT INTO exerciseAmount(EAID, ID, exercise, time, amount,date) VALUE ('{}','{}','{}','{}','{}','{}')".format(EAID, user_id, exerciseType, duration, amount,date))
    db.session.execute(sql)
    return render_template("SportAmount.html", date = date, type = exerciseType, time = duration, amount = amount)

@app.route('/DBList')
def show():
    sql = text("SELECT FLID, image.IID,image.ID,UpLoad_Date FROM food_label, image WHERE image.IID = food_label.IID")
    data = db.session.execute(sql).fetchall()
    return render_template("Admin_DBList.html", data= data)

@app.route('/record_Del', methods=['POST'])
def record_Del():
    FLID = request.form.get('FLID_2')
    sql = text("SELECT IID FROM food_label WHERE FLID = '{}'".format(FLID))
    IID = db.session.execute(sql).fetchall()
    sql = text("DELETE FROM food_label WHERE FLID ='{}' ".format(FLID))
    db.session.execute(sql)
    sql = text("DELETE FROM image WHERE IID ='{}' ".format(IID[0][0]))
    db.session.execute(sql)
    return redirect(url_for('show'))

@app.route('/ReScan')
def ReScan():
    return render_template("Admin_Scanner.html")

@app.route('/Up_Reocrds', methods=['POST'])
def upRecords():
    return render_template("Admin_Scanner.html")

@app.route('/AdminScanner', methods=['POST'])
def Scanner():
    file = request.files['image']
    ID = request.form['ID']
    SPID = request.form['SPID']
    StaffID =  session.get('userID')
    label = []
    value = []
    energy = 0
    tfat = 0
    protein = 0
    sodium = 0
    carbohydrates = 0
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = cv2.imread("C:\\Users\\User\\Documents\\USB\\FYP_py_db\\fyp_python_v1\\New_fyp\\static\\uploads\\"+filename)
        photo = "C:\\Users\\User\\Documents\\USB\\FYP_py_db\\fyp_python_v1\\New_fyp\\static\\uploads\\"+filename
        empPicture = convertToBinaryData(photo)
        text = imageToString(image)
        data = prepareData(text)
        for i in range(len(data)):
            label.append(data[i][0])
            value.append(data[i][1])
        for i in range(len(label)):
            label[i] = re.sub("([^\x00-\x7F])+", " ", label[i])
            label[i] = label[i].replace("/", "")
            label[i] = label[i].replace(" ", "")
        for i in range(len(value)):
            value[i] = value[i].replace(" ", "")
        for i in range(len(label)):
            if ("Energy" in label[i]) or ("Calories" in label[i]):
                energy = remove(value[i])
            if ("Protein" in label[i]) or ("protein" in label[i]):
                protein = remove(value[i])
            if ("Totalft" in label[i]) or ("TotalFat" in label[i]) or ("Totalfat" in label[i]):
                tfat= remove(value[i])
            if ("OtalCarbohydrates" in label[i]) or ("Carbohydrate" in label[i]) or ("TotalCarbohydrates" in label[i]):
                carbohydrates =remove(value[i])
            if ("Sodium" in label[i]) or ("sodium" in label[i]):
                sodium = remove(value[i])
        IID = getIID()
        exist = False
        sql = text("SELECT * FROM account WHERE ID = '{}'".format(ID))
        num = db.session.execute(sql).fetchall()
        if(len(num) == 0):
            exist = True
        else:
            sql = text("SELECT * FROM scanningProblem WHERE SPID = '{}'".format(SPID))
            num2 = db.session.execute(sql).fetchall()
            if(len(num2) == 0):
                exist = True
        if(exist):
            flash("The Problem ID or Account ID is incorrect!!")
            return render_template("Admin_Scanner.html")
        else:
            InsertImage(empPicture,filename,ID,IID)
            InsertLabelData(energy,tfat,protein,sodium,carbohydrates,IID)
            date = datetime.date.today()
            sql = text("UPDATE scanningproblem SET staffID = %s, EditDate = %s, Status='Solved' WHERE SPID = %s")
            db.session.execute(sql,(StaffID,date,SPID))
            return render_template("Admin_after.html", energy=str(energy)+"kcal", protein=str(protein)+"g",totalfat=str(tfat)+"g", totalcarbohydrates=str(carbohydrates)+"g", sodium=str(sodium)+"mg")
    else:
        flash('Please import the image.')
        return redirect(url_for('reScan'))
    
    
@app.route('/suggestion')
def showSuggestion():
    user_id = session.get('userID')
    str,gap =Compare_Nutrient.CompareNutrient(user_id)
    normal, require= Compare_Nutrient.getNurient()
    ndata =get_flabel.getdata(user_id)
    #get exc_amount
    data=[]
    
    sql="SELECT * FROM exerciseamount WHERE ID ='{}'".format(user_id)
    data=db.engine.execute(sql)
    num_results = data.rowcount
    if (int(num_results) == 0):
        flash('User data not found.')
        return redirect(url_for('Suggestion'))
    elif(int(num_results) > 0): 
        data=db.engine.execute(sql).fetchall() 
        return render_template("Suggestion.html",ndata=ndata,data=data,message=str, gap=gap, normal= normal, require=require)


@app.route('/map_p')
def Gmap():
    sql="SELECT * FROM buying_place"
    result = db.session.execute(sql)
    data = result.fetchall()  # 获取查询结果
    num_results = data.rowcount
    if (int(num_results) == 0):
        flash('place data not found.')
        return render_template("map_log.html")
    elif(int(num_results) > 0): 
        data=db.engine.execute(sql).fetchall() 
        return render_template("map_log.html",data=data)

@app.route('/map')
def Gomap():
    sql=text("SELECT * FROM buying_place")
    result = db.session.execute(sql)
    num_results = result.rowcount  # 获取查询结果
    if (int(num_results) == 0):
        flash('place data not found.')
        return render_template("map.html")
    elif(int(num_results) > 0): 
        data= db.session.execute(sql).fetchall() 
        return render_template("map.html",data=data)

@app.route('/add_place')
def addMap():
    return render_template("map_add.html")

@app.route('/add_place',methods=['POST'])
def addGMap():
    id = session.get('userID')
    place_name = request.form['place_name']
    place_url = request.form['place_url']
    sql = text("SELECT * FROM buying_place WHERE place_name = '{}'".format(place_name))
    results = db.session.execute(sql)
    num_results = results.rowcount
    PID = str(getplaceID())
    if (int(num_results) == 0):
        sql =text("INSERT INTO buying_place (placeId, place_name, place_url, ID) VALUE (%s, %s, %s, %s)")
        db.session.execute(sql,(PID,place_name,place_url,id))
        flash('Buying Places Added Successfully')
        return render_template("map_add.html")
    elif (int(num_results) > 0):
        flash('Buying places already exists.')
        return render_template("map_add.html")

@app.route('/MPM_View')
def GooMap():
    id = session.get('userID')
    sql="SELECT * FROM buying_place WHERE ID = '{}'".format(id)
    data=db.engine.execute(sql)
    num_results = data.rowcount
    if (int(num_results) == 0):
        flash('The own store data is not found.')
        return render_template("map_merchant.html")
    elif(int(num_results) > 0): 
        data=db.engine.execute(sql).fetchall() 
        return render_template("map_merchant.html",data=data)

@app.route('/merchant_add_place',methods=['POST'])
def addMGMap():
    id = session.get('userID')
    place_name = request.form['place_name']
    place_url = request.form['place_url']
    sql = text("SELECT * FROM buying_place WHERE place_name = '{}'".format(place_name))
    results = db.session.execute(sql)
    num_results = results.rowcount
    PID = str(getplaceID())
    if (int(num_results) == 0):
        sql =text("INSERT INTO buying_place (placeId, place_name, place_url, ID) VALUE (%s, %s, %s, %s)")
        db.session.execute(sql,(PID,place_name,place_url,id))
        flash('Buying Places Added Successfully')
        return render_template("Merchant_map_add.html")
    elif (int(num_results) > 0):
        flash('Buying places already exists.')
        return render_template("Merchant_map_add.html")

@app.route('/MPM_Add')
def GooMap_Add():
    return render_template("Merchant_map_add.html")

@app.route('/MPM_MG')
def MPM_view():
    id = session.get('userID')
    sql = text("SELECT * FROM buying_place WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_placeMG.html",data = data)

@app.route('/Merchant_Delete',methods=['POST'])
def Merchant_Delete():
    place_id = request.form.get('place_id')
    sql = text("DELETE FROM buying_place WHERE placeId = '{}'".format(place_id))
    db.session.execute(sql)
    sql = text("SELECT * FROM buying_place WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_placeMG.html",data = data)

@app.route('/Merchant_Update',methods=['POST'])
def Merchant_Update():
    place_id = request.form.get('place_id')
    sql = text("SELECT * FROM buying_place WHERE placeId = '{}'".format(place_id))
    data=db.session.execute(sql)
    num_results = data.rowcount
    if (int(num_results) == 0):
        flash('User data not found.')
        return redirect(url_for('MPM_MG'))
    elif(int(num_results) > 0): 
        data=db.session.execute(sql).fetchall() 
        return render_template("Merchant(edit).html",data=data)

@app.route('/Merchant_Edit',methods=['POST'])
def Merchant_Edit():
    id = session.get('userID')
    placeId = request.form['placeId']
    placeName = request.form['placeName']
    file = request.files['image']
    placeLoc = request.form['placeLoc']
    placeDesc = request.form['placeDesc']
    placeContact = request.form['placeContact']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        sql = text("UPDATE buying_place SET place_name = %s, place_image = %s, place_location = %s, place_desc = %s , place_contact = %s WHERE placeId = %s;")
        db.session.execute(sql,(placeName, filename, placeLoc, placeDesc, placeContact, placeId))
    else:
        sql = text("UPDATE buying_place SET place_name = %s, place_location = %s, place_desc = %s , place_contact = %s WHERE placeId = %s;")
        db.session.execute(sql,(placeName, placeLoc, placeDesc, placeContact, placeId))
    sql = text("SELECT * FROM buying_place WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_placeMG.html",data = data)

@app.route('/MSDM_View')
def Merchant_store_view():
    id = session.get('userID')
    sql = text("SELECT * FROM food WHERE ID = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_storeMG.html",data = data)

@app.route('/MSDM_Add')
def Merchant_food_page():
    return render_template("Merchant_store_add.html")

@app.route('/merchant_add_food', methods=['POST'])
def Merchant_food_add():
    id = session.get('userID')
    FID = getfoodID()
    foodName = request.form['foodName']
    file = request.files['image']
    foodDesc = request.form['foodDesc']
    foodPrice = request.form['foodPrice']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        sql = text("INSERT INTO food (Food_ID, Food_Name, Food_Image, Food_Desc, Food_Price, ID) VALUES (%s,%s,%s,%s,%s,%s) ")
        db.session.execute(sql,(FID, foodName, filename, foodDesc, foodPrice, id))
    else:
        sql = text("INSERT INTO food (Food_ID, Food_Name, Food_Desc, Food_Price, ID) VALUES (%s,%s,%s,%s,%s) ")
        db.session.execute(sql,(FID, foodName, foodDesc, foodPrice, id))
    sql = text("SELECT * FROM food WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_storeMG.html",data = data)

@app.route('/Merchant_store_Delete', methods=['POST'])
def Merchant_food_delete():
    foodId = request.form['foodId']
    id = session.get('userID')
    sql = text("DELETE FROM food WHERE Food_ID = '{}'".format(foodId))
    db.session.execute(sql)
    sql = text("SELECT * FROM food WHERE ID = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_storeMG.html",data = data)

@app.route('/Merchant_store_Update', methods=['POST'])
def Merchant_Update_store():
    food_id = request.form.get('foodId')
    sql = text("SELECT * FROM food WHERE FOOD_ID = '{}'".format(food_id))
    data=db.session.execute(sql)
    num_results = data.rowcount
    if (int(num_results) == 0):
        flash('User data not found.')
        return redirect(url_for('MSDM_View'))
    elif(int(num_results) > 0): 
        data=db.engine.execute(sql).fetchall() 
        return render_template("Merchant(editfood).html",data=data)

@app.route('/Merchant_EditFood', methods=['POST'])
def Merchant_EditFood():
    id = session.get('userID')
    foodId = request.form['foodId']
    foodName = request.form['foodName']
    file = request.files['image']
    foodDesc = request.form['foodDesc']
    foodPrice = request.form['foodPrice']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        sql = text("UPDATE food SET Food_Name = %s, Food_Image = %s, Food_Desc = %s, Food_Price = %s WHERE Food_ID = %s;")
        db.session.execute(sql,(foodName, filename, foodDesc, foodPrice, foodId))
    else:
        sql = text("UPDATE food SET Food_Name = %s, Food_Desc = %s, Food_Price = %s WHERE Food_ID = %s;")
        db.session.execute(sql,(foodName, foodDesc, foodPrice, foodId))
    sql = text("SELECT * FROM food WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("Merchant_storeMG.html",data = data)

@app.route('/Food_Detail',methods=['POST'])
def show_food_detail():
    id = request.form['temp']
    sql = text("SELECT * FROM food WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("map_show_food.html",data = data)

@app.route('/Food_Detail_public',methods=['POST'])
def show_food_detail_public():
    id = request.form['temp']
    sql = text("SELECT * FROM food WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("map_show_food(public).html",data = data)

@app.route('/Food_Detail_user',methods=['POST'])
def show_food_detail_user():
    id = request.form['temp']
    sql = text("SELECT * FROM food WHERE Id = '{}'".format(id))
    data = db.session.execute(sql).fetchall()
    return render_template("map_show_food(user).html",data = data)
    
@app.route('/responeProblem')
def showProblemForm():
    return render_template("ResponseProblem_log.html")
@app.route('/responeProblem',methods=['POST'])
def receiveProblem():
    ID = session.get('userID')
    problem = request.form['problem']
    scan = request.form['scan']
    date = datetime.date.today()
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = cv2.imread("C:\\Users\\User\\Documents\\USB\\FYP_py_db\\fyp_python_v1\\New_fyp\\static\\uploads\\"+filename)
        photo = "C:\\Users\\User\\Documents\\USB\\FYP_py_db\\fyp_python_v1\\New_fyp\\static\\uploads\\"+filename
        empPicture = convertToBinaryData(photo)
    InsertProblemData(empPicture, filename, date)
    InsertProblemInfo(ID, problem, scan,"not prcess")
    return render_template("ResponseResult.html")

@app.route('/ListProblem')
def ListProblem():
    sql = text("SELECT SPID,ImageName,Problem,ReScan,ID,UpLoadDate,Status,StaffID FROM scanningproblem, problemdata WHERE scanningproblem.SDID = problemdata.SDID")
    data = db.session.execute(sql).fetchall()
    return render_template("Admin_ProblemList.html", data= data)

@app.route('/PrcessProblem',methods=['POST'])
def PrcessProblem():
    SPID = request.form['SPID']
    ID = request.form['ID']
    return render_template("Admin_Scanner.html",SPID = SPID,ID = ID)

@app.route('/SolveProblem',methods=['POST'])
def SolveProblem():
    ID = session.get('userID')
    SPID = request.form['SPID']
    date = datetime.date.today()
    sql = text("UPDATE scanningproblem SET staffID = %s, EditDate = %s, Status='Solved' WHERE SPID = %s")
    db.session.execute(sql,(ID,date,SPID))
    return redirect(url_for('ListProblem'))

@app.route('/shopList')
def Shops():
    sql =text("SELECT placeId, place_name FROM buying_place")
    res = db.session.execute(sql).fetchall()
    return render_template("Admin_ShopList.html",data =res)

@app.route('/Admin_searchAccount')
def searchAccount():
    return render_template("Admin_searchAccount.html",action = "hide")

@app.route('/Admin_searchAccount',methods=['POST'])
def searchAcc():
    type = request.form['type']
    value = request.form['value']
    if(type =="id"):
        sql = text("SELECT * FROM account WHERE ID = '{}'".format(value))
        results = db.session.execute(sql).fetchall()
        if(len(results) == 0 ):
            msg = "Can not find related Records"
        else:
            msg = ""
    else:
        sql = text("SELECT * FROM account WHERE userType = '{}'".format(value))
        results = db.session.execute(sql).fetchall()
        if(len(results) == 0 ):
            msg = "Can not find related Records"
        else:
            msg = ""
    return render_template("Admin_searchAccount.html",action = "show", data=results,message = msg, type=type,value = value)

@app.route('/AdminDelAccount',methods=['POST'])
def AdminDelAccount():
    ID = request.form['ID']
    sql = text("SELECT IID FROM image WHERE ID ='{}'".format(ID))
    res = db.session.execute(sql).fetchall()
    for i in range(len(res)):
        iid = res[i].IID
        sql = text("DELETE FROM food_label WHERE IID = '{}'".format(iid))
        db.session.execute(sql)
    sql = text("DELETE FROM image WHERE ID ='{}'".format(ID))
    db.session.execute(sql)
    sql = text("DELETE FROM nutrient_info WHERE ID ='{}'".format(ID))
    db.session.execute(sql)
    sql = text("DELETE FROM exerciseamount WHERE ID = '{}'".format(ID))
    db.session.execute(sql)
    sql = text("DELETE FROM account WHERE ID ='{}'".format(ID))
    db.session.execute(sql)
    return redirect(url_for('searchAcc'))

@app.route('/delAccount')
def delAccount():
    user_id = session.get('userID')
    sql = text("SELECT IID FROM image WHERE ID ='{}'".format(user_id))
    res = db.session.execute(sql).fetchall()
    for i in range(len(res)):
        iid = res[i].IID
        sql = text("DELETE FROM food_label WHERE IID = '{}'".format(iid))
        db.session.execute(sql)
    sql = text("DELETE FROM image WHERE ID ='{}'".format(user_id))
    db.session.execute(sql)
    sql = text("DELETE FROM nutrient_info WHERE ID ='{}'".format(user_id))
    db.session.execute(sql)
    sql = text("DELETE FROM exerciseamount WHERE ID = '{}'".format(user_id))
    db.session.execute(sql)
    sql = text("DELETE FROM Account WHERE ID ='{}'".format(user_id))
    db.session.execute(sql)
    return render_template("index_page.html")

@app.route('/searchRecord')
def searchRecords():
    return render_template("RecordSearch_log.html",action = "hide")

@app.route('/searchRecord',methods=['POST'])
def searchRecord():
    user_id = session.get('userID')
    type= request.form['time']
    date = request.form['input']
    Date = date.split("-")
    if(type =="month"):
        sql = text("SELECT ImageName, image.IID, Calories, Total_Fat, Sodium, Total_Carbohydrate, Protein FROM image, food_label WHERE image.ID = '{}' AND image.IID = food_label.IID AND MONTH(upload_date) ='{}' AND YEAR(upload_date) ='{}' ".format(user_id,Date[1],Date[0]))
    else:
        sql = text("SELECT ImageName, image.IID, Calories, Total_Fat, Sodium, Total_Carbohydrate, Protein FROM image, food_label WHERE image.ID = '{}' AND image.IID = food_label.IID AND upload_date ='{}'".format(user_id,date))
    data = db.session.execute(sql).fetchall()
    if(len(data) == 0 ):
        msg = "Can not find related Records"
    else:
        msg = ""
    return render_template("RecordSearch_log.html",action="show",data=data,message = msg, type = type, value=date)

@app.route('/delRecord',methods=['POST'])
def delRecord():
    IID = request.form.get('IID')
    sql = text("DELETE FROM food_label WHERE IID = '{}'".format(IID))
    db.session.execute(sql)
    sql = text("DELETE FROM image WHERE IID ='{}'".format(IID))
    db.session.execute(sql)
    return redirect(url_for('searchRecord'))

@app.route('/Admin_searchRecord')
def searchRD():
    return render_template("Admin_searhRecords.html",action="hide")
@app.route('/Admin_searchRecord',methods=['POST'])
def searchRDs():
    type= request.form['type']
    value = request.form['input']
    if(type == 'month'):
        time = value.split('-')
        sql = text("SELECT ImageName, image.IID, Calories, Total_Fat, Sodium, Total_Carbohydrate, Protein FROM image, food_label WHERE YEAR(image.upload_date)='{}' AND MONTH(image.upload_date) = '{}' AND image.IID = food_label.IID".format(time[0],time[1]))
        data = db.session.execute(sql).fetchall()
    elif(type == 'id'):
        sql = text("SELECT ImageName, image.IID, Calories, Total_Fat, Sodium, Total_Carbohydrate, Protein FROM image, food_label WHERE image.ID = '{}' AND image.IID = food_label.IID".format(value))
        data = db.session.execute(sql).fetchall()
    else:
        sql = text("SELECT ImageName, image.IID, Calories, Total_Fat, Sodium, Total_Carbohydrate, Protein FROM image, food_label WHERE image.upload_date = '{}' AND image.IID = food_label.IID".format(value))
        data = db.session.execute(sql).fetchall()
    if(len(data) == 0 ):
        msg = "Can not find related Records"
    else:
        msg = ""
    return render_template("Admin_searhRecords.html",action="show",data=data,message = msg, type = type, value=value)

@app.route('/AdmindelRecord',methods=['POST'])
def AdmindelRecord():
    IID = request.form.get('IID')
    sql = text("DELETE FROM food_label WHERE IID = '{}'".format(IID))
    db.session.execute(sql)
    sql = text("DELETE FROM image WHERE IID ='{}'".format(IID))
    db.session.execute(sql)
    return redirect(url_for('searchRDs'))
    
@app.route('/shop_Del',methods=['POST'])
def delShop():
    data = request.form.get('pID')
    sql = text("DELETE FROM buying_place WHERE placeId = '{}'".format(data))
    db.session.execute(sql)
    return redirect(url_for('Shops'))

if __name__ == "__main__":
    app.run(debug=True)