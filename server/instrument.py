'''
Author: Radon
Date: 2021-06-09 16:37:49
LastEditors: Radon
LastEditTime: 2021-09-30 15:25:45
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

    def instrument(self):
        print("instrument...")

    def genInstrCFile(self, header_loc_list, source_loc_list, instrVarType, instrVarName):
        """生成获取插装变量的C文件

        Parameters
        ----------
        header_loc_list : list
            头文件列表
        source_loc_list : list
            源文件列表
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
        in_loc = os.path.join(os.path.dirname(source_loc_list[0]), "in")
        outputStructName = open(os.path.join(in_loc, "outputStruct.txt")).read()
        code = "#include <stdio.h>\n#include <stdbool.h>\n"
        for header in header_loc_list:
            code += "#include \"" + header + "\"\n"
        code += "\n\n" + instrVarType + " getInstrumentValue(" + outputStructName + "* data) {\n"
        code += "\treturn data->" + instrVarName + ";\n}"

        f = open(os.path.join(in_loc, "insFunc.c"), mode="w")
        f.write(code)
        f.close()


class instrumentMethod2BaseC89(instrumentMethod):
    def instrument(self, source_loc_list, instrTemplate):
        """基于C89标准对程序进行插装

        Parameters
        ----------
        source_loc_list : list
            源文件地址列表
        instrTemplate : str
            插装代码模板

        Notes
        -----
        [description]
        """
        # 获取所有函数中最后的声明变量语句的位置
        lastVarDeclDict = dict()    # <string, <string, int>>: <函数名称, <所在文件, 所在行>>
        codeDict = dict()           # <string, list>: <源文件地址, [源文件内容]>
        for i in range(len(source_loc_list)):   # XXX TEMP
            source_loc_list[i] = source_loc_list[i]
        for source in source_loc_list:
            try:
                f = open(source, mode="r", encoding="utf8")
                codeList = f.readlines()
                f.close()
            except UnicodeDecodeError:
                f = open(source, mode="r", encoding="utf-8")
                codeList = f.readlines()
                f.close()
            except  BaseException as e:
                print("\033[1;31m")
                traceback.print_exc()
                print("\033[0m")
                return
            codeDict[os.path.abspath(source)] = codeList    # 存储源代码内容
            index = clang.cindex.Index.create()             # 遍历AST获取所有函数中最后的声明变量语句的位置
            tu = index.parse(source)
            allFuncList = public.getAllFunctions(source_loc_list)
            self.traverseASTToGetLastVarDeclDict(tu.cursor, allFuncList, source_loc_list, lastVarDeclDict)

        for key, value in lastVarDeclDict.items():
            if key == "main":               # main函数一定会执行，所以不对它进行插装应该也行
                continue
            idx = allFuncList.index(key)    # 根据func的id生成插装语句
            instrCode = instrTemplate + "|=" + str(idx) + ";"
            line = codeDict[value["file"]][value["lastVarDeclLine"] - 1].split(";")
            if len(line) > 1:
                line[-1] = instrCode + line[-1]
                codeDict[value["file"]][value["lastVarDeclLine"] - 1] = ";".join(line)
            else:
                codeDict[value["file"]][value["lastVarDeclLine"] - 1] += instrCode

        for key, value in codeDict.items():
            newSource = "ins_" + os.path.basename(key)
            newSource = os.path.join(os.path.dirname(key), newSource)
            f = open(newSource, mode="w")
            for data in value:
                f.write(data)
            f.close()

    def traverseASTToGetLastVarDeclDict(self, cursor, allFuncList, source_loc_list, lastVarDeclDict):
        """遍历AST, 获取各函数中最后声明变量语句的位置信息

        Parameters
        ----------
        cursor : clang.cindex.Cursor
            根节点
        allFuncList : list
            所有函数
        source_loc_list : list
            源文件地址
        lastVarDeclDict : 存储最后声明变量语句位置信息的字典
            [description]

        Notes
        -----
        [description]
        """
        for cur in cursor.get_children():
            if cur.spelling in allFuncList and cur.location.file.name in source_loc_list:
                lastVarDeclLine = self.traverseFuncCursor(cur)
                if cur.spelling in lastVarDeclDict.keys():
                    lastVarDeclDict[cur.spelling]["lastVarDeclLine"] = max(lastVarDeclDict[cur.spelling]["lastVarDeclLine"], lastVarDeclLine)   # 如果遍历到新的声明语句，更新信息
                else:
                    lastVarDeclDict[cur.spelling] = dict()
                    lastVarDeclDict[cur.spelling]["file"] = cur.location.file.name      # 记录函数中最后一个声明变量语句的位置信息，包含所在文件和其所在行
                    lastVarDeclDict[cur.spelling]["lastVarDeclLine"] = lastVarDeclLine
            self.traverseASTToGetLastVarDeclDict(cur, allFuncList, source_loc_list, lastVarDeclDict)

    def traverseFuncCursor(self, cursor):
        """遍历一个函数的AST, 获取其中最后一个变量声明语句所在位置

        Parameters
        ----------
        cursor : clang.cindex.Cursor
            根节点

        Returns
        -------
        [type]
            [description]

        Notes
        -----
        [description]
        """
        lastVarDeclLine = -1
        for cur in cursor.get_children():
            if cur.kind.is_declaration():       # 如果该节点是声明变量的结点, 更新位置信息
                lastVarDeclLine = cur.location.line
            newDeclLine = self.traverseFuncCursor(cur)  # 有时候在递归遍历时会遍历到最后一句声明语句，但有时候也遍历不到
            if newDeclLine != -1:                       # 如果遍历到了，则更新位置信息
                lastVarDeclLine = max(lastVarDeclLine, newDeclLine)
        if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL and lastVarDeclLine == -1:  # 如果函数只有一行，可能会导致分析结果为-1
            lastVarDeclLine = cursor.location.line
        return lastVarDeclLine


class instrumentMethod2BaseC99(instrumentMethod):
    # TODO extern "C" { ... }
    def instrument(self, source_loc_list, instrTemplate):
        """插装

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
        root_loc = os.path.dirname(source_loc_list[0])

        # 获取所有函数，下标决定了它的id
        # TODO 如果函数数量超过插装变量的位数量
        allFuncList = public.getAllFunctions(source_loc_list)
        instr_loc_list = list()
        for source in source_loc_list:
            index = clang.cindex.Index.create()
            tu = index.parse(source)
            instr_loc_list.append(self.instrumentBaseAST(tu.cursor, allFuncList, source, instrTemplate))

    def instrumentBaseAST(self, cursor, allFuncList, source, instrTemplate):
        """根据AST的内容进行插装

        Parameters
        ----------
        cursor : clang.cindex.Cursor
            根节点
        allFuncList : list
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
            if token.spelling in allFuncList:
                if token.spelling == "main":
                    continue
                idx = allFuncList.index(token.spelling)
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

        newSource = os.path.join(os.path.dirname(source), "ins_" + os.path.basename(source))
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
            print("Error occured in instrumentBaseAST:", e)
        return newSource


class instrumentMethod3BaseC99(instrumentMethod):
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
        cmd += file + " "
    cmd += "-o " + os.path.join(os.path.dirname(source_loc_list[0]), "instrument.exe -lws2_32")
    os.system(cmd)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
