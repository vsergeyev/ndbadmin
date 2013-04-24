import datetime

from google.appengine.ext import ndb


class Field(object):
    """
    Base field
    """
    def __init__(self, field, label, initial="", required=False):
        super(Field, self).__init__()
        self.field = field
        self.label = label
        self.initial = initial
        self.required = required

    def render(self):
        "Return html input string"
        return '<input type="text" name="%s" value="%s" />' % (
            self.field,
            self.initial
        )

    def parse(self, val):
        "Parse value from request, convert it to DB format"
        # Admin view uses getall(key) for POST data
        # so we have here:
        # a) empty list
        if not val:
            return None
        # b) 1 value
        if len(val) == 1:
            return val[0]
        # c) list of values
        return val


class TextField(Field):
    """
    Input type "text"
    """
    def render(self):
        return '''<label>%s</label>
        <input type="text" name="%s" value="%s" placeholder="%s" %s />''' % (
            self.label,
            self.field,
            self.initial,
            self.label,
            "required" if self.required else ""
        )


class BigTextField(Field):
    """
    Input type "textarea"
    """
    def render(self):
        return '''<label>%s</label>
        <textarea name="%s" placeholder="%s" %s>%s</textarea>''' % (
            self.label,
            self.field,
            self.label,
            "required" if self.required else "",
            self.initial
        )


class CheckboxField(Field):
    """
    Input type "checkbox"
    """
    def render(self):
        return '''<label class="checkbox">
        <input type="checkbox" name="%s" %s %s /> %s</label>''' % (
            self.field,
            "checked" if self.initial else "",
            "required" if self.required else "",
            self.label
        )

    def parse(self, val):
        if not val:
            return False
        return (val[0] == "on")


class CheckboxListField(Field):
    """
    Group of checkboxes
    """
    def __init__(self, field, label, initial="", required=False, query=None):
        super(CheckboxListField, self).__init__(field, label, initial, required)
        self.query = query or []

    def render(self):
        res = "<h3>%s</h3>" % self.label
        row = '''<label class="checkbox">
            <input type="checkbox" name="%s" value="%s" %s %s /> %s</label>'''
        for item in self.query:
            res += row % (
                self.field,
                item.key.urlsafe(),
                "checked" if item.key in self.initial else "",
                "required" if self.required else "",
                item
            )
        return res

    def parse(self, val):
        return [ndb.Key(urlsafe=v) for v in val]
        #return [int(v) for v in val]


class GeoField(TextField):
    """
    Field for geo location
    """
    def parse(self, val):
        if not val or val[0]=="":
            return ndb.GeoPt("0,0")
        return ndb.GeoPt(val[0])


class KeyField(Field):
    """
    Select with a list of objects
    """
    def __init__(self, field, label, initial="", required=False, query=None):
        super(KeyField, self).__init__(field, label, initial, required)
        self.query = query or []

    def render(self):
        res = '''<label>%s</label>
            <select name="%s" %s>
            <option value="" %s>-- %s --</option>''' % (
                self.label,
                self.field,
                "required" if self.required else "",
                'selected="selected"' if not self.initial else "",
                self.label
            )
        row = '<option value="%s" %s>%s</option>'
        for item in self.query:
            res += row % (
                item.key.urlsafe(),
                'selected="selected"' if item.key == self.initial else "",
                item
            )
        return res + "</select>"

    def parse(self, val):
        if not val or val[0]=="":
            return None
        return ndb.Key(urlsafe=val[0])


class ChoiceField(Field):
    """
    Select with a list of strings
    """
    def __init__(self, field, label, initial="", required=False, query=None):
        super(ChoiceField, self).__init__(field, label, initial, required)
        self.query = query or []

    def render(self):
        res = '''<label>%s</label>
            <select name="%s" %s>
            <option value="" %s>-- %s --</option>''' % (
                self.label,
                self.field,
                "required" if self.required else "",
                'selected="selected"' if not self.initial else "",
                self.label
            )
        row = '<option value="%s" %s>%s</option>'
        for item in self.query:
            res += row % (
                item,
                'selected="selected"' if item == self.initial else "",
                item
            )
        return res + "</select>"


class MoneyField(Field):
    """
    Field for displaying money
    $ xxx.xx
    """

    def render(self):
        return '''<div class="input-prepend"><label>%s</label>
        <span class="add-on">$</span>
        <input class="span2" type="text" name="%s" value="%.2f" %s />
        </div>''' % (
            self.label,
            self.field,
            self.initial or 0.0,
            "required" if self.required else ""
        )

    def parse(self, val):
        if not val or val[0]=="":
            return 0.0
        return float(val[0])


class IntegerField(Field):
    """
    Field for displaying integer value
    """

    def render(self):
        return '''<label>%s</label>
        <input class="span2" type="number" name="%s" value="%i" %s />''' % (
            self.label,
            self.field,
            self.initial or 0,
            "required" if self.required else ""
        )

    def parse(self, val):
        if not val or val[0]=="":
            return 0
        return int(val[0])
    

class DateField(Field):
    """
    Input type ""
    """
    def render(self):
        return '''
        <label>%s</label>
        <input type="date" name="%s" value="%s" %s />''' % (
            self.label,
            self.field,
            self.initial,
            "required" if self.required else ""
        )

    def parse(self, val):
        if not val or val[0]=="":
            return None
        return datetime.datetime.strptime(val[0], "%Y-%m-%d")


class TextFileField(Field):
    """
    Input type "file"
    """
    def render(self):
        return '''
        <label>%s</label>
        <input type="file" name="%s" id="id_%s" %s />''' % (
            self.label,
            self.field,
            self.field,
            "required" if self.required else ""
        )

    def parse(self, val):
        if not val or val[0]=="":
            return ""
        return unicode(val[0].file.read(), "Latin-1")