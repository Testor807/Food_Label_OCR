from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from decimal import *
import pymysql
import os

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/fyp"

db.init_app(app)

def getInt(word):
    words = ""
    char = ["0","1","2","3","4","5","6","7","8","9"]
    for k in word:
        if (k in char):
            words=words+k
    return words

# sodium = 每天不要攝取超過2000 毫克 (即5克鹽)
sodium = 2
# cholesterol = 每天攝取量以 300 毫克為限

def CalEngerfy(sex,weight,height,age):
    global energy
    if (sex == "M") or (sex == "Male"):
        #male: energy = 10 x 體重（公斤）＋ 6.25 x 身高（公分）- 5  x 年齡 ＋5
        energy = 10*float(weight)+6.2*float(height)-5*int(age)+5
    if (sex == "F") or (sex == "Female"):
        #female: energy = 10 x 體重（公斤）＋ 6.25 x 身高（公分）- 5  x 年齡 – 161
        energy = 10*float(weight)+6.2*float(height)-5*int(age)-161

# protein 攝取量應為人體每天所需能量的 10% 至 15%
def CalProtein():
    global protein
    protein = energy*0.1
# tfat = 0攝取量應不超過人體每天所需能量的 1%
def CalTfa():
    global tfat
    tfat = energy*0.01
# total carbohydrate = 攝取量應為人體每天所需能量的 55% 至 75%。
def CalCDA():
    global carbohydrate
    carbohydrate = energy*0.55

def getRowID():
    sql ="SELECT * FROM nutrient_info"
    results = db.engine.execute(sql).fetchall()
    if((len(results)-1) == -1):
        NIID = "NI1"
    else:
        num = getInt(results[len(results)-1][0])
        NIID = "NI"+str(int(num)+1)
    return NIID


#Upload reference nutrient data into Database

def UploadDB(ID,sex,weight,height,age):
#def UploadDB():
    CalEngerfy(sex,weight,height,age)
    CalProtein()
    CalTfa()
    CalCDA()
    NIID = getRowID()
    sql = "SELECT * FROM nutrient_info WHERE ID = '{}'".format(ID)
    num = db.engine.execute(sql).fetchall()
    if(len(num) == 0):
        sql ="INSERT INTO nutrient_info VALUES('{}', '{}', '{}','{}', '{}','{}','{}')".format(NIID,ID,int(energy),tfat,int(sodium),int(carbohydrate),int(protein))
        results = db.engine.execute(sql)

    else:
        sql ="UPDATE nutrient_info SET Calorie = %s, Total_Fat = %s, Sodium = %s,Total_Carbohydrate = %s, Protein= %s WHERE ID = %s"
        results = db.engine.execute(sql,(int(energy),tfat,int(sodium),int(carbohydrate),int(protein),ID))