# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\VSCode_Project\python_project\fuzzProject\dialog_selectTarget.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets

import public


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(332, 394)
        Dialog.setModal(False)
        self.funcTableWidget = QtWidgets.QTableWidget(Dialog)
        self.funcTableWidget.setGeometry(QtCore.QRect(30, 30, 295, 291))
        self.funcTableWidget.setObjectName("funcTableWidget")
        self.funcTableWidget.setColumnCount(2)
        self.funcTableWidget.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.funcTableWidget.setVerticalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.funcTableWidget.setVerticalHeaderItem(1, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.funcTableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.funcTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.funcTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.funcTableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignVCenter)
        self.funcTableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.funcTableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.funcTableWidget.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.funcTableWidget.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.funcTableWidget.setItem(2, 1, item)
        self.unselectAllBtn = QtWidgets.QPushButton(Dialog)
        self.unselectAllBtn.setGeometry(QtCore.QRect(180, 340, 93, 31))
        self.unselectAllBtn.setObjectName("unselectAllBtn")
        self.selectAllBtn = QtWidgets.QPushButton(Dialog)
        self.selectAllBtn.setGeometry(QtCore.QRect(70, 340, 93, 31))
        self.selectAllBtn.setObjectName("selectAllBtn")

        # 手写
        # self.setValues("ui","C:\\Users\\Radon\\Desktop\\fuzztest\\main.c")
        self.selectAllBtn.clicked.connect(self.selectAll)
        self.unselectAllBtn.clicked.connect(self.unselectAll)
        # 结束

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "选择目标"))
        item = self.funcTableWidget.verticalHeaderItem(0)
        item.setText(_translate("Dialog", "1"))
        # item = self.funcTableWidget.verticalHeaderItem(1)
        # item.setText(_translate("Dialog", "2"))
        # item = self.funcTableWidget.verticalHeaderItem(2)
        # item.setText(_translate("Dialog", "3"))
        item = self.funcTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "函数名称"))
        item = self.funcTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "目标"))
        __sortingEnabled = self.funcTableWidget.isSortingEnabled()
        self.funcTableWidget.setSortingEnabled(False)
        # item = self.funcTableWidget.item(0, 0)
        # item.setText(_translate("Dialog", "main"))
        # item = self.funcTableWidget.item(1, 0)
        # item.setText(_translate("Dialog", "test1"))
        # item = self.funcTableWidget.item(2, 0)
        # item.setText(_translate("Dialog", "test6"))
        self.funcTableWidget.setSortingEnabled(__sortingEnabled)
        self.unselectAllBtn.setText(_translate("Dialog", "全不选"))
        self.selectAllBtn.setText(_translate("Dialog", "全选"))

    # 手写
    def setValues(self, ui, source_loc, SAResult):
        '''
        @description: 设置一些初始值
        @param {*} self
        @param {*} ui Ui_window的ui
        @param {*} source_loc 字符串，其中存储了所有的源文件地址，用\n隔开
        @param {*} SAResult 列表，静态分析的结果，其中存储了哪些函数可能存在缺陷
        @return {*}
        '''
        if len(SAResult) == 0:
            self.funcList = public.getAllFunctions(source_loc)
        else:
            self.funcList = SAResult
        self.funcTableWidget.setRowCount(len(self.funcList))
        self.ui = ui
        self.targetSet = []

        s_cbx = "{"
        s_lab = "{"
        for i in range(len(self.funcList)):
            s_cbx += str(i) + ":QtWidgets.QCheckBox(),"
            s_lab += str(i) + ":QtWidgets.QLabel(),"
        s_cbx += "}"
        s_lab += "}"
        self.checkboxs = eval(s_cbx)
        self.labels = eval(s_lab)
        print(self.funcList)
        for i in range(len(self.funcList)):
            hLayout = QtWidgets.QHBoxLayout()
            hLayout.addWidget(self.checkboxs[i])
            hLayout.setAlignment(self.checkboxs[i], QtCore.Qt.AlignCenter)
            widget = QtWidgets.QWidget()
            widget.setLayout(hLayout)
            self.funcTableWidget.setCellWidget(i, 1, widget)
            self.funcTableWidget.setRowHeight(i, 40)
            self.labels[i].setText(self.funcList[i])
            hLayout2 = QtWidgets.QHBoxLayout()
            hLayout2.addWidget(self.labels[i])
            hLayout2.setAlignment(self.labels[i], QtCore.Qt.AlignCenter)
            widget2 = QtWidgets.QWidget()
            widget2.setLayout(hLayout2)
            self.funcTableWidget.setCellWidget(i, 0, widget2)
            self.checkboxs[i].clicked.connect(lambda x, i=i: self.selectTarget(self.checkboxs[i], self.funcList[i]))

    def selectTarget(self, checkbox, label):
        '''
        @description: 选择目标
        @param {*} self
        @param {*} checkbox 用户所点击的checkbox
        @param {*} label 用户点击的checkbox所对应的label
        @return {*}
        '''
        self.ui.targetSetInfo.clear()
        if checkbox.isChecked():
            print("选中了" + label)
            self.targetSet.append(label)
        else:
            print("取消了" + label)
            if label in self.targetSet:
                self.targetSet.remove(label)
        self.targetSet = sorted(set(self.targetSet))
        for i in range(len(self.targetSet)):
            self.ui.targetSetInfo.append(self.targetSet[i])

    def selectAll(self):
        '''
        @description: 选择所有目标
        @param {*} self
        @return {*}
        '''
        for i in range(len(self.funcList)):
            self.checkboxs[i].setChecked(True)
            self.selectTarget(self.checkboxs[i], self.funcList[i])

    def unselectAll(self):
        '''
        @description: 将所有目标设置为未选中
        @param {*} self
        @return {*}
        '''
        for i in range(len(self.funcList)):
            self.checkboxs[i].setChecked(False)
            self.selectTarget(self.checkboxs[i], self.funcList[i])
    # 结束


import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
