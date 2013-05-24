import os
import webapp2
from google.appengine.ext import ndb
from webapp2_extras import jinja2

from models_admin import *
import settings


actions_map = {
    "c": "Add",
    "r": "List",
    "u": "Edit",
    "d": "Delete"
}


class BaseHandler(webapp2.RequestHandler):
    """
    Request handler, which knows how to render himself into template.
    """

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)


class AdminHandler(BaseHandler):
    """
    Admin panel main page.
    """
    #@admin_required
    def get(self):
        msg = self.request.GET.get('msg')
        self.render_template("admin_panel.html", **{"msg": msg})


class CrudHandler(BaseHandler):
    """
    Admin CRUD UI.

    Model must have Meta class, e.g.:
    class Model(ndb.Model):
        ...

        class Meta():
            # templates
            # CRUD use '/admin/[model]/' path prefix, model name is lower case
            c = "" # new item template
            r = "" # items list template
            u = "" # edit item template
            d = "" # delete item template

            # sample
            def __init__(self):
                self.fields = [
                    fields.TextField("name", "Name:"),
                    fields.KeyField("site", "Select site:", query=Site.query()),
                    fields.MoneyField("budget", "Budget:", required=True),
                    fields.CheckboxField("is_active", "Active?"),
                    fields.DateField("due_date", "Due date")
                    ...
                ]
            }
    """

    # default template names
    c = "create.html"
    r = "read.html"
    u = "update.html"
    d = "delete.html"

    # Decorator/auth usage for your consideration
    #@admin_required
    def get(self, model, action):
        item = None
        items = None
        items_count = 0
        cursor = self.request.get('cursor')
        next_c = None
        per_page = getattr(settings, "PER_PAGE", 10)
        item_id = self.request.GET.get("id", None)
        msg = self.request.GET.get("msg", None)

        if not model in MODELS:
            raise Exception(
                "Model `%s` not registered in `models_admin.py`" % model
            )

        m = eval(model)

        # model template for given action
        path = "/admin/%s/" % model.lower()
        template = m.Meta.__dict__.get(action, getattr(self, action))
        fields = m.Meta().fields

        # if no template - fallback to default one
        if not os.path.isfile('./templates' + path + template):
            path = "/admin/"

        # item
        if item_id:
            item = m.get_by_id(int(item_id))
            if action == "u":
                for f in fields:
                    f.initial = getattr(item, f.field)

        # list
        if action == "r":
            items = m.query()
            if hasattr(m.Meta(), "order_by"):
                items = items.order(m.Meta().order_by)

            items_count = items.count()

            # -- PAGINATE RESULTS --
            cursor = ndb.Cursor(urlsafe=cursor)
            items, next_curs, more = items.fetch_page(per_page,
                start_cursor=cursor)
            if more:
                next_c = next_curs.urlsafe()
            else:
                next_c = None

        content = {
                   "model": model,
                   "action": actions_map[action],
                   "fields": fields,
                   "item": item,
                   "items": items,
                   "items_count": items_count,
                   "cursor": next_c,
                   "per_page": per_page,
                   "msg": msg
                   }
        self.render_template(path + template, **content)

    # Decorator/auth usage for your consideration
    #@admin_required
    def post(self, model, action):
        item = None
        item_id = self.request.GET.get("id", None)
        data = self.request.POST
        msg = ""

        if not model in MODELS:
            raise Exception(
                "Model `%s` not registered in `models_admin.py`" % model
            )

        m = eval(model)

        # item: Delete or Update
        if item_id:
            item = m.get_by_id(int(item_id))

            if action == "d":
                msg = "%s '%s' has been removed" % (model, item)
                item.key.delete()
            elif action == "u":
                fields = m.Meta().fields
                for f in fields:
                    setattr(item, f.field, f.parse(data.getall(f.field)))
                item.put()
                msg = "%s '%s' saved" % (model, item)
        # Create
        elif action == "c":
            fields = m.Meta().fields
            item = m()
            for f in fields:
                setattr(item, f.field, f.parse(data.getall(f.field)))
            item.put()
            msg = "%s '%s' added" % (model, item)

        self.redirect(self.uri_for('admin_crud', model=model, action="r") \
                      + "?msg=" + msg)
