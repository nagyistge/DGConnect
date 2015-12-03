# -*- coding: utf-8 -*-
from qgis.core import QgsMessageLog
from string import Template
from PyQt4.QtCore import Qt, QEvent
from PyQt4.QtGui import QLineEdit, QPalette


EXAMPLE_STYLE_SHEET = "color: rgb(120, 120, 120);"

class ExampleLineEdit(QLineEdit):

    def __init__(self, example_text=""):
        super(ExampleLineEdit, self).__init__()
        self.example_text = example_text
        self.example_text_set = False
        self.set_to_example_text()
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        current_text = self.displayText()
        if event.type() == QEvent.FocusIn and self.example_text_set:
            self.reset_text()
        elif event.type() == QEvent.FocusOut and not current_text:
            self.set_to_example_text()
        return False

    def text(self):
        if self.example_text_set:
            return ""
        else:
            return super(ExampleLineEdit, self).text()

    def reset_text(self):
        self.setStyleSheet(None)
        self.setText("")
        self.example_text_set = False

    def set_to_example_text(self):
        self.setStyleSheet(EXAMPLE_STYLE_SHEET)
        self.setText(self.example_text)
        self.example_text_set = True
