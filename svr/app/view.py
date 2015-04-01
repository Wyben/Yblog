# -*- coding:utf-8 -*-

'''#############################################
    A simple blog web application base on Flask.           
#############################################'''



__author__ = 'Wyben Gu'

import markdown2, re, hashlib
from app import app, db
from flask import request, render_template, g, session, abort, jsonify, redirect, url_for
from models import User, Blog, Category, Comment
from apis import Page,APIError,APIValueError,APIPermissionError,APIResourceNotFoundError

_MANAGEMENT_ROUTE = '/manage'

def _check_admin():
    user = g.user
    if user and user.admin:
        return True
    return False

@app.before_request
def before_request():
    g.user = None
    user_id = session.get('user_id',None)
    if user_id:
        g.user = User.query.filter_by(id=user_id).first()
    path = request.path
    if path.startswith(_MANAGEMENT_ROUTE):
        if not _check_admin():
            return redirect(url_for('login'))
        

def _get_page_index():
    return int(request.args.get('page','1'))
        
def _get_blogs_by_page():
    total = Blog.query.count()
    page = Page(total, _get_page_index())
    blogs = Blog.query.offset(page.offset).limit(page.limit).all()
    return blogs, page



'''#############################################
      Below are the views for users               
#############################################'''


@app.route('/', methods=['GET','POST'])
def index():
    '''Index page redirect to blogs page.'''

    blogs, page = _get_blogs_by_page()
    return render_template("blogs.html", user=g.user,blogs=blogs, page=page)

@app.route('/login', methods=['GET','POST'])
def login():
    '''Login page.'''
    
    if request.method == 'GET':
        return render_template("login.html")

@app.route('/logout')
def logout():
    '''
    logout
    '''
    session.pop('user_id',None)
    return redirect(url_for('index'))

#Register page
@app.route('/register', methods=['GET'])
def register():
    return render_template("register.html",action=url_for('api_register_user'))

#A blog page
@app.route('/blog/<blog_id>', methods=['GET'])
def blog(blog_id):
    '''Page for view a blog'''
    
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog is None:
        raise notfound()
    comments = Comment.query.filter_by(blog=blog).order_by('pub_date desc').all()
    category = Category.query.order_by('name').all()
    blog.html_content = markdown2.markdown(blog.content)
    return render_template("blog.html",blog=blog, comments=comments, user=g.user, categorys=category)



'''#########################################
#  Below are the views for management
#############################################'''


#Manage index page redirect to comments list page
@app.route('/manage/', methods=['GET'])
def manage_index():
    return redirect(url_for('manage_comments'))

#Comments list page
@app.route('/manage/comments', methods=['GET'])
def manage_comments():
    return render_template('manage_comment_list.html',page_index=_get_page_index(),user=g.user)

#Blogs list page
@app.route('/manage/blogs', methods=['GET'])
def manage_blogs():
    return render_template('manage_blog_list.html',page_index=_get_page_index(),user=g.user)

#Create the blog    
@app.route('/manage/blogs/create', methods=['GET'])
def manage_blogs_create():
    categorys = Category.query.all()
    kw =  dict(id=None, action=url_for('api_create_a_blog'), redirect=url_for('manage_blogs'), user=g.user, categorys=categorys) 
    return render_template('manage_blog_edit.html',**kw)

#Edit the blog by blog_id
@app.route('/manage/blogs/edit/<blog_id>', methods=['GET'])
def manage_blogs_eidt(blog_id):
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog is None:
        return abort(404)
    categorys = Category.query.all()
    kw = dict(id=blog.id, action=url_for('api_update_a_blog',blog_id=blog_id), redirect=url_for('manage_blogs'), user=g.user, categorys=categorys)
    return render_template('manage_blog_edit.html',**kw)

#Users list page
@app.route('/manage/users', methods=['GET'])
def manage_users():
    return render_template('manage_user_list.html',page_index=_get_page_index(),user=g.user)
    

@app.route('/manage/category', methods=['GET'])
def manage_category():
    # Category list page
    return render_template('manage_category.html',user=g.user)


'''#########################################
#  Below are the REST APIs
#############################################'''


@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """API for authenticate the user."""

    email = request.form['email']
    password = request.form['password']
    remember = request.form['remember']
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIError('auth:failed', 'email', 'Invalid email.')
    elif user._password != password:
        raise APIError('auth:failed', 'password', 'Invalid password.')
    #make session cookie:
    #max_age = 804800 if remember=='true' else None
    session['user_id'] = user.id
    return jsonify({'user': user.username})
    
'''-------------REST APIs for comments.-----------------'''

@app.route('/api/comments', methods=['GET'])
def api_get_comments():
    
    #API for get comments.
 
    total = Comment.query.count()
    page = Page(total, _get_page_index())
    #comments = Comment.find_by('order by created_at desc limit ?,?',page.offset, page.limit)
    comments = Comment.query.order_by('pub_date desc').offset(page.offset).limit(page.limit).all()

    return jsonify({'comments': [ i.serialize for i in comments ],'page': page.serialize })

@app.route('/api/blogs/<blog_id>/comments', methods=['POST'])
def api_create_blog_comment(blog_id):
    
    #API for post a blog comment
    
    user = g.user
    if user is None:
        raise APIPermissionError('Need signin.')
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    content = request.form['content']
    if not content:
        raise APIValueError('content')
    cmt = Comment(content=content, author=user,blog=blog)
    db.session.add(cmt)
    db.session.commit()
    return jsonify({'Comment Post':'success'})

@app.route('/api/comments/<comment_id>/delete', methods=['POST'])
def api_delete_comment(comment_id):
    
    #API for delete a comment
    
    if not _check_admin():
        raise APIPermissionError('No permission.')
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment is None:
        raise APIResourceNotFoundError('Comment')
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'Comment Del':'success'})


'''---------------REST APIs for blog--------------------'''


@app.route('/api/blogs', methods=['GET'])
def api_get_blogs():
    
    #----API for get blogs.--------#
    
    #format = 'html' #request.get('format', '')
    blogs,page = _get_blogs_by_page()
    #if format=='html':
    #   for blog in blogs:
    #        blog.content = markdown2.markdown(blog.content)
    #return dict(blogs=blogs,page=page)
    return jsonify({'blogs': [ i.serialize for i in blogs ],'page': page.serialize })

@app.route('/api/blogs/<blog_id>', methods=['GET'])
def api_get_blog(blog_id):
    
    #API for get a blog.
    
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog:
        return jsonify(blog.serialize)
    raise APIResourceNotFoundError('Blog')

@app.route('/api/blogs/create', methods=['POST'])
def api_create_a_blog():
    
    #API for create a blog.
    if not _check_admin():
        raise APIPermissionError('No permission.')
    title = request.form['title']
    category_name = request.form['category']
    summary = request.form['summary']
    content = request.form['content']
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    if not category_name:
        raise APIValueError('category', 'category cannot be empty.')
    if not summary:
        raise APIValueError('summary', 'summary can not be empty.')
    if not content:
        raise APIValueError('content', 'content can not be empty.')
    
    user = g.user
    category = Category.query.filter_by(name=category_name).first()
    blog = Blog(title=title,summary=summary,content=content,author=user,category=category)
    db.session.add(blog)
    db.session.commit()
    return jsonify({'CreateBlog': 'sussed'})


@app.route('/api/blogs/<blog_id>', methods=['POST'])
def api_update_a_blog(blog_id):
    
    #API for update a blog.
    
    if not _check_admin():
        raise APIPermissionError('No permission.')
    title = request.form['title']
    category_name = request.form['category']
    summary = request.form['summary']
    content = request.form['content']
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    if not category_name:
        raise APIValueError('category', 'category cannot be empty.')
    if not summary:
        raise APIValueError('summary', 'summary can not be empty.')
    if not content:
        raise APIValueError('content', 'content can not be empty.')
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    category = Category.query.filter_by(name=category_name).first()
    if category is None:
        raise APIResourceNotFoundError('Category')
    blog.title = title
    blog.category = category
    blog.summary = summary
    blog.content = content
    db.session.commit()
    return jsonify({'UpdateBlog': 'suceed'})

@app.route('/api/blogs/<blog_id>/delete', methods=['POST'])
def api_delete_blog(blog_id):
    
    #API for delete a blog.
    
    if not _check_admin():
        raise APIPermissionError('No permission.')
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comments = Comment.query.filter_by(blog=blog).all()
    print 'AAAAAAAAAAAAAAAAAAAAAAAAaaaa'
    db.session.delete(comments)
    db.session.delete(blog)
    db.session.commit()
    return jsonify({'Delete Blog': 'suceed'})

'''-------------REST APIs for user-----------------'''

@app.route('/api/users', methods=['GET'])
def api_get_users():

    #API for get users.

    total = User.count_all()
    page = Page(total, _get_page_index())
    users = User.find_by('order by created_at desc limit ?,?',page.offset, page.limit)
    for u in users:
        u.password = '******'
    return dict(users=users,page=page)


#Regular expess for identify the email and password
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_PASSWORD_MD5 = re.compile(r'^[0-9a-f]{32}$')

@app.route('/api/users/create', methods=['POST'])
def api_register_user():
    """API for register a user."""
    
    name = request.form['name']
    email = request.form['email'].lower()
    password = request.form['password']
    if not name:
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not password:
        raise APIValueError('password')
    user = User.query.filter(User.email==email).first()
    if user:
        raise APIError('register:failed','email','Email is already in use.')
    user = User(username=name, email=email, password=password, image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email).hexdigest())
    db.session.add(user)
    db.session.commit()
    # make session cookie:
    session['user_id'] = user.id
    return jsonify(user.serialize)

'''-------------REST APIs for user-----------------'''

@app.route('/api/category', methods=['GET'])
def api_get_category():

    #API for get category.

    category = Category.query.all()
    return jsonify({'category': [ i.serialize for i in category ]})


@app.route('/api/category/add', methods=['POST'])
def api_add_category():
    
    #API for add a category.
    
    name = request.form['name']
    if not name:
        raise APIValueError('name')
    category = Category.query.filter_by(name=name).first()
    if category:
        raise APIError('Add:failed','Category','Category is already in use.')
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify({'Add category suceed': category.name})

@app.route('/api/category/<category_id>/delete', methods=['POST'])
def api_delete_category(category_id):
    
    #API for delete a blog.
    
    if not _check_admin():
        raise APIPermissionError('No permission.')
    category = Category.query.filter_by(id=category_id).first()
    if blog is None:
        raise APIResourceNotFoundError('Category')
    db.session.delete(category)
    db.session.commit()
    return jsonify({'Delete category suceed': category.name})

  
