# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
from flask import Flask, render_template, flash, redirect, url_for, Markup

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

user = {
    'username': 'Grey Li',
    'bio': 'A boy who loves movies and music.',
}

movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'},
]


# watchlist.html是在template文件夹下写好的一个模板，通过render_template()函数（Flask提供的渲染函数）
# 渲染后，原模板中的变量会被替换，注释被删除等，然后用户执行watchlist请求后就看到渲染后的内容，user和movies在
# 模板中要用到，所以这里传入
@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/base')
def base():
    return render_template('base.html')


# register template context handler
# 经过该装饰器注册的函数称为模板上下文处理函数，当用render_template()渲染任意模板时，该上下文处理函数都会被执行，
# 且函数的返回值被添加进模板，所以可在模板中直接使用它返回的变量。
@app.context_processor
def inject_info():
    foo = 'I am foo.'
    return dict(foo=foo)  # equal to: return {'foo': foo}


# register template global function
# 将函数注册为模板全局函数（只能注册全局函数），这里和@app.context_processor不同，
# 经@app.context_processor注册的函数在模板被渲染时自动执行，而这里是成为全局函数，
# 在模板中可直接调用
@app.template_global()
def bar():
    return 'I am bar.'


# register template filter
# 该装饰器注册自定义过滤器，在html模板中使用方法：{{value|filter}}，相当于Python中的
# filter(value)，且过滤器可嵌套使用，如{{value|filter1|filter2}}
# Markup
@app.template_filter()
def musical(s):
    return s + Markup(' &#9835;')


# register template test
# 注册自定义模板测试器，使用方法为value is tester，返回值为布尔值
@app.template_test()
def baz(n):
    if n == 'baz':
        return True
    return False


@app.route('/watchlist2')
def watchlist_with_static():
    return render_template('watchlist_with_static.html', user=user, movies=movies)


# message flashing
@app.route('/flash')
def just_flash():
    flash('你好，这是一条flash')  # flash可用在任意视图函数中，然后在模板中用内置全局函数get_flashed_message()获取flash所传的信息并显示在页面上
    return redirect(url_for('index'))


# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
