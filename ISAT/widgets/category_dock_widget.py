# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5 import QtWidgets, QtCore, QtGui
from ISAT.ui.category_dock import Ui_Form, Ui_Form_action
from fuzzywuzzy import process


class CategoriesDockWidget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, mainwindow):
        super(CategoriesDockWidget, self).__init__()
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.pushButton_category_setting.clicked.connect(self.mainwindow.category_setting)
        self.listWidget.itemClicked.connect(self.item_choice)
        self.lineEdit_search_category.textChanged.connect(self.update_widget)
        self.lineEdit_search_category.setClearButtonEnabled(True)

        # 新增 手动/自动 group 选择
        self.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))
        self.lineEdit_currentGroup.textChanged.connect(self.update_current_group)
        self.pushButton_increase.clicked.connect(self.increase_current_group)
        self.pushButton_decrease.clicked.connect(self.decrease_current_group)
        self.pushButton_group_mode.clicked.connect(self.toggle_group_mode)

        self.category_choice_shortcuts = {}
        for i in range(10):
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("{}".format(i)), self)
            shortcut.activated.connect(self.choice_category)
            self.category_choice_shortcuts[shortcut] = i - 1 if i != 0 else 9

    def choice_category(self):
        index = self.category_choice_shortcuts.get(self.sender(), 0)
        try:
            item = self.listWidget.item(index)
            widget = self.listWidget.itemWidget(item)
            label_radio = widget.findChild(QtWidgets.QRadioButton, 'label_radio')
            label_radio.setChecked(True)
        except:
            pass

    def update_widget(self):
        self.listWidget.clear()
        btngroup = QtWidgets.QButtonGroup(self)
        labels = self.mainwindow.cfg.get('label', [])
        search_text = self.lineEdit_search_category.text()

        name_label_dict = {label.get('name', 'UNKNOW'): label for label in labels}

        label_names = [label.get('name', 'UNKNOW') for label in labels]
        if search_text == '':
            show_label_names = label_names
        elif search_text.strip(' ') == '':
            show_label_names = label_names
        else:
            matches = process.extract(search_text, label_names, limit=5)
            show_label_names = [name for name, score in matches if score > 0]

        for index in range(len(show_label_names)):
            label = name_label_dict[show_label_names[index]]
            name = label.get('name', 'UNKNOW')
            color = label.get('color', '#000000')
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(200, 30))
            widget = QtWidgets.QWidget()

            layout = QtWidgets.QHBoxLayout()
            layout.setContentsMargins(9, 1, 9, 1)

            label_color = QtWidgets.QLabel()
            label_color.setFixedWidth(10)
            label_color.setStyleSheet("background-color: {};".format(color))
            label_color.setObjectName('label_color')

            label_radio = QtWidgets.QRadioButton('{}'.format(name))
            label_radio.setObjectName('label_radio')
            label_radio.toggled.connect(self.radio_choice)
            btngroup.addButton(label_radio)
            if name == '__background__':
                label_radio.setChecked(True)

            layout.addWidget(label_color)
            layout.addWidget(label_radio)
            widget.setLayout(layout)

            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def radio_choice(self):
        if isinstance(self.sender(), QtWidgets.QRadioButton):
            if self.sender().isChecked():
                self.mainwindow.current_category = self.sender().text()

    def item_choice(self, item_now):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            widget = self.listWidget.itemWidget(item)
            label_radio = widget.findChild(QtWidgets.QRadioButton, 'label_radio')
            label_radio.setChecked(item == item_now)

    def update_current_group(self, text):
        # Update the current_group variable when the text in the QLineEdit changes
        try:
            self.mainwindow.current_group = int(text)
        except ValueError:
            pass

    def increase_current_group(self):
        # Increase the current_group variable and update the QLineEdit text
        self.mainwindow.current_group += 1
        self.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))

    def decrease_current_group(self):
        # Decrease the current_group variable and update the QLineEdit text
        if self.mainwindow.current_group > 1:
            self.mainwindow.current_group -= 1
            self.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))

    def toggle_group_mode(self):
        _translate = QtCore.QCoreApplication.translate
        if self.mainwindow.group_select_mode == 'auto':
            self.mainwindow.group_select_mode = 'manual'
            self.pushButton_group_mode.setText("Manual")
            self.pushButton_group_mode.setStatusTip(_translate("MainWindow", "Manual set group id."))
        elif self.mainwindow.group_select_mode == 'manual':
            self.mainwindow.group_select_mode = 'track'
            self.pushButton_group_mode.setText("Track")
            self.pushButton_group_mode.setStatusTip(_translate("MainWindow",
                                                               "Group id changed with the group of current polygons when use [TAB] or [`] to check."))
        elif self.mainwindow.group_select_mode == 'track':
            self.mainwindow.group_select_mode = 'auto'
            self.pushButton_group_mode.setText("Auto")
            self.pushButton_group_mode.setStatusTip(
                _translate("MainWindow", "Group id auto add 1 when add a new polygon."))


# todo 0523对应分类，创建动作场景选择
class ActionsDockWidget(QtWidgets.QWidget, Ui_Form_action):
    def __init__(self, mainwindow):
        super(ActionsDockWidget, self).__init__()
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.pushButton_action_setting.clicked.connect(self.mainwindow.action_setting)  # TODO 待更新
        self.listWidget.itemClicked.connect(self.item_choice)
        self.lineEdit_search_action.textChanged.connect(self.update_widget)
        self.lineEdit_search_action.setClearButtonEnabled(True)

        # 新增 手动/自动 group 选择
        self.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))
        self.lineEdit_currentGroup.textChanged.connect(self.update_current_group)
        self.pushButton_increase.clicked.connect(self.increase_current_group)
        self.pushButton_decrease.clicked.connect(self.decrease_current_group)
        self.pushButton_group_mode.clicked.connect(self.toggle_group_mode)

        self.action_choice_shortcuts = {}
        for i in range(10):
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("{}".format(i)), self)
            shortcut.activated.connect(self.choice_action)
            self.action_choice_shortcuts[shortcut] = i - 1 if i != 0 else 9

    def choice_action(self):
        index = self.action_choice_shortcuts.get(self.sender(), 0)
        try:
            item = self.listWidget.item(index)
            widget = self.listWidget.itemWidget(item)
            label_radio = widget.findChild(QtWidgets.QRadioButton, 'label_radio')
            label_radio.setChecked(True)
        except:
            pass

    def update_widget(self):
        self.listWidget.clear()
        btngroup = QtWidgets.QButtonGroup(self)
        labels = self.mainwindow.cfg.get('action', [])  # TODO 这里新添一个加载isat.yaml文件，但不是加载类别，而是加载动作
        search_text = self.lineEdit_search_action.text()

        name_label_dict = {label.get('name', 'UNKNOW'): label for label in labels}

        label_names = [label.get('name', 'UNKNOW') for label in labels]
        if search_text == '':
            show_label_names = label_names
        elif search_text.strip(' ') == '':
            show_label_names = label_names
        else:
            matches = process.extract(search_text, label_names, limit=5)
            show_label_names = [name for name, score in matches if score > 0]

        for index in range(len(show_label_names)):
            label = name_label_dict[show_label_names[index]]
            name = label.get('name', 'UNKNOW')
            color = label.get('color', '#000000')
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(200, 30))
            widget = QtWidgets.QWidget()

            layout = QtWidgets.QHBoxLayout()
            layout.setContentsMargins(9, 1, 9, 1)

            label_color = QtWidgets.QLabel()
            label_color.setFixedWidth(10)
            label_color.setStyleSheet("background-color: {};".format(color))
            label_color.setObjectName('label_color')

            label_radio = QtWidgets.QRadioButton('{}'.format(name))
            label_radio.setObjectName('label_radio')
            label_radio.toggled.connect(self.radio_choice)
            btngroup.addButton(label_radio)
            if name == '__background__':
                label_radio.setChecked(True)

            layout.addWidget(label_color)
            layout.addWidget(label_radio)
            widget.setLayout(layout)

            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def radio_choice(self):
        if isinstance(self.sender(), QtWidgets.QRadioButton):
            if self.sender().isChecked():
                self.mainwindow.current_action = self.sender().text()

    def item_choice(self, item_now):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            widget = self.listWidget.itemWidget(item)
            label_radio = widget.findChild(QtWidgets.QRadioButton, 'label_radio')
            label_radio.setChecked(item == item_now)

    def update_current_group(self, text):
        # Update the current_group variable when the text in the QLineEdit changes
        try:
            self.mainwindow.current_group = int(text)
        except ValueError:
            pass

    def increase_current_group(self):
        # Increase the current_group variable and update the QLineEdit text
        self.mainwindow.current_group += 1
        self.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))

    def decrease_current_group(self):
        # Decrease the current_group variable and update the QLineEdit text
        if self.mainwindow.current_group > 1:
            self.mainwindow.current_group -= 1
            self.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))

    def toggle_group_mode(self):
        _translate = QtCore.QCoreApplication.translate
        if self.mainwindow.group_select_mode == 'auto':
            self.mainwindow.group_select_mode = 'manual'
            self.pushButton_group_mode.setText("Manual")
            self.pushButton_group_mode.setStatusTip(_translate("MainWindow", "Manual set group id."))
        elif self.mainwindow.group_select_mode == 'manual':
            self.mainwindow.group_select_mode = 'track'
            self.pushButton_group_mode.setText("Track")
            self.pushButton_group_mode.setStatusTip(_translate("MainWindow",
                                                               "Group id changed with the group of current polygons when use [TAB] or [`] to check."))
        elif self.mainwindow.group_select_mode == 'track':
            self.mainwindow.group_select_mode = 'auto'
            self.pushButton_group_mode.setText("Auto")
            self.pushButton_group_mode.setStatusTip(
                _translate("MainWindow", "Group id auto add 1 when add a new polygon."))
