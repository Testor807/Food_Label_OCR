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

def getdata(user_id): 
    ndata=[]
    sql = "SELECT Calories FROM image, food_label WHERE image.ID = '{}' AND image.IID = food_label.IID".format(user_id)
    ndata = db.engine.execute(sql).fetchall()
    return ndata