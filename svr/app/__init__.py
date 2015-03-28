# -*- coding:utf-8 -*-

__author__ = 'Wyben Gu'


from datetime import datetime,timedelta
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import view, models


@app.template_filter('datetime')
def datetime_filter(dt):

    delta = (datetime.utcnow()-dt).seconds
    
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta//60)
    if delta < 86400:
        return u'%s小时前' % (delta //3600)
    if delta < 604800:
        return u'%s天前' % (delta //86400)

    china_zone = timedelta(seconds=28800)   
    localtime = dt  + china_zone

    return u'%s年%s月%s日%s点%s分%s秒' % (localtime.year, localtime.month, localtime.day, localtime.hour, localtime.minute, localtime.second)


