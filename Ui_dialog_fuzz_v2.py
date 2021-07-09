# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\VSCode_Project\python_project\fuzzProject\dialog_v2.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import time
import sys
import re
import os

import fuzz
import fuzz_ai



class Ui_Dialog(object):
    stop = False
    fuzz_ai = False
    def setupUi(self, Dialog, fuzz_ai):
        Dialog.setObjectName("Dialog")

        self.fuzz_ai = fuzz_ai
        self.text_browser_nn = None
        self.text_browser_exec = None
        self.textBrowser = None
        if fuzz_ai:
            Dialog.resize(794, 357)
            self.text_browser_nn = QtWidgets.QTextBrowser(Dialog)
            self.text_browser_exec = QtWidgets.QTextBrowser(Dialog)
            self.text_browser_nn.setGeometry(QtCore.QRect(35, 21, 321, 271))
            self.text_browser_exec.setGeometry(QtCore.QRect(400, 21, 321, 271))
        else:
            Dialog.resize(494, 357)
            self.textBrowser = QtWidgets.QTextBrowser(Dialog)
            self.textBrowser.setGeometry(QtCore.QRect(35, 21, 421, 271))
            self.textBrowser.setObjectName("textBrowser")

        self.stopBtn = QtWidgets.QPushButton(Dialog)
        self.stopBtn.setGeometry(QtCore.QRect(50, 300, 93, 28))
        self.stopBtn.setObjectName("stopBtn")
        self.checkResultBtn = QtWidgets.QPushButton(Dialog)
        self.checkResultBtn.setGeometry(QtCore.QRect(200, 300, 93, 28))
        self.checkResultBtn.setObjectName("checkResultBtn")
        self.checkResultBtn.setEnabled(False)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # ======================================以下为手写内容==============================================
        # 新建并设置关闭页面的按钮
        self.closeBtn = QtWidgets.QPushButton(Dialog)
        self.closeBtn.setGeometry(QtCore.QRect(350, 300, 93, 28))
        self.closeBtn.setObjectName("closeBtn")
        self.closeBtn.setText("关闭页面")
        self.closeBtn.setDisabled(True)
        self.closeBtn.clicked.connect(Dialog.accept)

        # 右上角仅设置最小化按钮可用
        Dialog.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        self.stopBtn.setText("停止")
        self.stopBtn.clicked.connect(self.stopFuzz)
        self.checkResultBtn.setText("查看结果")
        self.checkResultBtn.clicked.connect(self.openFolder)
        # =======================================手写内容结束===============================================

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "测试信息"))
        if not self.fuzz_ai:
            self.textBrowser.setHtml(_translate("Dialog",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                            "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
                                            "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
                                            "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
                                            "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
                                            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">测试信息</p></body></html>"))

    # 以下为手写内容
    def startFuzz(self, source_loc, ui, uiFuzz):
        # fuzz.fuzz(source_loc,ui,ui2)
        self.source_loc = source_loc
        self.ui = ui
        self.targetSetInfo = re.sub("[^A-Za-z1-9_\n]","",ui.targetSetInfo.toPlainText())
        self.fuzzThread = FuzzThread()
        self.fuzzThread.fuzzInfoSgn.connect(self.fuzzInfoPrint)
        self.fuzzThread.nnInfoSgn.connect(self.nnInfoPrint)
        self.fuzzThread.execInfoSgn.connect(self.execInfoPrint)
        self.fuzzThread.overSgn.connect(self.overFuzz)
        self.fuzzThread.errorSgn.connect(self.errorFuzz)
        self.fuzzThread.setValues(source_loc, ui, uiFuzz, self.targetSetInfo, self.fuzz_ai)
        if self.fuzz_ai:
            self.text_browser_nn.setText("\n\n\t\t初始化中...\n\t即将开始基于机器学习的模糊测试...")
            self.text_browser_exec.setText("\n\n\t\t初始化中...\n\t即将开始基于机器学习的模糊测试...")
        elif len(self.targetSetInfo) == 0:
            self.textBrowser.setText("\n\n\t\t初始化中...\n\t即将开始无目标的模糊测试...")
        else:
            self.textBrowser.setText("\n\n\t\t初始化中...\n\t即将开始目标制导的模糊测试...")

    def fuzzInfoPrint(self,fuzzInfo):
        '''
        @description: 打印发送回来的模糊测试信息
        @param {*} self
        @param {*} fuzzInfo
        @return {*}
        '''
        # self.fuzzInfoTBrowser.setText(fuzzInfo)
        self.textBrowser.setText(fuzzInfo)
        QtWidgets.QApplication.processEvents()
        print(fuzzInfo)

    def nnInfoPrint(self, fuzzInfo):
        self.text_browser_nn.setText(fuzzInfo)
        QtWidgets.QApplication.processEvents()
        print(fuzzInfo)

    def execInfoPrint(self, fuzzInfo):
        self.text_browser_exec.setText(fuzzInfo)
        QtWidgets.QApplication.processEvents()
        print(fuzzInfo)

    def overFuzz(self):
        '''
        @description: 结束模糊测试，并将一些按钮变为可按的
        @param {*} self
        @return {*}
        '''
        self.closeBtn.setEnabled(True)
        self.checkResultBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.ui.startFuzzBtn.setEnabled(True)
        self.ui.popSeedDialogBtn.setEnabled(True)

    def errorFuzz(self):
        '''
        @description: 如果模糊测试出现了异常则执行这些
        @param {*} self
        @return {*}
        '''
        self.checkResultBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        self.closeBtn.setEnabled(True)

    def stopFuzz(self):
        '''
        @description: 停止模糊测试
        @param {*} self
        @return {*}
        '''
        print("stop!")
        self.stop = True

    def openFolder(self):
        '''
        @description: 打开out文件夹所在的位置
        @param {*} self
        @return {*}
        '''
        out_loc = self.source_loc[0]
        out_loc = re.sub(out_loc.split("\\")[-1], "", out_loc) + "out"
        if os.path.exists(out_loc):
            os.system("explorer.exe " + out_loc)
        else:
            print("out_loc not exist!")


# 模糊测试用一个新线程，不然会暂时卡死
class FuzzThread(QThread):
    # 3个信号，分别表示接收模糊测试信息的信号，结束模糊测试的信号，模糊测试出错的信号
    fuzzInfoSgn = QtCore.pyqtSignal(str)
    nnInfoSgn = QtCore.pyqtSignal(str)
    execInfoSgn = QtCore.pyqtSignal(str)
    overSgn = QtCore.pyqtSignal(bool)
    errorSgn = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()


    def setValues(self, source_loc, ui, uiFuzz, targetSetInfo, fuzz_ai):
        '''
        @description: 设置一些初始值
        @param {*} self
        @param {*} source_loc 列表，其中存储了所有源文件的地址
        @param {*} ui Ui_window_v5的ui
        @param {*} uiFuzz Ui_dialog_fuzz_v2的ui
        @param {*} targetSetInfo 目标集信息
        @return {*}
        '''
        self.fuzz_ai = fuzz_ai
        self.source_loc = source_loc
        self.ui = ui
        self.uiFuzz = uiFuzz
        self.targetSetInfo = targetSetInfo
        self.start()

    def run(self):
        '''
        @description: 启动模糊测试线程
        @param {*} self
        @return {*}
        '''
        print("FuzzThread has started.")
        if self.fuzz_ai:
            self.result=fuzz_ai.fuzz(self.source_loc,self.ui,self.uiFuzz,self)
        else:
            fuzz.initGloablVariable()
            self.result = fuzz.fuzz(self.source_loc,self.ui,self.uiFuzz,self)
        if isinstance(self.result,str):
            self.errorSgn.emit(True)
        else:
            self.overSgn.emit(True)

