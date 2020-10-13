# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
# 由于python2和python3中urlparse, urljoin所在的包不同，所以这里做了个兼容性处理
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, session, jsonify

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')


# get name value from query string and cookie
@app.route('/')
@app.route('/hello')
# 欢迎页面，获取用户登录名，判断其是否认证以返回不同信息，若未查到用户名则以'Human'作为用户名
def hello():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % escape(name)  # escape name to avoid XSS
    # return different response according to the user's authentication status
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response


# redirect:重定向
@app.route('/hi')
def hi():
    return redirect(url_for('hello'))


# use int URL converter:转换器的使用（即这里的int），因为默认输入的都被识别为字符串型，
# 所以按需进行相应转换，也就是数据类型转换
@app.route('/goback/<int:year>')
def go_back(year):
    return 'Welcome to %d!' % (2018 - year)


# use any URL converter 转换器
@app.route('/colors/<any(blue, white, red):color>')
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude.</p>'


# return error response
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'


# 404
@app.route('/404')
def not_found():
    abort(404)


# return response with different formats
# 展示4种MIME类型的响应数据
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1>Note</h1>
  <p>to: Peter</p>
  <p>from: Jane</p>
  <p>heading: Reminder</p>
  <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
'''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
'''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# set cookie
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello')))
    response.set_cookie('name', name)
    return response


# log in user
@app.route('/login')
def login():
    session['logged_in'] = True
    return redirect(url_for('hello'))


# protect view,只有登录后才可看见此视图
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to admin page.'


# log out user
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hello'))


# AJAX
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=3)
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


# redirect to last page
# request.full_path得到的是当前视图的相对地址，并非全地址
@app.route('/foo')
def foo():
    print('request.full_path: '+request.full_path)
    print(url_for('do_something', next=request.full_path))
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)
# 这里加了 next=request.full_path，在返回结果上变成了/do-something?next=%2Ffoo%3F
# 而？后的内容都是查询字符串，以键值对的形式给出，经解析后存储在request.args中，所以在
# redirect_back()中可以通过request.args.get('next')查到，为/foo


@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/do-something')
def do_something():
    # do something here
    return redirect_back()


# 检查URL的安全性，即判断它是否为属于程序内部URL
def is_safe_url(target):
    ref_url = urlparse(request.host_url)  # 获取程序内的主机URL
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# request.referrer存的是全地址
def redirect_back(default='hello', **kwargs):
    for target in request.referrer, request.args.get('next'):
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))  # 如果前面方法都定位失败，则定位到'hello'视图
