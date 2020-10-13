# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import click
from flask import Flask

app = Flask(__name__)


# the minimal Flask application
# app.route()装饰器把根地址(/)和函数index()绑定起来，当用户访问该URL(/)时就触发此函数index()
@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'


# bind multiple URL for one view function
@app.route('/hi')
@app.route('/hello')
def say_hello():
    return '<h1>Hello, Flask!</h1>'


# dynamic route, URL variable default
# 绑定动态URL，即URL除了写死的基本部分(/greet)，用户还可手动写入(<name>)
@app.route('/greet', defaults={'name': 'Programmer'})
@app.route('/greet/<name>')
def greet(name):
    return '<h1>Hello, %s!</h1>' % name


# custom flask cli command
@app.cli.command()
def hello():
    """Just say hello."""
    click.echo('Hello, Human!')


# 执行flask run时，该命令运行的开发服务器默认会监听http://127.0.0.1:5000，
# http://127.0.0.1即localhost，是指向本地机的IP地址，而5000端口是Flask默认使用的端口。
