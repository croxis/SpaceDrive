# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1000, 632)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 632))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 632))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(63, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 52, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(28, 28, 28))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(63, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 52, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(28, 28, 28))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(63, 63, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 52, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(28, 28, 28))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(21, 21, 21))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        MainWindow.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/res/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, -4, 1000, 80))
        self.label.setMinimumSize(QtCore.QSize(0, 65))
        self.label.setMaximumSize(QtCore.QSize(1001, 80))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/res/res/daytime_editor_logo.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.settings_tree = QtGui.QTreeWidget(self.centralwidget)
        self.settings_tree.setGeometry(QtCore.QRect(10, 120, 301, 491))
        self.settings_tree.setStyleSheet(_fromUtf8("QTreeView {\n"
"    background: #333;\n"
"    border: 0;\n"
"    color: #eee;\n"
"}\n"
"\n"
"QTreeView::item {\n"
"    background: #444;\n"
"    padding: 4px 3px;\n"
"    outline: 0 !important;\n"
"    margin-bottom: 3px;\n"
"    border-top: 1px solid rgba(255, 255, 255, 40);\n"
"    border-bottom: 1px solid  rgba(0, 0, 0, 90);\n"
"    border-radius: 1px;\n"
"    outline: none;\n"
"\n"
"}\n"
"\n"
"QTreeView::item:hover {\n"
"background: #494949;\n"
"}\n"
"\n"
"QTreeView::item:selected {\n"
"background: #2c6893;\n"
"border-top: 1px solid #3680b4;\n"
"border-bottom: 1px solid #25577a;\n"
"outline: none !important;\n"
"color: #eee;\n"
"}\n"
"\n"
"* {\n"
"outline: 0;\n"
"}\n"
"\n"
""))
        self.settings_tree.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.settings_tree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.settings_tree.setProperty("showDropIndicator", False)
        self.settings_tree.setAlternatingRowColors(False)
        self.settings_tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.settings_tree.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.settings_tree.setIndentation(18)
        self.settings_tree.setRootIsDecorated(True)
        self.settings_tree.setUniformRowHeights(False)
        self.settings_tree.setItemsExpandable(True)
        self.settings_tree.setAnimated(True)
        self.settings_tree.setAllColumnsShowFocus(False)
        self.settings_tree.setWordWrap(True)
        self.settings_tree.setHeaderHidden(True)
        self.settings_tree.setObjectName(_fromUtf8("settings_tree"))
        item_0 = QtGui.QTreeWidgetItem(self.settings_tree)
        item_0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsTristate)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        item_0 = QtGui.QTreeWidgetItem(self.settings_tree)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.settings_tree.header().setVisible(False)
        self.settings_tree.header().setCascadingSectionResizes(False)
        self.settings_tree.header().setDefaultSectionSize(200)
        self.frame_current_setting = QtGui.QFrame(self.centralwidget)
        self.frame_current_setting.setGeometry(QtCore.QRect(370, 80, 621, 551))
        self.frame_current_setting.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_current_setting.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_current_setting.setObjectName(_fromUtf8("frame_current_setting"))
        self.lbl_current_setting = QtGui.QLabel(self.frame_current_setting)
        self.lbl_current_setting.setGeometry(QtCore.QRect(0, 20, 221, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setKerning(True)
        self.lbl_current_setting.setFont(font)
        self.lbl_current_setting.setStyleSheet(_fromUtf8("color: #eee;"))
        self.lbl_current_setting.setObjectName(_fromUtf8("lbl_current_setting"))
        self.btn_reset = QtGui.QPushButton(self.frame_current_setting)
        self.btn_reset.setGeometry(QtCore.QRect(500, 20, 101, 31))
        self.btn_reset.setStyleSheet(_fromUtf8("background: #444; border: 0; color: #eee;\n"
"border-radius: 1px;\n"
"border-top: 1px solid #555;\n"
"border-bottom: 1px solid #222;"))
        self.btn_reset.setObjectName(_fromUtf8("btn_reset"))
        self.frame_3 = QtGui.QFrame(self.frame_current_setting)
        self.frame_3.setGeometry(QtCore.QRect(0, 94, 601, 441))
        self.frame_3.setStyleSheet(_fromUtf8("QFrame {\n"
"background: #eee;border: 1px solid #000;\n"
"}"))
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.verticalLayoutWidget = QtGui.QWidget(self.frame_3)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 591, 441))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.prefab_edit_widget = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.prefab_edit_widget.setSpacing(0)
        self.prefab_edit_widget.setObjectName(_fromUtf8("prefab_edit_widget"))
        self.lbl_setting_desc = QtGui.QLabel(self.frame_current_setting)
        self.lbl_setting_desc.setGeometry(QtCore.QRect(0, 60, 351, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lbl_setting_desc.setFont(font)
        self.lbl_setting_desc.setStyleSheet(_fromUtf8("color: #888;"))
        self.lbl_setting_desc.setWordWrap(True)
        self.lbl_setting_desc.setObjectName(_fromUtf8("lbl_setting_desc"))
        self.btn_insert_point = QtGui.QPushButton(self.frame_current_setting)
        self.btn_insert_point.setGeometry(QtCore.QRect(360, 20, 131, 31))
        self.btn_insert_point.setStyleSheet(_fromUtf8("background: #444; border: 0; color: #eee;\n"
"border-radius: 1px;\n"
"border-top: 1px solid #555;\n"
"border-bottom: 1px solid #222;"))
        self.btn_insert_point.setObjectName(_fromUtf8("btn_insert_point"))
        self.frame_2 = QtGui.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(0, 55, 340, 581))
        self.frame_2.setStyleSheet(_fromUtf8("background: #333;"))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(20, 30, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setKerning(True)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(_fromUtf8("color: #888; border: 0;"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.frame_4 = QtGui.QFrame(self.centralwidget)
        self.frame_4.setGeometry(QtCore.QRect(370, 20, 601, 51))
        self.frame_4.setStyleSheet(_fromUtf8("QFrame {\n"
"    background: #3a3a3a;\n"
"    border-radius: 1px;\n"
"    border-top: 1px solid #555;\n"
"    border-bottom: 1px solid #232323;\n"
"}\n"
"QLabel {border: 0;}"))
        self.frame_4.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_4.setObjectName(_fromUtf8("frame_4"))
        self.time_slider = QtGui.QSlider(self.frame_4)
        self.time_slider.setGeometry(QtCore.QRect(70, 16, 521, 31))
        self.time_slider.setMaximum(5184000)
        self.time_slider.setSingleStep(3600)
        self.time_slider.setPageStep(3600)
        self.time_slider.setProperty("value", 2592000)
        self.time_slider.setTracking(True)
        self.time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_slider.setInvertedAppearance(False)
        self.time_slider.setInvertedControls(False)
        self.time_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.time_slider.setTickInterval(432000)
        self.time_slider.setObjectName(_fromUtf8("time_slider"))
        self.time_label = QtGui.QLabel(self.frame_4)
        self.time_label.setGeometry(QtCore.QRect(9, 12, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.time_label.setFont(font)
        self.time_label.setStyleSheet(_fromUtf8("color: #eee;"))
        self.time_label.setObjectName(_fromUtf8("time_label"))
        self.lbl_select_setting = QtGui.QLabel(self.centralwidget)
        self.lbl_select_setting.setGeometry(QtCore.QRect(480, 370, 421, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl_select_setting.setFont(font)
        self.lbl_select_setting.setStyleSheet(_fromUtf8("color: #eee;"))
        self.lbl_select_setting.setObjectName(_fromUtf8("lbl_select_setting"))
        self.frame_2.raise_()
        self.label.raise_()
        self.settings_tree.raise_()
        self.frame_current_setting.raise_()
        self.frame_4.raise_()
        self.lbl_select_setting.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Day Time Editor", None))
        self.settings_tree.headerItem().setText(0, _translate("MainWindow", "Setting", None))
        self.settings_tree.headerItem().setText(1, _translate("MainWindow", "Value", None))
        __sortingEnabled = self.settings_tree.isSortingEnabled()
        self.settings_tree.setSortingEnabled(False)
        self.settings_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Ambient Occlusion", None))
        self.settings_tree.topLevelItem(0).child(0).setText(0, _translate("MainWindow", "Occlusion Strength", None))
        self.settings_tree.topLevelItem(0).child(0).setText(1, _translate("MainWindow", "0.5", None))
        self.settings_tree.topLevelItem(1).setText(0, _translate("MainWindow", "Scattering", None))
        self.settings_tree.topLevelItem(1).child(0).setText(0, _translate("MainWindow", "Sun Height", None))
        self.settings_tree.topLevelItem(1).child(0).setText(1, _translate("MainWindow", "0,4", None))
        self.settings_tree.topLevelItem(1).child(1).setText(0, _translate("MainWindow", "Sun Angle", None))
        self.settings_tree.topLevelItem(1).child(1).setText(1, _translate("MainWindow", "180 °", None))
        self.settings_tree.topLevelItem(1).child(2).setText(0, _translate("MainWindow", "Sun Color", None))
        self.settings_tree.topLevelItem(1).child(2).setText(1, _translate("MainWindow", "[128, 255, 100]", None))
        self.settings_tree.setSortingEnabled(__sortingEnabled)
        self.lbl_current_setting.setText(_translate("MainWindow", "Occlusion Strength", None))
        self.btn_reset.setText(_translate("MainWindow", "Reset to Default", None))
        self.lbl_setting_desc.setText(_translate("MainWindow", "Description: Some Description about the setting, to give the user a rough idea what this does ", None))
        self.btn_insert_point.setText(_translate("MainWindow", "Insert point from data", None))
        self.label_2.setText(_translate("MainWindow", "Settings", None))
        self.time_label.setText(_translate("MainWindow", "11:15", None))
        self.lbl_select_setting.setText(_translate("MainWindow", "Select a setting on the left to modify its value", None))

from . import resources_rc