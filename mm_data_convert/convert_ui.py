#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'yangzhuo'


from PySide.QtCore import *
from PySide.QtGui import *
from convert_center import *
from config import *
from tool_button import MBrowserButton


class MFileWidget(QWidget):
    sig_file_changed = Signal(str)

    def __init__(
            self,
            title='File',
            file_filter='All Files(*)',
            action='get',
            parent=None):
        super(MFileWidget, self).__init__(parent)
        self.dialog_title = title
        self.file_filter = file_filter
        self.action = action
        self.start_path = ''
        self.line_edit = QLineEdit('')
        self.line_edit.returnPressed.connect(self.slot_enter)

        file_button = MBrowserButton(size=18)
        file_button.clicked.connect(self.slot_open_dialog)
        main_lay = QHBoxLayout()
        main_lay.addWidget(self.line_edit)
        main_lay.addWidget(file_button)
        main_lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_lay)

    @Slot()
    def slot_open_dialog(self):
        args = (self, self.dialog_title, self.start_path, self.file_filter)
        r_file, _ = QFileDialog.getOpenFileName(*args) \
            if self.action == 'get' else QFileDialog.getSaveFileName(*args)
        if r_file != '':
            self.slot_file_changed(r_file)

    def set_dialog_title(self, title):
        self.dialog_title = title

    def set_filter_list(self, filter_list):
        if filter_list:
            self.file_filter = 'File({})'.format(
                ' '.join(['*' + e for e in filter_list]))

    def set_start_path(self, path):
        self.start_path = path

    @Slot()
    def slot_clear(self):
        self.line_edit.setText('')

    @Slot()
    def slot_enter(self):
        text = self.line_edit.text()
        self.set_start_path(text)
        self.sig_file_changed.emit(text)

    def get_data(self):
        return self.line_edit.text()

    def set_data(self, file_obj):
        self.set_start_path(file_obj)
        self.line_edit.setText(file_obj)

    def slot_file_changed(self, text):
        self.set_start_path(text)
        self.line_edit.setText(text)
        self.sig_file_changed.emit(text)


class MSelectOption(QToolButton):
    def __init__(self, parent=None):
        super(MSelectOption, self).__init__(parent)
        self.setObjectName('selectOption')
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setFixedSize(QSize(70, 20))
        self.setIconSize(QSize(20, 20))


class MSelectWidget(QWidget):
    def __init__(self, parent=None):
        super(MSelectWidget, self).__init__(parent)
        self.flatten = False
        self.button_grp = QButtonGroup()
        self.button_grp.setExclusive(True)
        self.main_lay = QGridLayout()
        self.main_lay.setSpacing(20)
        self.setLayout(self.main_lay)

    def set_exclusive(self, flag):
        self.button_grp.setExclusive(flag)

    def set_flatten(self, flag):
        self.flatten = flag

    def set_text_list(self, data_list):
        total = len(data_list)
        if self.flatten:
            max_column = 200
        else:
            max_column = 2 if total == 4 else 3

        for index, data in enumerate(data_list):
            button = MSelectOption()
            button.setText(data['name'])
            setattr(button, 'data', data)
            if 'icon' in data.keys():
                button.setIcon(QIcon(data['icon']))
            self.button_grp.addButton(button)
            self.main_lay.addWidget(
                button, index / max_column, index %
                max_column)

    def get_checked_button(self):
        self.button_grp.checkedButton()

    def get_checked_text(self):
        but = self.button_grp.checkedButton()
        return but.text() if but else None

    def get_checked_data(self):
        but = self.button_grp.checkedButton()
        return getattr(but, 'data', None)

    def set_checked_text(self, text):
        for but in self.button_grp.buttons():
            if but.text() == text:
                but.setChecked(True)
                return


class MQComboBox(QWidget):
    def __init__(self):
        super(MQComboBox, self).__init__()
        self.com_box = QComboBox()
        self.com_box.addItems(RESOLUTION_LIST)
        self.com_box.setCurrentIndex(6)
        self.com_box.currentIndexChanged.connect(
            self.set_value
        )
        self.width, self.height = QLineEdit(), QLineEdit()
        self.width.setValidator(QRegExpValidator(QRegExp(r"[0-9\-]+"), self))
        self.height.setValidator(QRegExpValidator(QRegExp(r"[0-9\-]+"), self))
        lay = QHBoxLayout()
        lay.addWidget(self.width)
        lay.addWidget(self.height)
        lay.addWidget(self.com_box)

        self.setLayout(lay)

    def set_value(self):
        compile_ = re.compile(r'(\d*) x (\d*)')
        result = re.findall(compile_,
                            RESOLUTION_LIST[self.com_box.currentIndex()])
        if result:
            width, height = result[0]
            self.width.setText(width)
            self.height.setText(height)

    def get_data(self):
        return float(self.width.text()), float(self.height.text())


class CovertDialog(QWidget):
    def __init__(self):
        super(CovertDialog, self).__init__()
        self.load_soft, self.save_soft = MSelectWidget(), MSelectWidget()
        self.resolution = MQComboBox()
        run_btn = QPushButton('Run', clicked=self.run)
        self.load_soft.set_text_list(SOFTWARE_BUTTON_DATA)
        self.save_soft.set_text_list(SOFTWARE_BUTTON_DATA)

        self.load_wgt = MFileWidget(file_filter="*.txt", action='get')
        self.save_wgt = MFileWidget(file_filter="*.txt", action='save')

        main_lay = QFormLayout()
        main_lay.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        main_lay.addRow(QLabel(self.tr('Load File:')), self.load_wgt)
        main_lay.addRow(QLabel(self.tr('Save File:')), self.save_wgt)
        main_lay.addRow(QLabel(self.tr('Choose Resolution:')), self.resolution)
        main_lay.addRow(QLabel(self.tr('Load SoftWare:')), self.load_soft)
        main_lay.addRow(QLabel(self.tr('Save SoftWare:')), self.save_soft)
        main_lay.addRow(run_btn)

        self.setLayout(main_lay)

    def run(self):
        load_file_path, save_file_path = self.load_wgt.get_data(), self.save_wgt.get_data()
        width, height = self.resolution.get_data()
        load_soft = self.load_soft.get_checked_data()
        save_soft = self.save_soft.get_checked_data()
        msg = QMessageBox()
        if (load_file_path and save_file_path) and (
                width and height) and (load_soft, save_soft):
            instance_load = eval(load_soft.get('data', None))()
            instance_save = eval(save_soft.get('data', None))()
            load_data = instance_load.load(load_file_path, width, height)
            instance_save.data = load_data
            instance_save.save(save_file_path, width, height)
            os.startfile(os.path.dirname(save_file_path))
            msg.setText(u"Nice! 数据转换成功!")
        else:
            msg.setText(u"您有的数据填写为空,请详细填写.")
        msg.exec_()
        return False


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main = CovertDialog()
    main.show()
    app.exec_()
