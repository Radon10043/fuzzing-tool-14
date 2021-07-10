# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\VSCode_Project\python_project\fuzzProject\dialog_selectStruct.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import os, re, sys
from PyQt5 import QtCore, QtGui, QtWidgets

import staticAnalysis
import public
import Ui_dialog_seed as seedDialogPY

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(415, 414)
        Dialog.setModal(False)
        self.structTableWidget = QtWidgets.QTableWidget(Dialog)
        self.structTableWidget.setGeometry(QtCore.QRect(30, 30, 361, 291))
        self.structTableWidget.setObjectName("structTableWidget")
        self.structTableWidget.setColumnCount(2)
        self.structTableWidget.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.structTableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.structTableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.structTableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.structTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.structTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        # self.structTableWidget.setItem(0, 0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setTextAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignVCenter)
        # item.setCheckState(QtCore.Qt.Unchecked)
        # self.structTableWidget.setItem(0, 1, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setTextAlignment(QtCore.Qt.AlignCenter)
        # self.structTableWidget.setItem(1, 0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setCheckState(QtCore.Qt.Unchecked)
        # self.structTableWidget.setItem(1, 1, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setTextAlignment(QtCore.Qt.AlignCenter)
        # self.structTableWidget.setItem(2, 0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setCheckState(QtCore.Qt.Unchecked)
        self.structTableWidget.setItem(2, 1, item)
        self.structTableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.structTableWidget.horizontalHeader().setDefaultSectionSize(175)
        self.yesBtn = QtWidgets.QPushButton(Dialog)
        self.yesBtn.setGeometry(QtCore.QRect(90, 340, 221, 51))
        self.yesBtn.setObjectName("yesBtn")

        # =================================手写 =======================================
        self.yesBtn.clicked.connect(self.popSeedDialog)
        self.yesBtn.clicked.connect(Dialog.accept)
        # =============================================================================

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "选择目标"))
        item = self.structTableWidget.verticalHeaderItem(0)
        item.setText(_translate("Dialog", "1"))
        item = self.structTableWidget.verticalHeaderItem(1)
        item.setText(_translate("Dialog", "2"))
        item = self.structTableWidget.verticalHeaderItem(2)
        item.setText(_translate("Dialog", "3"))
        item = self.structTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "结构体"))
        item = self.structTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "用于输入"))
        __sortingEnabled = self.structTableWidget.isSortingEnabled()
        self.structTableWidget.setSortingEnabled(False)
        # item = self.structTableWidget.item(0, 0)
        # item.setText(_translate("Dialog", "struct1"))
        # item = self.structTableWidget.item(1, 0)
        # item.setText(_translate("Dialog", "struct2"))
        # item = self.structTableWidget.item(2, 0)
        # item.setText(_translate("Dialog", "struct3"))
        self.structTableWidget.setSortingEnabled(__sortingEnabled)
        self.yesBtn.setText(_translate("Dialog", "确定"))
        # ===========================手写=================================
        self.selectedStruct = ""
        # ================================================================

    # ========================================手写===========================================
    '''
    @description: 设置界面的初始值
    @param {*} self
    @param {*} header_loc 传进来的header_loc已经是一个列表了
    @return {*}
    '''
    def setValues(self,header_loc):
        self.header_loc = header_loc
        self.structList = staticAnalysis.getAllStruct(header_loc)
        self.structTableWidget.setRowCount(len(self.structList))

        s_cbx = "{"
        s_lab = "{"
        for i in range(len(self.structList)):
            s_cbx += str(i)+":QtWidgets.QCheckBox(),"
            s_lab += str(i)+":QtWidgets.QLabel(),"
        s_cbx += "}"
        s_lab += "}"
        self.checkboxs = eval(s_cbx)
        self.labels = eval(s_lab)
        print(self.structList)
        for i in range(len(self.structList)):
            hLayout = QtWidgets.QHBoxLayout()
            hLayout.addWidget(self.checkboxs[i])
            hLayout.setAlignment(self.checkboxs[i],QtCore.Qt.AlignCenter)
            widget = QtWidgets.QWidget()
            widget.setLayout(hLayout)
            self.structTableWidget.setCellWidget(i,1,widget)
            self.structTableWidget.setRowHeight(i,40)
            self.labels[i].setText(self.structList[i])
            hLayout2 = QtWidgets.QHBoxLayout()
            hLayout2.addWidget(self.labels[i])
            hLayout2.setAlignment(self.labels[i],QtCore.Qt.AlignCenter)
            widget2 = QtWidgets.QWidget()
            widget2.setLayout(hLayout2)
            self.structTableWidget.setCellWidget(i,0,widget2)
            self.checkboxs[i].clicked.connect(lambda x,i=i:self.selectStruct(self.checkboxs[i],self.structList[i]))

        # 默认高度较矮，需要设置一下
        for i in range(len(self.structList)):
            self.structTableWidget.setRowHeight(i, 50)


    def selectStruct(self,checkbox,label):
        '''
        @description: 选择了某个结构体，将其对应的checkbox打勾
        @param {*} self
        @param {*} checkbox
        @param {*} label
        @return {*}
        '''
        self.unselectAll()
        checkbox.setChecked(True)
        self.selectedStruct = label


    def unselectAll(self):
        '''
        @description: 因为结构体是单选，所以写一个取消全部选择的函数，在选择某个结构体前先取消全部选择
        @param {*} self
        @return {*}
        '''
        for i in range(len(self.structList)):
            self.checkboxs[i].setChecked(False)
        self.selectedStruct = ""


    def popSeedDialog(self):
        '''
        @description: 弹出输入种子输入的界面
        @param {*} self
        @return {*}
        '''
        try:
            if self.selectedStruct == "":
                raise ValueError("没有选择结构体")
            self.seedDialog = QtWidgets.QDialog()
            self.uiSeed = seedDialogPY.Ui_Dialog()
            self.uiSeed.setupUi(self.seedDialog)
            self.uiSeed.initStructDict(self.header_loc, False, self.selectedStruct, self.structList)
            self.seedDialog.show()
        except ValueError as e:
            print(repr(e))
            exceptionBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "还没有选择结构体")
            exceptionBox.exec_()
        except BaseException as e:
            print(repr(e))
            exceptionBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", repr(e))
            exceptionBox.exec_()
    # ====================================================================================================