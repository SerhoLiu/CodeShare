#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    code 发布和管理模块
"""

import datetime
import tornado.web
import tornado.database
from settings import db, NAVNUM
from libs import markdown
from tornado.escape import xhtml_escape
from libs.utils import hexuserpass, checkuserpass

md = markdown.Markdown(safe_mode=True)


class BaseHandler(tornado.web.RequestHandler):
    
    @property
    def db(self):
        blogdb = tornado.database.Connection(
            host=db["host"] + ":" + db["port"], database=db["db"],
            user=db["user"], password=db["password"])
        return blogdb

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id:
            return None
        return self.db.get("SELECT * FROM users WHERE id = %s", int(user_id))


class HomeHandler(BaseHandler):
    
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 8")
        if not entries:
            self.redirect("/newcode")
            return
        results = self.db.query("SELECT COUNT(*) As code FROM entries")
        count = results[0].code
        pages = (count - 1) / NAVNUM + 1
        self.render("home.html", entries=entries, pages=pages, counts=count)


class PageHandler(BaseHandler):

    def get(self, id):
        results = self.db.query("SELECT COUNT(*) As code FROM entries")
        count = results[0].code
        pages = (count - 1) / NAVNUM + 1
        offset = (int(id) - 1) * NAVNUM
        entries = self.db.query("""
            SELECT * FROM entries ORDER BY published DESC LIMIT 8 OFFSET %s
            """, offset)
        self.render("page.html", entries=entries, pages = pages, this=int(id),
            counts=count)


class EntryHandler(BaseHandler):
    
    def get(self, slug):
        entry = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        if not entry:
            raise tornado.web.HTTPError(404)
        self.render("entry.html", entry=entry)


class FeedHandler(BaseHandler):
    
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY published "
                                "DESC LIMIT 10")
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", entries=entries)


class ComposeHandler(BaseHandler):
    
    def get(self):
        self.render("compose.html")

    def post(self):
        #id = self.get_argument("id", None)
        title = xhtml_escape(self.get_argument("title"))
        tep = self.get_argument("info")
        code = xhtml_escape(self.get_argument("code"))
        pswd = self.get_argument("password")

        # 添加了一个丑陋的验证机制，预防无脑的机器发布垃圾信息
        check = self.get_argument("check", None)
        if check != "1984":
            self.redirect("/newcode")
            return

        info = md.convert(tep)
        password = hexuserpass(pswd)
        slug = "zzzzzzzz"  # 丑陋的一笔
        self.db.execute("""
            INSERT INTO entries (password,title,slug,code,info,markdown,
            published) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, password, title, slug, code, info, tep, datetime.datetime.now())
        e = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        eid = e.id
        slug = eid
        self.db.execute("UPDATE entries SET slug = %s WHERE id = %s", slug, int(eid))
        self.redirect("/" + str(slug))


class DeleteHandler(BaseHandler):

    def post(self):
        password = self.get_argument("password")
        id = self.get_argument("id")
        e = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
        
        if checkuserpass(password, e["password"]):
            self.db.execute("DELETE FROM entries WHERE id=%s", int(id))
            self.redirect("/")
        else:
            self.redirect("/" + str(id))


class UserLoginHandler(BaseHandler):
    
    def post(self):
        password = self.get_argument("password")
        id = self.get_argument("id")
        e = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
        if checkuserpass(password, e["password"]):
            self.set_secure_cookie("codeid", str(id))
            self.redirect("/update/" + str(id))
        else:
            self.redirect("/" + str(id))
    
    
class UpdateHandler(BaseHandler):
    
    def get(self, codeid):
        id = self.get_secure_cookie("codeid")
        if str(codeid) == str(id):
            code = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
            self.render("update.html", code=code)
        else:
            self.redirect("/" + str(codeid))
            
    def post(self, codeid):
        title = xhtml_escape(self.get_argument("title"))
        tep = self.get_argument("info")
        code = xhtml_escape(self.get_argument("code"))
        pswd = self.get_argument("password")
        info = md.convert(tep)
        codes = self.db.get("SELECT * FROM entries WHERE id = %s", int(codeid))
        if checkuserpass(pswd, codes["password"]):
            self.db.execute("""
                UPDATE entries SET title = %s, info = %s, code = %s, markdown = %s
                WHERE id = %s""", title, info, code, tep,  int(codeid))
            self.clear_cookie("codeid")
            self.redirect("/" + str(codeid))
        else:
            self.redirect("/" + str(codeid))
