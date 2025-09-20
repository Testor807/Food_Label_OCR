from cv2 import normalize
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from decimal import *
import datetime
import pymysql
import os

from sqlalchemy import false, null, true

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/fyp"

db.init_app(app)

def getDailyNutrient(accID):
    global Fat
    global Sodium
    global Carbohydrate
    global Protein
    global normal
    global empty
    global Calorie
    empty = false
    Calorie = 0
    Fat = 0
    Sodium = 0 
    Carbohydrate  = 0 
    Protein  = 0 
    normal = []
    date = datetime.date.today()
    #target date
    nd = date - datetime.timedelta(days=7)
    sql = "SELECT Calories, Total_Fat, Sodium, Total_Carbohydrate,Protein FROM food_label,image WHERE image.ID = '{}' AND image.IID = food_label.IID AND image.UpLoad_Date >= '{}'".format(accID,nd)
    #sql = "SELECT * FROM image WHERE Upload_Date >= '{}'".format(nd) 
    #results = db.engine.execute(sql)
    data = db.engine.execute(sql).fetchall()
    #num_results = results.rowcount
    if(len(data) != 0):
        for i in range(len(data)):
            Calorie += data[i][0]
            Fat += data[i][1]
            Sodium += data[i][2]
            Carbohydrate += data[i][3]
            Protein += data[i][4]
        normal.append(int(Calorie/len(data)))
        normal.append(int(Fat/len(data)))
        normal.append(int(Sodium/len(data)))
        normal.append(int(Carbohydrate/len(data)))
        normal.append(int(Protein/len(data)))
    else:
        empty = true
        for x in range(5):
            normal.append("null")

def getRequiredNutrient(accID):
    global R_Calorie
    global R_Fat
    global R_Sodium
    global R_Carbohydrate
    global R_Protein
    global require
    R_Calorie = 0
    R_Fat = 0
    R_Sodium = 0
    R_Carbohydrate = 0
    R_Protein = 0
    require = []
    sql = "SELECT Calorie,Total_Fat, Sodium, Total_Carbohydrate,Protein FROM nutrient_info WHERE ID = '{}'".format(accID)
    data = db.engine.execute(sql).fetchall()
    if(len(data) != 0):
        R_Calorie = data[0][0]
        R_Fat = data[0][1]
        R_Sodium = data[0][2]
        R_Carbohydrate = data[0][3]
        R_Protein = data[0][4]
        require.append(R_Calorie)
        require.append(R_Fat)
        require.append(R_Sodium)
        require.append(R_Carbohydrate)
        require.append(R_Protein)
    else:
        for x in range(5):
            require.append("null")

def CompareNutrient(accID):
    getDailyNutrient(accID)
    getRequiredNutrient(accID)
    str = []
    gap = []
    if(empty == true):
        for x in range(5):
            gap.append(0)
        str.append("Sorry, Having not enough data to analysis result!")
    else:
        calorie = int(Calorie)-int(R_Calorie)
        fat = int(Fat)-int(R_Fat)
        sodium = int(Sodium)-int(R_Sodium)
        carbohydrate = int(Carbohydrate)-int(R_Carbohydrate)
        protein = int(Protein)-int(R_Protein)
        gap.append(calorie)
        gap.append(fat)
        gap.append(sodium)
        gap.append(carbohydrate)
        gap.append(protein)
        if(fat>0):
            str.append("You should eat less food which is included hight fat!")
        if(sodium>0):
            str.append("You should eat less food which is included hight sodium!")
        if(carbohydrate<0):
            str.append("You should eat more food which is included hight total_carbohydrate!")
        if(protein<0):
            str.append("You should eat more food which is included hight protein such as soy food or dairy food!")
        if(len(str) == 0):
            str.append("You should keep current intake!")
    
    return (str, gap)

def getNurient():
    return (normal, require)
    
if __name__ == "__main__":
    app.run(debug=True)