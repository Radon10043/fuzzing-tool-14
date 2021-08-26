# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Project_VSCode\python\fuzzProject\server\window_server.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

import sys, os, traceback
import re

import Ui_dialog_execServer as execServerDialogPY
import Ui_dialog_selectTarget as targetDialogPY
import Ui_dialog_selectStruct as selectStructDialogPY
import Ui_dialog_output as outputDialogPY
import staticAnalysis as sa
import instrument as instr
import callgraph as cg


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 770)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(300, 30, 161, 16))
        self.title.setObjectName("title")
        self.fileSelectGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.fileSelectGroupBox.setGeometry(QtCore.QRect(70, 50, 651, 241))
        self.fileSelectGroupBox.setObjectName("fileSelectGroupBox")
        self.chooseCBtn = QtWidgets.QPushButton(self.fileSelectGroupBox)
        self.chooseCBtn.setGeometry(QtCore.QRect(510, 90, 131, 28))
        self.chooseCBtn.setObjectName("chooseCBtn")
        self.CFileLoc = QtWidgets.QTextBrowser(self.fileSelectGroupBox)
        self.CFileLoc.setGeometry(QtCore.QRect(10, 20, 631, 61))
        self.CFileLoc.setObjectName("CFileLoc")
        self.HFileLoc = QtWidgets.QTextBrowser(self.fileSelectGroupBox)
        self.HFileLoc.setGeometry(QtCore.QRect(10, 130, 631, 61))
        self.HFileLoc.setObjectName("HFileLoc")
        self.chooseHBtn = QtWidgets.QPushButton(self.fileSelectGroupBox)
        self.chooseHBtn.setGeometry(QtCore.QRect(510, 200, 131, 28))
        self.chooseHBtn.setObjectName("chooseHBtn")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(400, 300, 321, 171))
        self.tabWidget.setStyleSheet("background-color:rgb(235, 235, 235)")
        self.tabWidget.setObjectName("tabWidget")
        self.codeStructTab = QtWidgets.QWidget()
        self.codeStructTab.setObjectName("codeStructTab")
        self.SAByCppcheckBtn = QtWidgets.QPushButton(self.codeStructTab)
        self.SAByCppcheckBtn.setGeometry(QtCore.QRect(210, 15, 93, 31))
        self.SAByCppcheckBtn.setObjectName("SAByCppcheckBtn")
        self.SAByManBtn = QtWidgets.QPushButton(self.codeStructTab)
        self.SAByManBtn.setGeometry(QtCore.QRect(210, 60, 93, 31))
        self.SAByManBtn.setObjectName("SAByManBtn")
        self.targetSetInfo = QtWidgets.QTextBrowser(self.codeStructTab)
        self.targetSetInfo.setGeometry(QtCore.QRect(10, 12, 191, 121))
        self.targetSetInfo.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.targetSetInfo.setObjectName("targetSetInfo")
        self.SAResultGenBtn = QtWidgets.QPushButton(self.codeStructTab)
        self.SAResultGenBtn.setGeometry(QtCore.QRect(210, 105, 93, 31))
        self.SAResultGenBtn.setObjectName("SAResultGenBtn")
        self.tabWidget.addTab(self.codeStructTab, "")

        # self.interfaceTab = QtWidgets.QWidget()
        # self.interfaceTab.setObjectName("interfaceTab")
        # self.tabWidget.addTab(self.interfaceTab, "")

        self.selectInsVarGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.selectInsVarGroupBox.setGeometry(QtCore.QRect(70, 310, 291, 131))
        self.selectInsVarGroupBox.setObjectName("selectInsVarGroupBox")
        self.structParameterName = QtWidgets.QLineEdit(self.selectInsVarGroupBox)
        self.structParameterName.setGeometry(QtCore.QRect(20, 80, 113, 31))
        self.structParameterName.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.structParameterName.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.structParameterName.setCursorPosition(3)
        self.structParameterName.setObjectName("structParameterName")
        self.pointerStyleRadioBtn = QtWidgets.QRadioButton(self.selectInsVarGroupBox)
        self.pointerStyleRadioBtn.setGeometry(QtCore.QRect(160, 70, 115, 19))
        self.pointerStyleRadioBtn.setChecked(True)
        self.pointerStyleRadioBtn.setObjectName("pointerStyleRadioBtn")
        self.pointStyleRadioBtn = QtWidgets.QRadioButton(self.selectInsVarGroupBox)
        self.pointStyleRadioBtn.setGeometry(QtCore.QRect(160, 100, 115, 19))
        self.pointStyleRadioBtn.setChecked(False)
        self.pointStyleRadioBtn.setObjectName("pointStyleRadioBtn")
        self.selectInsVarBtn = QtWidgets.QPushButton(self.selectInsVarGroupBox)
        self.selectInsVarBtn.setGeometry(QtCore.QRect(80, 30, 141, 28))
        self.selectInsVarBtn.setObjectName("selectInsVarBtn")
        self.autoGenInsCodeConfirmBtn = QtWidgets.QPushButton(self.selectInsVarGroupBox)
        self.autoGenInsCodeConfirmBtn.setGeometry(QtCore.QRect(230, 80, 51, 28))
        self.autoGenInsCodeConfirmBtn.setObjectName("autoGenInsCodeConfirmBtn")
        self.startServerBtn = QtWidgets.QPushButton(self.centralwidget)
        self.startServerBtn.setGeometry(QtCore.QRect(400, 610, 321, 71))
        self.startServerBtn.setObjectName("startServerBtn")
        self.callGraphGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.callGraphGroupBox.setGeometry(QtCore.QRect(400, 500, 321, 80))
        self.callGraphGroupBox.setObjectName("callGraphGroupBox")
        self.genCallGraphBtn = QtWidgets.QPushButton(self.callGraphGroupBox)
        self.genCallGraphBtn.setGeometry(QtCore.QRect(90, 30, 151, 28))
        self.genCallGraphBtn.setObjectName("genCallGraphBtn")
        self.manualInputInsCodeGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.manualInputInsCodeGroupBox.setGeometry(QtCore.QRect(70, 460, 291, 121))
        self.manualInputInsCodeGroupBox.setObjectName("manualInputInsCodeGroupBox")
        self.manualInputInsVarType = QtWidgets.QLineEdit(self.manualInputInsCodeGroupBox)
        self.manualInputInsVarType.setGeometry(QtCore.QRect(20, 30, 201, 31))
        self.manualInputInsVarType.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.manualInputInsVarType.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.manualInputInsVarType.setText("")
        self.manualInputInsVarType.setCursorPosition(0)
        self.manualInputInsVarType.setObjectName("manualInputInsVarType")
        self.manualInputInsCodeConfirmBtn = QtWidgets.QPushButton(self.manualInputInsCodeGroupBox)
        self.manualInputInsCodeConfirmBtn.setGeometry(QtCore.QRect(230, 70, 51, 28))
        self.manualInputInsCodeConfirmBtn.setObjectName("manualInputInsCodeConfirmBtn")
        self.manualInputInsCode = QtWidgets.QLineEdit(self.manualInputInsCodeGroupBox)
        self.manualInputInsCode.setGeometry(QtCore.QRect(20, 70, 201, 31))
        self.manualInputInsCode.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.manualInputInsCode.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.manualInputInsCode.setText("")
        self.manualInputInsCode.setCursorPosition(0)
        self.manualInputInsCode.setObjectName("manualInputInsCode")
        self.insCodePreviewGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.insCodePreviewGroupBox.setGeometry(QtCore.QRect(70, 600, 291, 121))
        self.insCodePreviewGroupBox.setObjectName("insCodePreviewGroupBox")
        self.instrumentCodeLabel = QtWidgets.QLabel(self.insCodePreviewGroupBox)
        self.instrumentCodeLabel.setGeometry(QtCore.QRect(20, 20, 271, 20))
        self.instrumentCodeLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.instrumentCodeLabel.setTextFormat(QtCore.Qt.AutoText)
        self.instrumentCodeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.instrumentCodeLabel.setWordWrap(False)
        self.instrumentCodeLabel.setIndent(-1)
        self.instrumentCodeLabel.setObjectName("instrumentCodeLabel")
        self.instrumentBtn = QtWidgets.QPushButton(self.insCodePreviewGroupBox)
        self.instrumentBtn.setGeometry(QtCore.QRect(80, 80, 141, 28))
        self.instrumentBtn.setObjectName("instrumentBtn")
        self.insVarTypeLabelTip = QtWidgets.QLabel(self.insCodePreviewGroupBox)
        self.insVarTypeLabelTip.setGeometry(QtCore.QRect(20, 45, 101, 20))
        self.insVarTypeLabelTip.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.insVarTypeLabelTip.setTextFormat(QtCore.Qt.AutoText)
        self.insVarTypeLabelTip.setAlignment(QtCore.Qt.AlignCenter)
        self.insVarTypeLabelTip.setWordWrap(False)
        self.insVarTypeLabelTip.setIndent(-1)
        self.insVarTypeLabelTip.setObjectName("insVarTypeLabelTip")
        self.insVarTypeLabel = QtWidgets.QLabel(self.insCodePreviewGroupBox)
        self.insVarTypeLabel.setGeometry(QtCore.QRect(130, 45, 151, 20))
        self.insVarTypeLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.insVarTypeLabel.setTextFormat(QtCore.Qt.AutoText)
        self.insVarTypeLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.insVarTypeLabel.setWordWrap(False)
        self.insVarTypeLabel.setIndent(-1)
        self.insVarTypeLabel.setObjectName("insVarTypeLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # ==========connect================================================
        self.chooseCBtn.clicked.connect(self.chooseCFile)
        self.chooseHBtn.clicked.connect(self.chooseHFile)
        self.selectInsVarBtn.clicked.connect(self.popStructDialog)
        self.autoGenInsCodeConfirmBtn.clicked.connect(self.setInstrumentCode)
        self.pointerStyleRadioBtn.clicked.connect(self.setInstrumentCode)
        self.pointStyleRadioBtn.clicked.connect(self.setInstrumentCode)
        self.manualInputInsCodeConfirmBtn.clicked.connect(self.setInstrumentCodeManually)
        self.SAByCppcheckBtn.clicked.connect(self.SAByCppcheck)
        self.SAByManBtn.clicked.connect(self.popTargetDialog)
        self.SAResultGenBtn.clicked.connect(self.genSAResult)
        self.instrumentBtn.clicked.connect(self.instrumentSource)
        self.genCallGraphBtn.clicked.connect(self.genCallGraph)
        self.startServerBtn.clicked.connect(self.startServer)
        # =================================================================

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "模糊测试工具 - 服务端"))
        self.title.setText(_translate("MainWindow", "模糊测试工具 - 服务端"))
        self.fileSelectGroupBox.setTitle(_translate("MainWindow", "文件选择"))
        self.chooseCBtn.setText(_translate("MainWindow", "选择C文件"))
        self.CFileLoc.setPlaceholderText(_translate("MainWindow", "C文件位置"))
        self.HFileLoc.setPlaceholderText(_translate("MainWindow", "头文件位置"))
        self.chooseHBtn.setText(_translate("MainWindow", "选择头文件"))
        self.SAByCppcheckBtn.setText(_translate("MainWindow", "cppcheck"))
        self.SAByManBtn.setText(_translate("MainWindow", "手动选择"))
        self.targetSetInfo.setPlaceholderText(_translate("MainWindow", "目标集信息"))
        self.SAResultGenBtn.setText(_translate("MainWindow", "结果生成"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.codeStructTab), _translate("MainWindow", "基于代码结构"))

        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.interfaceTab), _translate("MainWindow", "基于交互接口故规约"))

        self.selectInsVarGroupBox.setTitle(_translate("MainWindow", "选择插桩变量"))
        self.structParameterName.setText(_translate("MainWindow", "dtg"))
        self.structParameterName.setPlaceholderText(_translate("MainWindow", "结构体实参名"))
        self.pointerStyleRadioBtn.setText(_translate("MainWindow", "方式1"))
        self.pointStyleRadioBtn.setText(_translate("MainWindow", "方式2"))
        self.selectInsVarBtn.setText(_translate("MainWindow", "选择插桩变量"))
        self.autoGenInsCodeConfirmBtn.setText(_translate("MainWindow", "确定"))
        self.startServerBtn.setText(_translate("MainWindow", "启动服务端程序"))
        self.callGraphGroupBox.setTitle(_translate("MainWindow", "调用图"))
        self.genCallGraphBtn.setText(_translate("MainWindow", "生成函数调用图"))
        self.manualInputInsCodeGroupBox.setTitle(_translate("MainWindow", "手动输入插桩语句"))
        self.manualInputInsVarType.setToolTip(_translate("MainWindow", "手动输入插桩变量类型"))
        self.manualInputInsVarType.setPlaceholderText(_translate("MainWindow", "手动输入插桩变量类型"))
        self.manualInputInsCodeConfirmBtn.setText(_translate("MainWindow", "确定"))
        self.manualInputInsCode.setToolTip(_translate("MainWindow", "手动输入插桩语句，输入等号前的内容即可"))
        self.manualInputInsCode.setPlaceholderText(_translate("MainWindow", "手动输入插桩语句"))
        self.insCodePreviewGroupBox.setTitle(_translate("MainWindow", "插桩语句预览"))
        self.instrumentCodeLabel.setText(_translate("MainWindow", "dtg->variable = 1 << x;"))
        self.instrumentBtn.setText(_translate("MainWindow", "插桩"))
        self.insVarTypeLabelTip.setText(_translate("MainWindow", "插桩变量类型:"))
        self.insVarTypeLabel.setText(_translate("MainWindow", "暂无"))


    # ==========定义功能================================================================
    def chooseCFile(self):
        """选择C文件

        Notes
        -----
        现在可以选择C或CPP文件
        """
        # 注意！getOpenFileNames()中的filter如果想选择多个文件的话，需要用两个分号隔开！
        # temp = QtWidgets.QFileDialog.getOpenFileNames(None,"choose file","C:/Users/Radon/Desktop/",filter="c files (*.c);;cpp Files (*.cpp)")
        temp = QtWidgets.QFileDialog.getOpenFileNames(None, "choose file", "C:/Users/Radon/Desktop/",
                                                    filter="cpp files(*.cpp);;c files(*.c)")
        path = ""
        for i in range(len(temp[0])):
            path += temp[0][i] + "\n"
        path = path.rstrip("\n")
        self.CFileLoc.setText(path)


    def chooseHFile(self):
        """选择头文件

        Notes
        -----
        [description]
        """
        temp = QtWidgets.QFileDialog.getOpenFileNames(None, "choose file", "C:/Users/Radon/Desktop/", "h files (*.h)")
        path = ""
        for i in range(len(temp[0])):
            path += temp[0][i] + "\n"
        path = path.rstrip("\n")
        self.HFileLoc.setText(path)


    def popStructDialog(self):
        """弹出选择结构体的对话框

        Notes
        -----
        [description]
        """
        self.header_loc_list = self.HFileLoc.toPlainText().split("\n")
        for header in self.header_loc_list:
            if not os.path.exists(header):
                headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "头文件" + header + "不存在!")
                headerNotExistBox.exec_()
                return

        # 询问用户是否读取JSON
        readJSON = False
        whetherReadJSONBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, "读取文件", "是否读取现有JSON文件?")
        yes = whetherReadJSONBox.addButton("是", QtWidgets.QMessageBox.YesRole)
        no = whetherReadJSONBox.addButton("否", QtWidgets.QMessageBox.NoRole)
        whetherReadJSONBox.exec_()
        if whetherReadJSONBox.clickedButton() == yes:
            readJSON = True

        # 如果读取现有文件，就让用户选择JSON
        if readJSON:
            selectedFile = QtWidgets.QFileDialog.getOpenFileName(None, "choose file", "C:/Users/Radon/Desktop/", filter="json file (*.json)")
            JSONPath = selectedFile[0]
            try:
                # 如果JSONPath是空字符串，表示用户点击了右上角的X
                if JSONPath == "":
                    return
                self.outputDialog = QtWidgets.QDialog()
                self.uiOutput = outputDialogPY.Ui_Dialog()
                self.uiOutput.setupUi(self.outputDialog)
                self.uiOutput.initStructDict(self.header_loc_list, JSONPath, readJSON, self, struct="struct", allStruct=["all","Struct"])
                self.outputDialog.show()
            except BaseException as e:
                traceback.print_exc()
                loadJSONFailedBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "读取失败", "JSON文件读取失败!")
                loadJSONFailedBox.exec_()
        # 如果不读取现有文件，就让用户选择输入/输出变量格式
        else:
            # 检查clang是否安装正确
            if os.system("clang -v") != 0:
                clangInstallErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "未检测到clang")
                clangInstallErrBox.exec_()
                return
            self.selectStructDialog = QtWidgets.QDialog()
            self.uiSelectStruct = selectStructDialogPY.Ui_Dialog()
            self.uiSelectStruct.setupUi(self.selectStructDialog)
            self.uiSelectStruct.setValues(self.header_loc_list, "output", self)
            self.selectStructDialog.show()


    def popTargetDialog(self):
        """弹出一个dialog，其中显示了C中所有函数，供用户选择目标

        Notes
        -----
        [description]
        """
        # 获取所有函数需要用clang，检测是否安装clang
        if os.system("clang -v") != 0:
            clangInstallErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "未检测到clang")
            clangInstallErrBox.exec_()
            return

        self.targetSetInfo.clear()
        source_loc_str = self.CFileLoc.toPlainText()
        source_loc_list = source_loc_str.split("\n")
        for source in source_loc_list:
            if not os.path.exists(source):
                sourceNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "C文件不存在!")
                sourceNotExistBox.exec_()
                return
        self.targetDialog = QtWidgets.QDialog()
        self.uiTarget = targetDialogPY.Ui_Dialog()
        self.uiTarget.setupUi(self.targetDialog)
        self.uiTarget.setValues(ui, source_loc_list, [])
        self.targetDialog.show()


    def SAByCppcheck(self):
        """通过CPPCHECK进行静态分析获取可能有缺陷的地方

        Notes
        -----
        [description]
        """
        # cppcheck与人工分析的结果需要存储到txt里
        self.targetSetInfo.clear()

        source_loc_list = self.CFileLoc.toPlainText().split("\n")
        for source in source_loc_list:
            if not os.path.exists(source):
                sourceNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "C文件不存在")
                sourceNotExistBox.exec_()
                return

        # 检查cppcheck是否正确安装
        if os.system("cppcheck --version") != 0:
            cppcheckInstallErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "未检测到cppcheck")
            cppcheckInstallErrBox.exec_()
            return

        try:
            source_loc_str = self.CFileLoc.toPlainText()
            self.SAResult = sa.analyze(source_loc_str)
            if len(self.SAResult) == 0:
                self.targetSetInfo.setText("暂无目标!")
                return
            if isinstance(self.SAResult, str):
                self.targetSetInfo.setText(self.SAResult)
                return
            self.targetDialog = QtWidgets.QDialog()
            self.uiTarget = targetDialogPY.Ui_Dialog()
            self.uiTarget.setupUi(self.targetDialog)
            self.uiTarget.setValues(ui, source_loc_str.split("\n"), self.SAResult)
            self.targetDialog.show()
        except BaseException as e:
            cppcheckErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "分析失败:" + str(e))
            cppcheckErrBox.exec_()


    def genSAResult(self):
        """将目标集信息写入saresult.txt

        Notes
        -----
        [description]
        """
        try:
            source_loc_list = self.CFileLoc.toPlainText().split("\n")
            for source in source_loc_list:
                if not os.path.exists(source):
                    sourceNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "C文件不存在")
                    sourceNotExistBox.exec_()
                    return

            root_loc = source_loc_list[0]
            root_loc = re.sub(root_loc.split("/")[-1], "", root_loc) + "in/"
            if not os.path.exists(root_loc):
                os.mkdir(root_loc)
            f = open(root_loc + "saresult.txt", mode="w")
            for data in self.targetSetInfo.toPlainText().split("\n"):
                f.write(data + "\n")
            f.close()
            genSAResultSuccBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "结果生成成功!")
            genSAResultSuccBox.exec_()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            genSAResultErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "结果生成失败:" + str(e))
            genSAResultErrBox.exec_()


    def setInstrumentCode(self):
        """设置插桩语句的预览文本

        Notes
        -----
        [description]
        """
        # 读取插桩变量
        root_loc = self.CFileLoc.toPlainText().split("\n")[0]
        root_loc = re.sub(root_loc.split("/")[-1], "", root_loc)
        if os.path.exists(root_loc + "/in/instrument.txt"):
            f = open(root_loc + "/in/instrument.txt")
            content = f.read()
            insVarName = content.split(" ")[-1].split(":")[0]
            insVarType = content.split(":")[0].split(" ")   # list
            insVarType.pop(-1)
            insVarType = " ".join(insVarType)       #str
            f.close()
        else:
            insVarName = "还未生成插桩文件"
            insVarType = "暂无"

        # 设置连接符
        if self.pointerStyleRadioBtn.isChecked():
            connectStr = "->"
        else:
            connectStr = "."

        # 设置预览文本
        self.instrumentCodeLabel.setText(self.structParameterName.text() + connectStr + insVarName + " |= 1<<x;")
        self.insVarTypeLabel.setText(insVarType)


    def setInstrumentCodeManually(self):
        """手动设置插桩语句

        Notes
        -----
        [description]
        """
        self.instrumentCodeLabel.setText(self.manualInputInsCode.text() + " |= 1<<x;")
        if self.manualInputInsVarType.text() == "":
            self.insVarTypeLabel.setText("暂无")
        else:
            self.insVarTypeLabel.setText(self.manualInputInsVarType.text())


    def instrumentSource(self):
        """对文件进行插桩与编译，在源文件同目录下生成instrument.exe文件

        Notes
        -----
        [description]
        """
        source_loc_list = self.CFileLoc.toPlainText().split("\n")
        header_loc_list = self.HFileLoc.toPlainText().split("\n")
        root_loc = re.sub(source_loc_list[0].split("/")[-1], "", source_loc_list[0])

        for source in source_loc_list:
            if not os.path.exists(source):
                sourceNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "C文件不存在!")
                sourceNotExistBox.exec_()
                return
        for header in header_loc_list:
            if not os.path.exists(header):
                headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "头文件不存在!")
                headerNotExistBox.exec_()
                return

        # 检查mingw是否安装正确
        if os.system("gcc --version") != 0:
            gccInstallErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "未检测到mingw")
            gccInstallErrBox.exec_()
            return

        # 移除旧的instrument.exe
        if os.path.exists(root_loc + "instrument.exe"):
            os.remove(root_loc + "instrument.exe")

        try:
            instrTemplate = self.instrumentCodeLabel.text().split("|=")[0].rstrip()

            # 生成insFunc.c与insFunc.dll
            # insVarName是插桩变量的名字, instrTemplate是插桩语句等号左边的东西
            insVarName = instrTemplate.replace("->", " ").replace(".", " ")
            insVarName = re.sub(insVarName.split(" ")[0], "", instrTemplate)
            insVarName = insVarName.lstrip("[->.]")
            # insVarType是插桩变量的类型
            insVarType = self.insVarTypeLabel.text()
            # 生成获取插桩值的instrument.dll
            f = open(root_loc + "in/insFunc.c", mode="w")
            code = "#include <stdio.h>\n#include <stdbool.h>\n"
            for header in header_loc_list:
                code += "#include \"" + header + "\"\n"
            code += "\n\n" + insVarType + " getInstrumentValue(" + open(root_loc + "in/outputStruct.txt").read() + "* data) {\n"
            code += "\treturn data->" + insVarName + ";\n}"
            f.write(code)
            f.close()
            os.system("gcc -shared -o " + root_loc + "in/insFunc.dll " + root_loc + "in/insFunc.c")

            # 插桩
            instr.instrument(source_loc_list, instrTemplate)

            instrSuccBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "插桩成功!")
            instrSuccBox.exec_()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            instrErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "插桩失败: " + str(e))
            instrErrBox.exec_()


    def genCallGraph(self):
        """在源文件根目录的in文件夹下生成调用图callgraph.txt

        Notes
        -----
        [description]
        """
        source_loc_list = self.CFileLoc.toPlainText().split("\n")
        root_loc = re.sub(source_loc_list[0].split("/")[-1], "", source_loc_list[0])

        for source in source_loc_list:
            if not os.path.exists(source):
                sourceNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "C文件不存在!")
                sourceNotExistBox.exec_()
                return

        # 获取函数调用图需要用clang，检测是否安装clang
        if os.system("clang -v") != 0:
            clangInstallErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "未检测到clang")
            clangInstallErrBox.exec_()
            return

        try:
            if not os.path.exists(root_loc + "in"):
                os.mkdir(root_loc+ "in")
            graph_loc =  root_loc + "in/callgraph.txt"
            cg.createCallGraph(source_loc_list, graph_loc)
            genCGSuccBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "调用图生成成功!")
            genCGSuccBox.exec_()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            genCGErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "调用图生成失败: " + str(e))
            genCGErrBox.exec_()


    def startServer(self):
        """启动服务端程序

        Notes
        -----
        [description]
        """
        try:
            program_loc = self.CFileLoc.toPlainText().split("\n")[0]
            program_loc = re.sub(program_loc.split("/")[-1], "instrument.exe", program_loc)
            if not os.path.exists(program_loc):
                programNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "插桩程序不存在!")
                programNotExistBox.exec_()
                return

            self.execServerDialog = QtWidgets.QDialog()
            self.uiExecServer = execServerDialogPY.Ui_Dialog()
            self.uiExecServer.setupUi(self.execServerDialog)
            self.uiExecServer.startServer(program_loc, ui, self.uiExecServer)
            self.execServerDialog.show()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            startServerErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "服务端启动失败:" + str(e))
            startServerErrBox.exec_()
    # ==================================================================================


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
