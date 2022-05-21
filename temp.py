'''
Author: Radon
Date: 2021-08-26 11:20:37
LastEditors: Radon
LastEditTime: 2022-01-10 10:26:35
Description: Hi, say something
'''

from client.staticAnalysis import analyze
import server.public

import clang.cindex
import subprocess
import os
import re
import socket
import traceback
import pycparser
import ctypes
# import matplotlib.pyplot as plt
import numpy as np
import sys
import struct


def getAllStruct(header_loc_list):
    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split("\\")[-1], "", libclangPath) + "libclang.dll"
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    # 获取所有结构体
    structList = list()
    for header in header_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(header)
        headerStructList = traverseASTToGetAllStruct(tu.cursor)
        [structList.append(struct) for struct in headerStructList if not struct in structList]

    print(structList)
    return structList


def traverseASTToGetAllStruct(cursor):
    temp = list()
    headerStructList = list()
    for cur in cursor.get_children():
        if cur.kind == clang.cindex.CursorKind.STRUCT_DECL:
            if len(temp) > 0:
                headerStructList.append(temp.copy())
                temp.clear()
            temp.append(cur.spelling)
            print(cur.spelling, ",", cur.kind)
        elif cur.kind == clang.cindex.CursorKind.TYPEDEF_DECL:
            temp.append(cur.spelling)
    headerStructList.append(temp)
    return headerStructList


def analyzeStruct(header_loc_list, structName):
    # TODO 识别是否别名
    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split("\\")[-1], "", libclangPath) + "libclang.dll"
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    # 获取所有结构体
    structList = list()
    for header in header_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(header)
        traverseASTToAnalyzeOneStruct(tu.cursor, structName, "")


def traverseASTToAnalyzeOneStruct(cursor, structName, nowStruct):
    for cur in cursor.get_children():
        if cur.kind == clang.cindex.CursorKind.STRUCT_DECL:
            nowStruct = cur.spelling
        elif cur.kind == clang.cindex.CursorKind.FIELD_DECL and nowStruct == structName:
            print(cur.type.spelling + " " + cur.spelling, end="")
            if cur.is_bitfield():
                print(" :", cur.get_bitfield_width(), end="")
            print()
        traverseASTToAnalyzeOneStruct(cur, structName, nowStruct)

    # for cur in cursor.get_tokens():
    #     print(cur.spelling, ",", cur.kind)
    #     traverseASTToAnalyzeOneStruct(cur)


def traverseByPyc(header_loc):
    ast = pycparser.parse_file(header_loc, use_cpp=True, cpp_path='clang', cpp_args=['-E', '-I./fake_lib'])
    for decl in ast:
        pass
    print()


def instrumentMethod2(source_loc_list, dataType, dataName):
    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split("\\")[-1], "", libclangPath) + "libclang.dll"
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    funcList = server.public.getAllFunctions(source_loc_list)
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
        initInstrVar(tu.cursor, lines, funcList, initGlobalVar, dataType, dataName)
        instrumentSource(tu.cursor, source, lines, funcList, dataName)
        initGlobalVar = False


def initInstrVar(cursor, lines, funcList, initGlobalVar, dataType, dataName):
    for cur in cursor.get_children():
        if cur.kind == clang.cindex.CursorKind.FUNCTION_DECL and cur.spelling in funcList and os.path.splitext(cur.location.file.name)[-1] != ".h":
            if initGlobalVar:
                lines[cur.location.line - 1] = dataType + " " + \
                    dataName + " = 0;" + lines[cur.location.line - 1]
            else:
                lines[cur.location.line - 1] = "extern " + dataType + \
                    " " + dataName + ";" + lines[cur.location.line - 1]
            return


def instrumentSource(cursor, source, lines, funcList, dataName):
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

    f = open(os.path.join(os.path.dirname(source), "ins_" + os.path.basename(source)), mode="w")
    for line in lines:
        f.write(line)
    f.close()


def test():
    # 大小端转换
    # 大端 0x21436587 ->
    # 小端 0x87654321
    # 参考资料: https://blog.csdn.net/weiwangchao_/article/details/80395941
    value = chr(49)
    value = bytes(value, encoding="utf8")
    result = struct.unpack('<c', struct.pack('c', value))[0]
    result = ord(result)
    return


def instrumentAfterDeclare(source_loc_list):
    # Load dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split("\\")[-1], "", libclangPath) + "libclang.dll"
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    lastVarDeclDict = dict()  # <string, int>
    for source in source_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(source)
        allFuncList = server.public.getAllFunctions(source_loc_list)
        traverseASTToGetLastVarDeclDict(tu.cursor, allFuncList, source_loc_list, lastVarDeclDict)
    return lastVarDeclDict


def traverseASTToGetLastVarDeclDict(cursor, allFuncList, source_loc_list, lastVarDeclDict):
    for cur in cursor.get_children():
        if cur.spelling in allFuncList and cur.location.file.name in source_loc_list:
            lastVarDeclLine = traverseFuncCursor(cur)
            if cur.spelling in lastVarDeclDict.keys():
                lastVarDeclDict[cur.spelling]["lastVarDeclLine"] = max(lastVarDeclDict[cur.spelling]["lastVarDeclLine"], lastVarDeclLine)
            else:
                lastVarDeclDict[cur.spelling] = dict()
                lastVarDeclDict[cur.spelling]["file"] = cur.location.file.name
                lastVarDeclDict[cur.spelling]["lastVarDeclLine"] = lastVarDeclLine
        traverseASTToGetLastVarDeclDict(cur, allFuncList, source_loc_list, lastVarDeclDict)


def traverseFuncCursor(cursor):
    lastVarDeclLine = -1
    for cur in cursor.get_children():
        if cur.kind.is_declaration():  # 如果该节点是声明变量的结点, 更新位置信息
            lastVarDeclLine = cur.location.line
        newDeclLine = traverseFuncCursor(cur)  # 有时候在递归遍历时会遍历到最后一句声明语句，但有时候也遍历不到
        if newDeclLine != -1:  # 如果遍历到了，则更新位置信息
            lastVarDeclLine = max(lastVarDeclLine, newDeclLine)
    if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL and lastVarDeclLine == -1:
        lastVarDeclLine = cursor.location.line
    return lastVarDeclLine


def test(source_loc_list):
    # Load dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = re.sub(libclangPath.split("\\")[-1], "", libclangPath) + "libclang.dll"
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    allFuncList = server.public.getAllFunctions(source_loc_list)
    allFuncLocDict = dict()
    index = clang.cindex.Index.create()
    tu = index.parse(source_loc_list[0])
    traverse(tu.cursor, allFuncList, allFuncLocDict)
    return allFuncLocDict


def traverse(cursor, allFuncList, allFuncLocDict):
    for cur in cursor.get_children():
        if cur.spelling in allFuncList:
            if not cur.spelling in allFuncLocDict.keys():
                allFuncLocDict[cur.spelling] = dict()
                allFuncLocDict[cur.spelling]["file"] = cur.location.file.name
                allFuncLocDict[cur.spelling]["line"] = cur.location.line
            else:
                allFuncLocDict[cur.spelling]["file"] = cur.location.file.name
                allFuncLocDict[cur.spelling]["line"] = cur.location.line
        traverse(cur, allFuncList, allFuncLocDict)


class analyzeCpp:
    def getAllCppFuncs(self, source_loc_list: list):
        """分析cpp文件，获得所有函数

        Parameters
        ----------
        source_loc_list : list
            源文件

        Returns
        -------
        list, dict
            list: 所有函数名
            dict: 函数信息字典, <函数名, <所在文件, 行>>

        Notes
        -----
        [description]
        """
        libclangPath = subprocess.getstatusoutput("where clang")[1]
        libclangPath = os.path.dirname(libclangPath)
        libclangPath = os.path.join(libclangPath, "libclang.dll")   # 获得libclang的地址
        if clang.cindex.Config.loaded == True:
            print("clang.cindex.Config.loaded == True:")
        else:
            clang.cindex.Config.set_library_file(libclangPath)
            print("install path")

        funcSet = set() # 存储所有函数的集合
        funcDict = dict()   # 存储函数信息的字典 <函数名, <所在文件, 行>>
        index = clang.cindex.Index.create()
        for source in source_loc_list:
            tu = index.parse(source)
            self.preorderTraverse(tu.cursor, source, funcSet, funcDict)   # 前序遍历AST获得所有函数名称
        funcList = sorted(list(funcSet))    # 函数名称存入funcList
        return funcList, funcDict


    def preorderTraverse(self, cursor: clang.cindex.Cursor, source: str, funcSet: set, funcDict: dict):
        """前序遍历AST，更新函数集合funcSet

        Parameters
        ----------
        cursor : clang.cindex.Cursor
            根节点
        source : str
            源文件
        funcSet : set
            函数集合
        funcDict : dict
            函数字典, <函数名, <所在文件, 行>>

        Notes
        -----
        [description]
        """
        for cur in cursor.get_children():
            if cur.location.file and cur.location.file.name == source:
                if cur.kind == clang.cindex.CursorKind.CXX_METHOD or cur.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                    funcSet.add(cur.spelling)
                    funcDict[cur.spelling] = dict()
                    funcDict[cur.spelling][cur.location.file.name] = cur.location.line
            self.preorderTraverse(cur, source, funcSet, funcDict)



if __name__ == "__main__":
    fake_lib_loc = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    fake_lib_loc += "/fake_lib/fake_libc_include"
    header_loc_list = ["C:/Users/Radon/Desktop/fuzztest/test/Datagram.h", "C:/Users/Radon/Desktop/fuzztest/test/Trajectory.h"]
    source_loc_list = [r"C:\Users\Radon\Desktop\fuzztest\CommuExample4\main.cpp"]
    # source_loc_list = ["test.cpp"]

    obj = analyzeCpp()
    funcList, funcDict = obj.getAllCppFuncs(source_loc_list)
    del obj
    print(funcList)

    # instrumentMethod2(source_loc_list, "unsigned long long", "instr")
    # getAllStruct(header_loc_list)
    # analyzeStruct(header_loc_list, "Trajectory")