#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hashlib import sha1
import random


def hexuserpass(password):
    """
    加密使用者发布代码时的密码，所以使用最简单的加密方法
    """
    enpass = sha1(password.encode('utf-8')).hexdigest()
    return enpass


def checkuserpass(passwd, enpass):
    password = hexuserpass(passwd)
    return (password == enpass)


def hexpassword(password):
    """
    加密管理员密码，就目前来说，这个加密强度也太弱了，可以考虑使用 `pbkdf2` 加密方法
    """
    seed = "1234567890abcdefghijklmnopqrstuvwxyz   \
            ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
    sa = []
    for i in range(8):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    enpass = sha1(sha1((salt + password).encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()
    return str(salt) + '$' + str(enpass)


def checkpassword(passwd, enpass):
    salt = enpass[:8]
    password = sha1(sha1((salt + passwd).encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()
    p = str(salt) + '$' + str(password)
    return (p == enpass)
