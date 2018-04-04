#!/usr/bin/env python

import os
import jinja2
import webapp2

from models import Message

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):#mostrarformulario
    def get(self):
        return self.render_template("hello.html")


class ResultHandler(BaseHandler):#peticionyenvio
    def post(self):
        n = self.request.get("some_name")
        e = self.request.get("some_email")
        t = self.request.get("some_text")

        if not n:
            n = "blank"
        if not e:
            e = "blank"

        msg = Message(name=n, email=e, text=t)#no poner created aqui, ya esta generado
        msg.put()

        return self.redirect_to("entries")#a la url, le damos un nombre entries mas abajo

class EntriesHandler(BaseHandler):#mostrar entradas
    def get(self):
        all_entries = Message.query().fetch()
        params = {"everything": all_entries}
        return self.render_template("entries.html", params=params)

class EntryDetailsHandler(BaseHandler):#mostrar una entrada
    def get(self, message_id):
        entry_message = Message.get_by_id(int(message_id))
        params = {"message": entry_message}
        return self.render_template("entry_details.html", params=params)


class EditMessageHandler(BaseHandler):#editarentradas
    def get(self, message_id):
        existing_message = Message.get_by_id(int(message_id))
        params = {"message": existing_message}
        return self.render_template("entries_edit.html", params=params)

    def post(self, message_id):
        new_text = self.request.get("some_text")
        message = Message.get_by_id(int(message_id))
        message.text = new_text
        message.put()
        return self.redirect_to("singleentry")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/result', ResultHandler),
    webapp2.Route('/entries', EntriesHandler),#para poner la url arriba, escribir redirect en vez de redirect to
    webapp2.Route('/single-entry/<message_id:\d+>', EntryDetailsHandler, name = "singleentry"),
    webapp2.Route('/single-entry/<message_id:\d+>/edit', EditMessageHandler),
], debug=True)
