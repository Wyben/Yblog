# -*- coding: utf-8 -*-

__author__ = 'Wyben Gu'

'''
Models for user,blog,comment.
'''

from app import db
from datetime import datetime

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True)
    email = db.Column(db.String(120),unique=True)
    password  = db.Column(db.String(120))
    admin = db.Column(db.Boolean)
    image = db.Column(db.String(500))
    register_date = db.Column(db.DateTime)
    
    def __init__(self, username, email, password, admin=False, image='',register_date=None):
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin
        self.image = image
        if register_date is None:
            register_date = datetime.utcnow()
        self.register_date = register_date
        
    @property
    def serialize(self):
       '''Return object data in easily serializeable format'''
       return {
           'id'            : self.id,
           'username'      : self.username,
           'password'      : self.password,
           'admin'         : self.admin,
           'image'         : self.image,
           'register_date' : dump_datetime(self.register_date)
       }
        
    def __repr__(self):
        return '<User %r>' % self.username

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    summary = db.Column(db.String(200))
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('blogs', lazy='dynamic'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('blogs',lazy='dynamic'))
    
    def __init__(self, title, summary, content, category, author, pub_date=None):
        self.title = title
        self.summary = summary
        self.content = content
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.category = category
        self.author = author
    
    @property
    def serialize(self):
       '''Return object data in easily serializeable format'''
       return {
           'id'         : self.id,
           'title'      : self.title,
           'summary'    : self.summary,
           'content'    : self.content,
           'pub_date'   : dump_datetime(self.pub_date),
           'category'   : self.category.serialize,
           'author'     : self.author.serialize
           # This is an example how to deal with Many2Many relations
           #'many2many'   : self.serialize_many2many
       }
    
    '''
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]
    '''
    
    def __repr__(self):
        return '<Blog %r>' % self.title
        
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
      
    def __init__(self, name):
        self.name = name

    @property
    def serialize(self):
       '''Return object data in easily serializeable format'''
       return {
           'id'         : self.id,
           'name'      : self.name
       }

    def __repr__(self):
        return '<Category %r>' % self.name

class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog = db.relationship('Blog', backref=db.backref('bcomments',lazy='dynamic'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('ucomments',lazy='dynamic'))
    
    def __init__(self, content, blog, author, pub_date=None):
        self.content = content
        self.blog = blog
        self.author = author
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        
    @property
    def serialize(self):
       '''Return object data in easily serializeable format'''
       return {
           'id'         : self.id,
           'content'    : self.content,
           'pub_date'   : dump_datetime(self.pub_date),
           'blog'       : self.blog.serialize,
           'author'     : self.author.serialize
       }
        
    def __repr__(self):
        return '<Comment %r>' % self.content
    
    
    
    
    
    
    
    
    
    
    
    
    
    
