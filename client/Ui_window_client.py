# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Project_VSCode\python\fuzzProject\client\window_client.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

import sys, traceback, os, re

import Ui_dialog_seed as seedDialogPY
import Ui_dialog_selectStruct as selectStructDialogPY
import Ui_dialog_validation as validateDialogPY
import Ui_dialog_prepareFuzz as prepareFuzzDialogPY

import Ui_dialog_AICfg as  aicfgDialogPY

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(714, 686)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(290, 30, 161, 16))
        self.label.setObjectName("label")
        self.fileSelectGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.fileSelectGroupBox.setGeometry(QtCore.QRect(79, 70, 561, 141))
        self.fileSelectGroupBox.setObjectName("fileSelectGroupBox")
        self.HFileLoc = QtWidgets.QTextBrowser(self.fileSelectGroupBox)
        self.HFileLoc.setGeometry(QtCore.QRect(20, 20, 521, 71))
        self.HFileLoc.setObjectName("HFileLoc")
        self.chooseHFileBtn = QtWidgets.QPushButton(self.fileSelectGroupBox)
        self.chooseHFileBtn.setGeometry(QtCore.QRect(430, 100, 111, 28))
        self.chooseHFileBtn.setObjectName("chooseHFileBtn")
        self.seedInputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.seedInputGroupBox.setGeometry(QtCore.QRect(390, 220, 251, 111))
        self.seedInputGroupBox.setObjectName("seedInputGroupBox")
        self.seedInputBtn = QtWidgets.QPushButton(self.seedInputGroupBox)
        self.seedInputBtn.setGeometry(QtCore.QRect(50, 40, 151, 28))
        self.seedInputBtn.setObjectName("seedInputBtn")
        self.isMutateInRangeCheckBox = QtWidgets.QCheckBox(self.seedInputGroupBox)
        self.isMutateInRangeCheckBox.setGeometry(QtCore.QRect(60, 80, 131, 19))
        self.isMutateInRangeCheckBox.setChecked(True)
        self.isMutateInRangeCheckBox.setObjectName("isMutateInRangeCheckBox")
        self.validationGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.validationGroupBox.setGeometry(QtCore.QRect(80, 490, 291, 121))
        self.validationGroupBox.setObjectName("validationGroupBox")
        self.startValidateBtn = QtWidgets.QPushButton(self.validationGroupBox)
        self.startValidateBtn.setGeometry(QtCore.QRect(100, 30, 93, 28))
        self.startValidateBtn.setObjectName("startValidateBtn")
        self.validateTipLabel = QtWidgets.QLabel(self.validationGroupBox)
        self.validateTipLabel.setGeometry(QtCore.QRect(70, 70, 161, 41))
        self.validateTipLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.validateTipLabel.setObjectName("validateTipLabel")
        self.addressSetGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.addressSetGroupBox.setGeometry(QtCore.QRect(80, 220, 291, 111))
        self.addressSetGroupBox.setObjectName("addressSetGroupBox")
        self.senderIPLineEdit = QtWidgets.QLineEdit(self.addressSetGroupBox)
        self.senderIPLineEdit.setGeometry(QtCore.QRect(20, 30, 141, 21))
        self.senderIPLineEdit.setText("")
        self.senderIPLineEdit.setObjectName("senderIPLineEdit")
        self.receiverIPLineEdit = QtWidgets.QLineEdit(self.addressSetGroupBox)
        self.receiverIPLineEdit.setGeometry(QtCore.QRect(20, 70, 141, 21))
        self.receiverIPLineEdit.setObjectName("receiverIPLineEdit")
        self.senderPortLineEdit = QtWidgets.QLineEdit(self.addressSetGroupBox)
        self.senderPortLineEdit.setGeometry(QtCore.QRect(180, 30, 91, 21))
        self.senderPortLineEdit.setText("")
        self.senderPortLineEdit.setObjectName("senderPortLineEdit")
        self.receiverPortLineEdit = QtWidgets.QLineEdit(self.addressSetGroupBox)
        self.receiverPortLineEdit.setGeometry(QtCore.QRect(180, 70, 91, 21))
        self.receiverPortLineEdit.setText("")
        self.receiverPortLineEdit.setObjectName("receiverPortLineEdit")
        self.senderColonLabel = QtWidgets.QLabel(self.addressSetGroupBox)
        self.senderColonLabel.setGeometry(QtCore.QRect(165, 30, 16, 16))
        self.senderColonLabel.setObjectName("senderColonLabel")
        self.receiverColonLabel = QtWidgets.QLabel(self.addressSetGroupBox)
        self.receiverColonLabel.setGeometry(QtCore.QRect(165, 70, 16, 16))
        self.receiverColonLabel.setObjectName("receiverColonLabel")
        self.startFuzzBtn = QtWidgets.QPushButton(self.centralwidget)
        self.startFuzzBtn.setGeometry(QtCore.QRect(420, 510, 201, 81))
        self.startFuzzBtn.setObjectName("startFuzzBtn")
        self.stopOptionGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.stopOptionGroupBox.setGeometry(QtCore.QRect(79, 340, 291, 141))
        self.stopOptionGroupBox.setObjectName("stopOptionGroupBox")
        self.stopByCrash = QtWidgets.QRadioButton(self.stopOptionGroupBox)
        self.stopByCrash.setGeometry(QtCore.QRect(20, 30, 161, 19))
        self.stopByCrash.setChecked(True)
        self.stopByCrash.setObjectName("stopByCrash")
        self.stopByTime = QtWidgets.QRadioButton(self.stopOptionGroupBox)
        self.stopByTime.setGeometry(QtCore.QRect(20, 70, 81, 19))
        self.stopByTime.setObjectName("stopByTime")
        self.stopByTC = QtWidgets.QRadioButton(self.stopOptionGroupBox)
        self.stopByTC.setGeometry(QtCore.QRect(20, 110, 121, 19))
        self.stopByTC.setObjectName("stopByTC")
        self.fuzzTime = QtWidgets.QSpinBox(self.stopOptionGroupBox)
        self.fuzzTime.setGeometry(QtCore.QRect(110, 67, 71, 25))
        self.fuzzTime.setMaximum(9999)
        self.fuzzTime.setObjectName("fuzzTime")
        self.timeUnit = QtWidgets.QComboBox(self.stopOptionGroupBox)
        self.timeUnit.setGeometry(QtCore.QRect(190, 67, 81, 25))
        self.timeUnit.setObjectName("timeUnit")
        self.timeUnit.addItem("")
        self.timeUnit.addItem("")
        self.TCNumsLineEdit = QtWidgets.QLineEdit(self.stopOptionGroupBox)
        self.TCNumsLineEdit.setGeometry(QtCore.QRect(150, 105, 101, 25))
        self.TCNumsLineEdit.setObjectName("TCNumsLineEdit")
        self.amountLabel = QtWidgets.QLabel(self.stopOptionGroupBox)
        self.amountLabel.setGeometry(QtCore.QRect(255, 110, 21, 16))
        self.amountLabel.setObjectName("amountLabel")

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(390, 340, 251, 141))
        self.tabWidget.setStyleSheet("background-color:rgb(235, 235, 235)")
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setObjectName("tabWidget")

        self.AITab = QtWidgets.QWidget()
        self.AITab.setObjectName("interfaceTab")
        self.AICfgInfo = QtWidgets.QTextBrowser(self.AITab)
        self.AICfgInfo.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.AICfgInfo.setGeometry(QtCore.QRect(20, 10, 201, 71))
        # self.AIFuzz = QtWidgets.QRadioButton(self.AITab)
        # self.AIFuzz.setGeometry(QtCore.QRect(230, 10, 93, 31))
        self.AICfgBtn = QtWidgets.QPushButton(self.AITab)
        self.AICfgBtn.setGeometry(QtCore.QRect(70, 85, 93, 30))
        self.AICfgBtn.setObjectName("AICfgBtn")

        # self.AICfgDialog = aicfgDialogPY.Ui_Dialog(self.AICfgInfo)


        self.otherOptionGroupBox = QtWidgets.QGroupBox()
        self.tabWidget.addTab(self.otherOptionGroupBox, "")
        self.tabWidget.addTab(self.AITab, "")
        #　self.otherOptionGroupBox.setGeometry(QtCore.QRect(390, 340, 251, 141))
        self.otherOptionGroupBox.setObjectName("otherOptionGroupBox")
        self.TCNumPerCyc = QtWidgets.QLineEdit(self.otherOptionGroupBox)
        self.TCNumPerCyc.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.TCNumPerCyc.setGeometry(QtCore.QRect(137, 15, 71, 30))
        self.TCNumPerCyc.setObjectName("TCNumPerCyc")
        self.timeoutLEdit = QtWidgets.QLineEdit(self.otherOptionGroupBox)
        self.timeoutLEdit.setGeometry(QtCore.QRect(137, 65, 71, 30))
        self.timeoutLEdit.setObjectName("timeoutLEdit")
        self.timeoutLEdit.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.TCNumPerCycLabel = QtWidgets.QLabel(self.otherOptionGroupBox)
        self.TCNumPerCycLabel.setGeometry(QtCore.QRect(10, 20, 121, 16))
        self.TCNumPerCycLabel.setObjectName("TCNumPerCycLabel")
        self.TCTimeoutLabel = QtWidgets.QLabel(self.otherOptionGroupBox)
        self.TCTimeoutLabel.setGeometry(QtCore.QRect(10, 70, 121, 16))
        self.TCTimeoutLabel.setObjectName("TCTimeoutLabel")
        self.secondLabel = QtWidgets.QLabel(self.otherOptionGroupBox)
        self.secondLabel.setGeometry(QtCore.QRect(210, 70, 21, 16))
        self.secondLabel.setObjectName("secondLabel")
        self.pieceLabel = QtWidgets.QLabel(self.otherOptionGroupBox)
        self.pieceLabel.setGeometry(QtCore.QRect(210, 20, 21, 16))
        self.pieceLabel.setObjectName("pieceLabel")


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 714, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # ==========connect========================================================
        self.chooseHFileBtn.clicked.connect(self.chooseHFile)
        self.seedInputBtn.clicked.connect(self.popStructDialog)
        self.startValidateBtn.clicked.connect(self.popValidateDialog)
        self.startFuzzBtn.clicked.connect(self.popPrepareFuzzDialog)

        self.AICfgBtn.clicked.connect(self.popAICfgDialog)



        # 每轮测试用例数量、超时时间上线为1000，测试用例总数量上线为1亿
        regExp1 = QtCore.QRegExp("^([1-9]\d{0,2}|1000)$")
        self.TCNumPerCyc.setValidator(QtGui.QRegExpValidator(regExp1))
        self.timeoutLEdit.setValidator(QtGui.QRegExpValidator(regExp1))
        regExp2 = QtCore.QRegExp("^([1-9]\d{0,6}|10000000)$")
        self.TCNumsLineEdit.setValidator(QtGui.QRegExpValidator(regExp2))
        self.AICfgDialog = None

        # self.senderIPLineEdit.setText("")
        # self.senderPortLineEdit.setText("9999")
        # self.receiverIPLineEdit.setText("192.168.50.176")
        # self.receiverPortLineEdit.setText("8888")
        # =========================================================================

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "模糊测试工具 - 客户端"))
        self.label.setText(_translate("MainWindow", "模糊测试工具 - 客户端"))
        self.fileSelectGroupBox.setTitle(_translate("MainWindow", "文件选择"))
        self.HFileLoc.setPlaceholderText(_translate("MainWindow", "头文件位置"))
        self.chooseHFileBtn.setText(_translate("MainWindow", "选择头文件"))
        self.seedInputGroupBox.setTitle(_translate("MainWindow", "种子设置"))
        self.seedInputBtn.setText(_translate("MainWindow", "设置种子测试用例"))
        self.isMutateInRangeCheckBox.setText(_translate("MainWindow", "变异体在范围内"))
        self.validationGroupBox.setTitle(_translate("MainWindow", "完整性验证"))
        self.startValidateBtn.setText(_translate("MainWindow", "开始验证"))
        self.validateTipLabel.setText(_translate("MainWindow", "验证目前是否已持有进行\n"
"模糊测试的必要文件"))
        self.addressSetGroupBox.setTitle(_translate("MainWindow", "地址设置"))
        self.senderIPLineEdit.setToolTip(_translate("MainWindow", "通常为本机IP地址"))
        self.senderIPLineEdit.setPlaceholderText(_translate("MainWindow", "发送方IP地址"))
        self.receiverIPLineEdit.setPlaceholderText(_translate("MainWindow", "接收方IP地址"))
        self.senderPortLineEdit.setPlaceholderText(_translate("MainWindow", "端口"))
        self.receiverPortLineEdit.setPlaceholderText(_translate("MainWindow", "端口"))
        self.senderColonLabel.setText(_translate("MainWindow", ":"))
        self.receiverColonLabel.setText(_translate("MainWindow", ":"))
        self.startFuzzBtn.setText(_translate("MainWindow", "开始测试"))
        self.stopOptionGroupBox.setTitle(_translate("MainWindow", "终止条件"))
        self.stopByCrash.setText(_translate("MainWindow", "检测到错误就停止"))
        self.stopByTime.setText(_translate("MainWindow", "按时间"))
        self.stopByTC.setText(_translate("MainWindow", "按测试用例数"))
        self.timeUnit.setItemText(0, _translate("MainWindow", "分钟"))
        self.timeUnit.setItemText(1, _translate("MainWindow", "小时"))
        self.TCNumsLineEdit.setText(_translate("MainWindow", "2000"))
        self.amountLabel.setText(_translate("MainWindow", "个"))

        # self.otherOptionGroupBox.setTitle(_translate("MainWindow", "其他设置"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.AITab), _translate("MainWindow", "基于交互接口规约"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.otherOptionGroupBox), _translate("MainWindow", "基于代码结构"))


        self.TCNumPerCyc.setText(_translate("MainWindow", "5"))
        self.timeoutLEdit.setText(_translate("MainWindow", "10"))
        self.TCNumPerCycLabel.setText(_translate("MainWindow", "每轮测试用例生成"))
        self.TCTimeoutLabel.setText(_translate("MainWindow", "测试用例超时时间"))
        self.secondLabel.setText(_translate("MainWindow", "秒"))
        self.pieceLabel.setText(_translate("MainWindow", "个"))
        self.AICfgBtn.setText(_translate("MainWindow", "设置"))


    # ==========定义功能================================================================
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



    def popAICfgDialog(self):
        self.AICfgDialog = aicfgDialogPY.Ui_Dialog(self.AICfgInfo)
        self.AICfgDialog.show()


    def popStructDialog(self):
        """弹出选择结构体的界面

        Parameters
        ----------
        choice : str
            表示按下了哪个按钮，如果按下了输入按钮choice的值就是input，输出是output

        Notes
        -----
        [description]
        """
        self.header_loc_list = self.HFileLoc.toPlainText().split("\n")
        for header in self.header_loc_list:
            if not os.path.exists(header):
                headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "头文件不存在!")
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
                self.seedDialog = QtWidgets.QDialog()
                self.uiSeed = seedDialogPY.Ui_Dialog()
                self.uiSeed.setupUi(self.seedDialog)
                # 如果读取JSON的话，后两个参数其实是用不上的
                self.uiSeed.initStructDict(self.header_loc_list, JSONPath, readJSON, self, struct="struct", allStruct=["all","struct"])
                self.seedDialog.show()
            except BaseException as e:
                traceback.print_exc()
                loadJSONFailedBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "读取失败", "JSON文件读取失败: " + str(e))
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
            self.selectStructDialog.show()
            self.uiSelectStruct.setValues(self.header_loc_list, "input", self)


    def popValidateDialog(self):
        """弹出验证完整性的对话框

        Notes
        -----
        [description]
        """
        try:
            header_loc_list = self.HFileLoc.toPlainText().split("\n")
            for header in header_loc_list:
                if not os.path.exists(header):
                    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "头文件不存在")
                    headerNotExistBox.exec_()
                    return
            self.validateDialog = QtWidgets.QDialog()
            self.uiValidate = validateDialogPY.Ui_Dialog()
            self.uiValidate.setupUi(self.validateDialog)
            self.validateDialog.show()
            self.uiValidate.startValidate(header_loc_list)
        except BaseException as e:
            validateErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "验证失败: " + str(e))
            validateErrBox.exec_()
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m]")


    def popPrepareFuzzDialog(self):
        header_loc_list = self.HFileLoc.toPlainText().split("\n")
        for header in header_loc_list:
            if not os.path.exists(header):
                headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "头文件不存在")
                headerNotExistBox.exec_()
                return

        # IPAddress列表中存储了发送方与接收方的IP，0是发送方，1是接收方
        IPAddressList = list()
        IPAddressList.append(self.senderIPLineEdit.text() + ":" + self.senderPortLineEdit.text())
        IPAddressList.append(self.receiverIPLineEdit.text() + ":" + self.receiverPortLineEdit.text())

        self.prepareFuzzDialog = QtWidgets.QDialog()
        self.uiPrepareFuzz = prepareFuzzDialogPY.Ui_Dialog()
        self.uiPrepareFuzz.setupUi(self.prepareFuzzDialog)
        self.prepareFuzzDialog.show()
        self.uiPrepareFuzz.setValues(self, header_loc_list, IPAddressList)
    # ==================================================================================

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())