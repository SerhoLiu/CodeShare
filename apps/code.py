#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs import markdown
import tornado.database
import tornado.web
from tornado.escape import xhtml_escape

import sae.const
from libs.utils import hexuserpass,checkuserpass
from settings import db

md = markdown.Markdown(safe_mode=True)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        blogdb = tornado.database.Connection(
            host=db["host"]+":"+db["port"], database=db["db"],
            user=db["user"], password=db["password"])
        return blogdb

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.db.get("SELECT * FROM users WHERE id = %s", int(user_id))


class HomeHandler(BaseHandler):
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 8")
        results = self.db.query("SELECT COUNT(*) As code FROM entries")
        navnum = 8
        count = results[0].code
        if count % navnum==0:
            pages = count / navnum
        else:
            pages = count / navnum + 1
        if not entries:
            self.redirect("/newcode")
            return
        self.render("home.html", entries=entries,pages=pages)

class PageHandler(BaseHandler):

    def get(self,id):
        navnum = 8
        results = self.db.query("SELECT COUNT(*) As code FROM entries")
        count = results[0].code
        if count % navnum==0:
            pages = count / navnum
        else:
            pages = count / navnum + 1
        offset = (int(id)-1) * navnum
        entries = self.db.query("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 8 OFFSET %s",offset)
        self.render("page.html",entries=entries,pages = pages,this=int(id))

class EntryHandler(BaseHandler):
    def get(self, slug):
        entry = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        if not entry: raise tornado.web.HTTPError(404)
        self.render("entry.html", entry=entry)


class FeedHandler(BaseHandler):
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 10")
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", entries=entries)


class ComposeHandler(BaseHandler):
    def get(self):
        entry = None
        self.render("compose.html")

    def post(self):
        id = self.get_argument("id", None)
        title = xhtml_escape(self.get_argument("title"))
        tep = self.get_argument("info") 
        code = xhtml_escape(self.get_argument("code"))
        pswd = self.get_argument("password")
        info = md.convert(tep)
        password = hexuserpass(pswd)
        slug = "zzzzzzzz"
        self.db.execute(
                "INSERT INTO entries (password,title,slug,code,info,"
                "published) VALUES (%s,%s,%s,%s,%s,UTC_TIMESTAMP())",
                 password, title, slug, code, info)
        e = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        eid = e.id
        slug = eid
        self.db.execute("UPDATE entries SET slug = %s WHERE id = %s", slug, int(eid))
        self.redirect("/"+str(slug))


class DeleteHandler(BaseHandler):

    def post(self):
        password = self.get_argument("password")
        id = self.get_argument("id")
        e = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
        
        if checkuserpass(password,e["password"]):
            self.db.execute("DELETE FROM entries WHERE id=%s", int(id))
            self.redirect("/")
        else:
            self.redirect("/"+str(id))
