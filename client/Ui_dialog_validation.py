'''
Author: Radon
Date: 2021-08-12 14:33:16
LastEditors: Radon
LastEditTime: 2021-10-09 14:14:59
Description: Hi, say something
'''
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Project_VSCode\python\fuzzProject\client\dialog_validation.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets

import re, os


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 308)
        self.validateResultTextBrowser = QtWidgets.QTextBrowser(Dialog)
        self.validateResultTextBrowser.setGeometry(QtCore.QRect(50, 20, 301, 231))
        self.validateResultTextBrowser.setObjectName("validateResultTextBrowser")
        self.closeBtn = QtWidgets.QPushButton(Dialog)
        self.closeBtn.setGeometry(QtCore.QRect(160, 260, 93, 28))
        self.closeBtn.setObjectName("closeBtn")

        # ==========connect================================================================
        self.closeBtn.clicked.connect(Dialog.accept)
        # =================================================================================

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "完整性验证"))
        self.validateResultTextBrowser.setHtml(
            _translate(
                "Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">验证中...</p></body></html>"
            ))
        self.closeBtn.setText(_translate("Dialog", "关闭页面"))

    def startValidate(self, header_loc_list):
        root_loc = os.path.join(os.path.dirname(header_loc_list[0]), "in")
        self.validateResultTextBrowser.clear()

        # 查看当前目录下是否有in文件夹
        if not os.path.exists(root_loc):
            self.validateResultTextBrowser.append("<font color='red'>X 头文件根目录下不存在in文件夹</font>")
            return
        self.validateResultTextBrowser.append("<font color='green'>√ 头文件根目录下存在in文件夹</font>")

        # 查看in文件夹中是否有mutate.c, input.json, checkCodeMethod.txt, header_loc_list.txt, seed, callgraph.txt, insFunc.dll, nodes.txt
        filesForNoTarget = [
            "mutate.c", "mutate.dll", "input.json", "checkCodeMethod.txt", "header_loc_list.txt", "seed", "callgraph.txt", "insFunc.dll", "nodes.txt"
        ]
        noTargetFilesValidation = True
        for file in filesForNoTarget:
            if os.path.exists(os.path.join(root_loc, file)):
                self.validateResultTextBrowser.append("<font color='green'>√ %s</font>" % ("已检测到" + file))
                if file == "mutate.c":
                    cJSONRootPath = os.path.dirname(os.path.abspath(__file__))      # 使用copy命令将cJSON.c与cJSON.h复制到in目录下
                    copyCmd = "copy " + os.path.join(cJSONRootPath, "*cJSON*") + " " + root_loc
                    os.system(copyCmd)
                    os.system("gcc -shared -o " + os.path.join(root_loc, "mutate.dll") + " " + os.path.join(root_loc, "mutate.c") + " " + os.path.join(root_loc, "cJSON.c"))
            else:
                self.validateResultTextBrowser.append("<font color='red'>X %s</font>" % ("未检测到" + file))
                noTargetFilesValidation = False

        # 查看in文件夹中是否有saresult.txt
        filesForTarget = ["saresult.txt"]
        targetFilesValidation = True
        for file in filesForTarget:
            if os.path.exists(os.path.join(root_loc, file)):
                self.validateResultTextBrowser.append("<font color='green'>√ %s</font>" % ("已检测到" + file))
            else:
                self.validateResultTextBrowser.append("<font color='red'>X %s</font>" % ("未检测到" + file))
                targetFilesValidation = False

        # 如果客户端与服务端的完整性验证均通过，则可以开始目标制导的模糊测试
        # 如果客户端通过，服务端不通过，则可以开始无目标制导的模糊测试
        # 如果客户端不通过，服务端通过或两者均不通过，则无法开始模糊测试
        if noTargetFilesValidation and targetFilesValidation:
            self.validateResultTextBrowser.append("<font color='green'>- %s</font>" % ("可以开始目标制导的模糊测试"))
        elif noTargetFilesValidation and not targetFilesValidation:
            self.validateResultTextBrowser.append("<font color='orange'>- %s</font>" % ("可以开始无目标制导的模糊测试"))
        else:
            self.validateResultTextBrowser.append("<font color='red'>- %s</font>" % ("无法开始模糊测试，请尝试重新生成文件"))
