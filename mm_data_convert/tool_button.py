#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'yangzhuo'

from PySide.QtCore import *
from PySide.QtGui import *


class MToolButton(QToolButton):
    sig_clicked = Signal(object)
    _toolTip = 'tooltips'
    _toolTip_unchecked = 'tooltips_unchecked'

    def __init__(self, size=24, checkable=False, user_data=None, parent=None):
        super(MToolButton, self).__init__(parent)
        if checkable:
            self.setCheckable(checkable)
            self.toggled.connect(self.slot_check_state_changed)
            self.setChecked(True)
        self.user_data = user_data
        self.clicked.connect(self.slot_clicked)
        self.setToolTip(self._toolTip)
        self.setIcon(QIcon('static/image/icon-browser.png'))
        self.setFixedSize(size + 1, size + 1)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)

    @Slot(bool)
    def slot_check_state_changed(self, checked):
        self.setChecked(checked)
        if checked:
            self.setToolTip(self._toolTip)
        else:
            self.setToolTip(self._toolTip_unchecked)

    @Slot()
    def slot_clicked(self):
        self.sig_clicked.emit(self.user_data)


class MBrowserButton(MToolButton):
    _toolTip = 'browser'
