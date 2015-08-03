__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from HTMLParser import HTMLParser

# constants for html parsing
TAG_FORM = 'form'
TAG_INPUT = 'input'

KEY_ACTION = 'action'
KEY_TYPE = 'type'
KEY_NAME = 'name'
KEY_VALUE = 'value'

VALUE_HIDDEN = 'hidden'

class CASFormHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.action = None
        self.hidden_data = {}

    def handle_starttag(self, tag, attrs):
        if tag == TAG_FORM:
            for key, value in attrs:
                if key == KEY_ACTION:
                    self.action = value
                    break
        elif tag == TAG_INPUT:
            is_hidden = False
            for key, value in attrs:
                if key == KEY_TYPE and value == VALUE_HIDDEN:
                    is_hidden = True
                    break
            if is_hidden:
                form_name = None
                form_value = None
                for key, value in attrs:
                    if key == KEY_NAME:
                        form_name = value
                    elif key == KEY_VALUE:
                        form_value = value
                self.hidden_data[form_name] = form_value