'''
Author: Radon
Date: 2021-06-09 16:37:49
LastEditors: Radon
LastEditTime: 2021-09-12 15:10:46
Description: Hi, say something
'''
from PyQt5 import QtWidgets
import sys
import os
import re
import subprocess
import clang.cindex
import traceback

import public


class instrumentMethod(object):
    def instrument(self):
        print("instrument...")

    def genInstrCFile(self, header_loc_list, instrVarType, instrVarName):
        """生成获取插装变量的C文件

        Parameters
        ----------
        header_loc_list : list
            头文件列表
        instrVarType : str
            插装变量类型
        instrVarName : str
            插装变量名称

        Returns
        -------
        [type]
            [description]

        Notes
        -----
        [description]
        """
        in_loc = os.path.join(os.path.dirname(header_loc_list[0]), "in")
        outputStructName = open(os.path.join(in_loc, "outputStruct.txt")).read()
        code = "#include <stdio.h>\n#include <stdbool.h>\n"
        for header in header_loc_list:
            code += "#include \"" + header + "\"\n"
        code += "\n\n" + instrVarType + " getInstrumentValue(" + outputStructName + "* data) {\n"
        code += "\treturn data->" + instrVarName + ";\n}"

        f = open(os.path.join(in_loc, "insFunc.c"), mode="w")
        f.write(code)
        f.close()


class instrumentMethod3(instrumentMethod):
    def __init__(self):
        """构造函数，加载dll

        Notes
        -----
        [description]
        """
        libclangPath = subprocess.getstatusoutput("where clang")[1]
        libclangPath = os.path.join(os.path.dirname(libclangPath), "libclang.dll")
        if clang.cindex.Config.loaded == True:
            print("clang.cindex.Config.loaded == True:")
        else:
            clang.cindex.Config.set_library_file(libclangPath)
            print("install path")

    def instrument(self, source_loc_list, dataType, dataName):
        """插装函数

        Parameters
        ----------
        source_loc_list : list
            源文件地址列表
        dataType : str
            插装变量数据类型
        dataName : str
            插装变量名称

        Notes
        -----
        [description]
        """
        funcList = public.getAllFunctions(source_loc_list)
        initGlobalVar = True
        for source in source_loc_list:
            try:
                f = open(source, mode="r", encoding="utf-8")
                lines = f.readlines()
                f.close()
            except UnicodeDecodeError:
                f = open(source, mode="r", encoding="gbk")
                lines = f.readlines()
                f.close()
            except BaseException as e:
                print("\033[1;31m")
                traceback.print_exc()
                print("\033[0m")
                return
            index = clang.cindex.Index.create()
            tu = index.parse(source)
            self.initInstrVar(tu.cursor, lines, funcList, initGlobalVar, dataType, dataName)
            self.instrumentSource(tu.cursor, source, lines, funcList, dataName)
            initGlobalVar = False

    def initInstrVar(self, cursor, lines, funcList, initGlobalVar, dataType, dataName):
        """初始化插装全局变量为0

        Parameters
        ----------
        cursor : clang.cindex.Cursor
            根节点
        lines : list
            源码内容
        funcList : list
            全部函数
        initGlobalVar : bool
            是否初始化全局变量
        dataType : str
            插装变量数据类型
        dataName : str
            插装变量数据名称

        Notes
        -----
        [description]
        """
        for cur in cursor.get_children():
            if cur.kind == clang.cindex.CursorKind.FUNCTION_DECL and cur.spelling in funcList and os.path.splitext(cur.location.file.name)[-1] != ".h":
                if initGlobalVar:
                    lines[cur.location.line - 1] = dataType + " " + \
                        dataName + " = 0;" + lines[cur.location.line - 1]
                else:
                    lines[cur.location.line - 1] = "extern " + dataType + \
                        " " + dataName + ";" + lines[cur.location.line - 1]
                return

    def instrumentSource(self, cursor, source, lines, funcList, dataName):
        """对源码进行插装

        Parameters
        ----------
        cursor : clang.cindex.Cursor
            根节点
        source : str
            源文件位置
        lines : list
            源文件内容
        funcList : list
            全部函数
        dataName : str
            插装变量名称

        Notes
        -----
        [description]
        """
        brace = 0
        for token in cursor.get_tokens():
            if token.spelling in funcList:
                idx = funcList.index(token.spelling)
                instrCode = dataName + " |= 1 << " + str(idx) + ";"
                instr = True
            if token.spelling == ";":
                instr = False
            if token.spelling == "{":
                if instr and brace == 0:
                    temp = lines[token.location.line - 1].split("{")
                    temp[1] = instrCode + temp[1]
                    lines[token.location.line - 1] = "{".join(temp)
                    instr = False
                brace += 1
            if token.spelling == "}":
                brace -= 1

        try:
            f = open(os.path.join(os.path.dirname(source), "ins_" + os.path.basename(source)), mode="w", encoding="utf-8")
        except UnicodeEncodeError:
            f = open(os.path.join(os.path.dirname(source), "ins_" + os.path.basename(source)), mode="w", encoding="gbk")
        for line in lines:
            f.write(line)
        f.close()

    def insertAssignCode(self, source_loc_list, targetSource, nthLine, assignCode):
        """向已插入全局变量的语句中插入插装变量赋值语句

        Parameters
        ----------
        source_loc_list : list
            源文件列表
        targetSource : str
            目标源文件名称
        nthLine : int
            要插入的行数
        assignCode : str
            要插入的赋值语句

        Notes
        -----
        [description]
        """
        targetSource = os.path.join(os.path.dirname(source_loc_list[0]), targetSource)
        try:
            f = open(targetSource, mode="r", encoding="utf-8")
            lines = f.readlines()
            f.close()
        except UnicodeDecodeError:
            f = open(targetSource, mode="r", encoding="gbk")
            lines = f.readlines()
            f.close()
        except:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")

        f = open(targetSource, mode="w")
        lines[nthLine - 1] = assignCode + lines[nthLine - 1]
        for line in lines:
            f.write(line)
        f.close()


def compileInstrFiles(source_loc_list):
    """编译插装的文件，生成instrument.exe

    Parameters
    ----------
    source_loc_list : list
        源文件列表

    Notes
    -----
    [description]
    """
    instrFilesList = list()
    for source in source_loc_list:
        instrFilesList.append(os.path.join(os.path.dirname(source), "ins_" + os.path.basename(source)))

    cmd = "g++ -g "
    for file in instrFilesList:
        cmd += source + " "
    cmd += "-o " + os.path.join(os.path.dirname(source_loc_list[0]), "instrument.exe -lws2_32")
    os.system(cmd)


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
            instrCode = instrTemplate + str(idx) + ";"
            instr = True
            print(token.spelling, ",", token.location.file.name + "?" + str(token.location.line))
        if token.spelling == ";":
            instr = False
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
    TODO 保留当前插装方式，新增一个插装方式：用户指定发回报文的代码位置，程序自动设计一个插装变量，然后发回报文前进行赋值
    """
    root_loc = re.sub(source_loc_list[0].split("/")[-1], "", source_loc_list[0])

    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split("\\")[-1], "", libclangPath) + "libclang.dll"
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
