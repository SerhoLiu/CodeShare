#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from code import BaseHandler
from libs.utils import hexpassword, checkpassword


class SiteStartHandler(BaseHandler):
    
    def get(self):
        admin = self.db.query("SELECT * FROM users ORDER BY id DESC LIMIT 1")
        if not admin:
            self.render("start.html")
        else:
            self.redirect("/")
    
    def post(self):
        email = self.get_argument("email")
        pswd1 = self.get_argument("password1")
        pswd2 = self.get_argument("password2")
    	
        if pswd1 != pswd2:
            self.redirect("/admin/start")
            password = hexpassword(pswd1)
            self.db.execute(
                "INSERT INTO users (password,email) VALUES (%s,%s)", password, email)
        self.redirect("/auth/login")


class LoginHandler(BaseHandler):

    def get(self):
        if self.current_user:
            self.redirect("/")
            return
        self.render("login.html", msg=0)
    
    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password")
        
        user = self.db.get("SELECT * FROM users WHERE email = %s", email)
        if user and checkpassword(password, user["password"]):
            self.set_secure_cookie("user", str(user["id"]))
            self.redirect("/")
        else:
            msg = "Error"
            self.render("login.html", msg=msg)


class LogoutHandler(BaseHandler):
    
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class DeleteHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self, slug):
        code = self.db.get("SELECT * FROM entries WHERE slug = %s", str(slug))
        if not code:
            raise tornado.web.HTTPError(404)
        else:
            self.db.execute("DELETE FROM entries WHERE slug=%s", str(slug))
            self.redirect("/")
