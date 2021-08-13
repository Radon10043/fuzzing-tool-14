'''
Author: Radon
Date: 2021-06-09 16:37:49
LastEditors: Radon
LastEditTime: 2021-08-11 19:51:25
Description: Hi, say something
'''
import os
import re

import public


def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]


def printInfo(msg):
    print("\n\033[0;32mInfo:\033[0m" + msg)


def instrument(source_loc, instrument_loc, instrument_var):
    '''
    @description: 多文件插装的方法
    @param {*} source_loc 列表，存储了所有源文件位置
    @param {*} instrument_loc 插装后的源文件位置
    @param {*} output_loc 输出文件位置，输出的文件是instrument.exe
    @param {*} instrument_var 插装变量
    @return {*}
    '''
    # 获取所有函数结点，方便编号
    allNode = public.getAllFunctions(source_loc)
    allNode = sorted(set(allNode), key=allNode.index)
    print(allNode)
    for num in range(len(source_loc)):
        brace = 0  # 记录大括号数量，方便后续操作
        instr = False
        try:
            f = open(source_loc[num])
            lines = f.readlines()
        except UnicodeDecodeError:
            f = open(source_loc[num], encoding="utf8")
            lines = f.readlines()
        f.close()
        # 删除注释
        lines = public.deleteNote(lines)
        length = len(lines)
        j = 0
        while j != length:
            if "(" in lines[j] and brace == 0:
                code = lines[j].split("(")[0]
                code = re.sub("[^A-Za-z1-9_]", " ", code)
                # 插桩语句，更换为改变结构体的值
                funcName = code.split(" ")[-1]
                if funcName == "main":
                    j += 1
                    continue
                for k in range(len(allNode)):
                    if allNode[k] == funcName:
                        break
                # 把变量的某一位置为1，用或操作
                instrCode = "\t" + instrument_var + " |= 1<<" + str(k) + ";\n"
                instr = True
            if "{" in lines[j]:
                brace += 1
            if "}" in lines[j]:
                brace -= 1
            if instr == True and brace > 0:
                lines.insert(j + 1, instrCode)
                instr = False
                length += 1
            j += 1
        f = open(instrument_loc[num], mode="w")
        for code in lines:
            f.write(code)
        f.close()
    printInfo("Instrument complete.")
    multiFileCompile(instrument_loc)


def multiFileCompile(source_loc):
    '''
    @description: 多文件编译的方法
    @param {*} source_loc 列表，其中存储了要编译的源文件的位置
    @return {*}
    '''
    # 获取所有源文件的名字
    cppFileName = []
    for source in source_loc:
        cppFileName.append(source.split("/")[-1])
    # 源文件所在的根目录
    root_loc = re.sub(source_loc[0].split("/")[-1], "", source_loc[0])
    # 指令集合
    cmds = []
    oFileName = []
    for f in cppFileName:
        cmds.append("g++ -c " + f)
        f = f.split(".")[0] + ".o"
        oFileName.append(f)

    # 切换工作目录，开始编译
    os.chdir(root_loc)
    cmds.append("g++ -o instrument.exe " + " ".join(oFileName) + " -lws2_32")
    for cmd in cmds:
        if os.system(cmd) != 0:
            print("出错!")
    # 移除插装的源文件
    for source in source_loc:
        os.remove(source)
    # 删掉.o文件
    for oFile in oFileName:
        os.remove(oFile)


import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
