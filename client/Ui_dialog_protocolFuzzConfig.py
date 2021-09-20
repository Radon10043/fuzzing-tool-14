import os
import re

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self, textBrowser, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.textBrowser = textBrowser
        self.setObjectName("Dialog")
        self.resize(380, 480)
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.Tool | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)


        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.nnOptionGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.nnOptionGroup.setGeometry(QtCore.QRect(20, 50, 340, 180))
        self.nnOptionGroup.setObjectName("stopOptionGroup")
        self.aiEnableCheckBox = QtWidgets.QCheckBox(self)
        self.aiEnableCheckBox.setGeometry(QtCore.QRect(20, 18, 250, 30))
        self.aiEnableCheckBox.setChecked(False)
        self.aiEnableCheckBox.clicked.connect(self.enableAI)

        self.randTS = QtWidgets.QRadioButton(self.nnOptionGroup)
        self.randTS.setGeometry(QtCore.QRect(20, 20, 150, 19))
        self.randTS.setObjectName("randTS")
        self.randTS.setChecked(True)
        self.randTS.setEnabled(False)
        self.randTSSize = QtWidgets.QLineEdit(self.nnOptionGroup)
        self.randTSSize.setGeometry(QtCore.QRect(240, 20, 90, 25))
        self.randTSSize.setObjectName("randTSSize")
        self.randTSSize.setEnabled(False)

        self.existTS = QtWidgets.QRadioButton(self.nnOptionGroup)
        self.existTS.setGeometry(QtCore.QRect(20, 60, 115, 19))
        self.existTS.setObjectName("existTS")
        self.existTS.setEnabled(False)
        self.tsLoc = QtWidgets.QTextBrowser(self.nnOptionGroup)
        self.tsLoc.setGeometry(QtCore.QRect(20, 100, 310, 25))
        self.choosBtn = QtWidgets.QPushButton(self.nnOptionGroup)
        self.choosBtn.setGeometry(QtCore.QRect(140, 135, 80, 30))
        self.tsLoc.setEnabled(False)
        self.choosBtn.setEnabled(False)
        self.choosBtn.setStyleSheet("")
        self.existTS.clicked.connect(self.enableChooseSeed)
        self.randTS.clicked.connect(self.disableChooseSeed)
        self.choosBtn.clicked.connect(self.chooseTrainingSet)

        self.execOptionGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.execOptionGroup.setGeometry(QtCore.QRect(20, 240, 340, 130))
        self.execOptionGroup.setObjectName("execOptionGroup")
        self.seedPerRoundLabel = QtWidgets.QLabel(self.execOptionGroup)
        self.seedPerRoundLabel.setGeometry(QtCore.QRect(20, 30, 130, 19))
        self.seedPerRound = QtWidgets.QLineEdit(self.execOptionGroup)
        self.seedPerRound.setGeometry(QtCore.QRect(240, 30, 90, 25))
        self.seedPerRound.setObjectName("seedPerRound")
        self.mutSize = QtWidgets.QComboBox(self.execOptionGroup)
        self.mutSize.setGeometry(QtCore.QRect(240, 70, 90, 25))
        self.mutSize.setObjectName("mutSize")
        self.mutSize.addItem("")
        self.mutSize.addItem("")
        self.mutSize.addItem("")
        self.mutSizeLabel = QtWidgets.QLabel(self.execOptionGroup)
        self.mutSizeLabel.setGeometry(QtCore.QRect(20, 70, 130, 25))
        regex = QtCore.QRegExp("^([1-9]\d{0,2}|1000)$")
        self.seedPerRound.setValidator(QtGui.QRegExpValidator(regex))
        self.randTSSize.setValidator(QtGui.QRegExpValidator(regex))

        self.yesBtn = QtWidgets.QPushButton(self)
        self.yesBtn.setGeometry(QtCore.QRect(200, 400, 160, 30))
        self.yesBtn.clicked.connect(self.close)
        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "基于交互接口规约的模糊测试设置"))
        self.aiEnableCheckBox.setText(_translate("Dialog", "使用AI制导的测试用例生成策略"))
        # self.nnOptionGroup.setTitle(_translate("Dialog", "模型训练"))
        self.execOptionGroup.setTitle(_translate("Dialog", "测试执行"))
        self.randTS.setText(_translate("nnOptionGroup", "随机生成初始训练数据"))
        # self.randTSSize.setText(_translate("nnOptionGroup", "10"))
        self.randTSSize.setPlaceholderText("100")
        self.existTS.setText(_translate("nnOptionGroup", "使用已有训练数据"))
        self.choosBtn.setText(_translate("nnOptionGroup", "浏览"))
        self.seedPerRoundLabel.setText(_translate("execOptionGroup", "每轮选取变异的种子数"))
        # self.seedPerRound.setText(_translate("execOptionGroup", "2"))
        self.seedPerRound.setPlaceholderText("10")
        self.mutSizeLabel.setText(_translate("execOptionGroup", "变异规模"))
        self.mutSize.setItemText(0, _translate("execOptionGroup", "小"))
        self.mutSize.setItemText(1, _translate("execOptionGroup", "中"))
        self.mutSize.setItemText(2, _translate("execOptionGroup", "大"))
        self.yesBtn.setText(_translate("Dialog", "确 定"))

    def enableChooseSeed(self):
        self.choosBtn.setEnabled(True)
        self.tsLoc.setEnabled(True)
        self.randTSSize.setEnabled(False)

    def disableChooseSeed(self):
        self.choosBtn.setEnabled(False)
        self.tsLoc.setEnabled(False)
        self.randTSSize.setEnabled(True)
        self.tsLoc.setText("")

    def enableAI(self):
        if self.aiEnableCheckBox.isChecked():
            self.randTS.setEnabled(True)
            self.randTSSize.setEnabled(True)
            self.existTS.setEnabled(True)
            self.choosBtn.setEnabled(True)
        else:
            self.randTS.setEnabled(False)
            self.randTSSize.setEnabled(False)
            self.existTS.setEnabled(False)
            self.tsLoc.setEnabled(False)
            self.choosBtn.setEnabled(False)


    def chooseTrainingSet(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None, os.curdir)
        self.tsLoc.setText(path)

    def getConfigInfo(self):
        info = ""
        if self.aiEnableCheckBox.isChecked():
            info += "使用AI制导的测试用例生成策略\n"
            if self.randTS.isChecked():
                info += "随机生成初始训练数据，规模：" + self.randTSSize.text()
            else:
                info += "使用已有训练数据：\n" + self.tsLoc.toPlainText()
        else:
            info += "使用随机测试用例生成策略\n"
        info += "\n每轮选取变异的种子数：" + self.seedPerRound.text()
        info += "\n变异规模：" + self.mutSize.currentText()
        return info

    def closeEvent(self, event):
        if self.randTSSize.text() == "":
            self.randTSSize.setText(self.randTSSize.placeholderText())
        if self.seedPerRound.text() == "":
            self.seedPerRound.setText(self.seedPerRound.placeholderText())
        if self.tsLoc.isEnabled() and self.tsLoc.toPlainText() == "":
            warning = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "请指定初始训练集位置！")
            warning.exec_()
            event.ignore()
            return
        self.textBrowser.setText(self.getConfigInfo())
        event.accept()