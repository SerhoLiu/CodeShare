#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sae.const

settings = {
    "sitename": "Code Share",#设置为你的站点名
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path":os.path.join(os.path.dirname(__file__), "static"),
    "xsrf_cookies": True,
    "cookie_secret":"11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp29g6P1o/Vo=",#设置为随机的一串字符，千万不要使用现在这个
    "login_url":"/auth/login",
    "autoescape": None,
    "debug":True,
}
#数据库设置
db = {
    "host": sae.const.MYSQL_HOST,
    "db": sae.const.MYSQL_DB,
    "port": sae.const.MYSQL_PORT,
    "user": sae.const.MYSQL_USER,
    "password": sae.const.MYSQL_PASS,
}