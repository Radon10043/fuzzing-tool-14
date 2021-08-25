'''
Author: Radon
Date: 2021-06-09 16:37:49
LastEditors: Radon
LastEditTime: 2021-08-25 17:56:59
Description: Hi, say something
'''
import os
import re, subprocess
import clang.cindex

import public


def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]


def printInfo(msg):
    print("\n\033[0;32mInfo:\033[0m" + msg)


def instrumentBaseOnAST(cursor, allFunc, source, instrTemplate):
    """根据AST的内容进行插装

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        根节点
    allFunc : list
        全部函数
    source : str
        源文件地址
    instrTemplate : str
        插装模板

    Returns
    -------
    [type]
        [description]

    Notes
    -----
    [description]
    """
    instrTemplate += " |= 1 << "
    instr = False
    brace = 0
    try:
        f = open(source, mode="r", encoding="utf-8")
        codeList = f.readlines()
        f.close()
    except UnicodeDecodeError:
        f = open(source, mode="r", encoding="gbk")
        codeList = f.readlines()
        f.close()
    except:
        print("err!")
        return

    for token in cursor.get_tokens():
        if token.spelling in allFunc:
            if token.spelling == "main":
                continue
            idx = allFunc.index(token.spelling)
            instrCode = instrTemplate +  str(idx) + ";"
            instr = True
            print(token.spelling, ",", token.location.file.name + "?" + str(token.location.line))
        if token.spelling == "{":
            if instr and brace == 0:
                temp = codeList[token.location.line - 1].split("{")
                temp[1] = instrCode + temp[1]
                codeList[token.location.line - 1] = "{".join(temp)
                instr = False
            brace += 1
        if token.spelling == "}":
            brace -= 1

    newSource = re.sub(source.split("/")[-1], "ins_" + source.split("/")[-1], source)
    try:
        f = open(newSource, mode="w", encoding="utf-8")
        for code in codeList:
            f.write(code)
        f.close()
    except UnicodeEncodeError:
        f = open(newSource, mode="w", encoding="gbk")
        for code in codeList:
            f.write(code)
        f.close()
    except BaseException as e:
        print("Error occured in instrumentBaseOnAST:", e)

    return newSource


def instrument(source_loc_list, instrTemplate):
    """插装与编译

    Parameters
    ----------
    source_loc_list : list
        源文件地址
    instrTemplate : str
        插装语句模板

    Notes
    -----
    [description]
    """
    root_loc = re.sub(source_loc_list[0].split("/")[-1], "", source_loc_list[0])

    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split(
        "\\")[-1], "", libclangPath) + "libclang.dll"
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    # 获取所有函数，下标决定了它的id
    # TODO 如果函数数量超过插装变量的位数量
    allFunc = public.getAllFunctions(source_loc_list)
    ins_loc_list = list()
    for source in source_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(source)
        ins_loc_list.append(instrumentBaseOnAST(tu.cursor, allFunc, source, instrTemplate))

    # 编译生成exe文件
    # g++ -g aaa.cpp bbb.cpp -o ccc.exe -lws2_32
    cmd = "g++ -g "
    for file in ins_loc_list:
        cmd += file + " "
    cmd += "-o " + root_loc + "instrument.exe -lws2_32"
    os.system(cmd)
    for file in ins_loc_list:
        os.remove(file)


import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
