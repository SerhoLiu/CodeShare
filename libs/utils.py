#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hashlib import sha1
import random


def hexuserpass(password):
    enpass = sha1(password.encode('utf-8')).hexdigest()
    return enpass


def checkuserpass(passwd, enpass):
    password = hexuserpass(passwd)
    if password == enpass:
        return True
    else:
        return False


def hexpassword(password):
    """
    加密密码
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
    if p == enpass:
        return True
    else:
        return False
