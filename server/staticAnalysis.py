import os
import re
import uuid

import pycparser


# 变量无名异常
class VariableNoNameError(BaseException):
    pass


def findFunction(lineNum, source):
    '''
    @description: 根据行号寻找可疑代码所在函数
    @param {*} lineNum
    @param {*} source
    @return {*}
    '''
    brace = 0
    i = 0
    try:
        f = open(source, encoding="utf8")
        lines = f.readlines()
    except UnicodeDecodeError:
        f = open(source)
        lines = f.readlines()
    f.close()
    # 在到达可疑代码所在行前，最新检测到的函数就是可疑代码所在函数
    while i < lineNum:
        if brace == 0 and "(" in lines[i]:
            function = lines[i].split("(")[0].split(" ")[-1]
        if "{" in lines[i]:
            brace += 1
        if "}" in lines[i]:
            brace -= 1
        i += 1
    return function


def getSuspFunction(suspLoc, source_loc_list):
    '''
    @description: 获取可疑函数列表
    @param {*} suspLoc 可疑位置，格式形如main.c:14:15
    @param {*} sourceList 源文件列表，存储所有源文件位置的一个列表
    @return {*} 返回可疑函数的列表
    '''
    suspFunction = []
    for loc in suspLoc:
        for source in source_loc_list:
            if loc.split(":")[0] == source.split("/")[-1]:
                suspFunction.append(findFunction(int(loc.split(":")[1]), source))
    return suspFunction


def analyze(source_loc_str):
    '''
    @description: 通过cppcheck进行静态分析，获取可能有缺陷的代码及其所在行
    @param {*} source_loc_str
    @return {*}
    '''
    # TODO 或许可以根据clang分析出的AST的行号获取函数位置
    source_loc_list = source_loc_str.split("\n")
    for source in source_loc_list:
        if not os.path.exists(source):
            return "被测文件不存在!"
    suspCode = []
    suspLoc = []
    source = source_loc_list[0].split("/")[-1]
    path = re.sub(source, "", source_loc_list[0])  # 设定存储位置
    cmd = "cppcheck --output-file=" + path + "in/AnalyzeResult.txt " + re.sub("\n", " ", source_loc_str)
    os.system(cmd)
    f = open(path + "in/AnalyzeResult.txt")
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.replace("\\", "/")
        if "error:" in line:
            suspLoc.append(line.split(" error:")[0].split("/")[-1])
    suspFunction = getSuspFunction(suspLoc, source_loc_list)
    suspFunction = list(set(suspFunction))
    return suspFunction


def getAllStruct(header_loc_list):
    '''
    @description: 获取头文件中所有结构体的名称，header_loc_list是一个列表
    @param {*} header_loc_list 一个列表，里面存储了所有要解析的头文件的位置
    @return {*} 返回一个列表，列表里存储了所有结构体的名称
    '''
    allStruct = []
    # 获取所有头文件中结构体的名称
    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', r'-Iutils/fake_libc_include'])
        for decl in ast:
            # 如果当前decl是函数声明，不是结构体，则跳过
            if isinstance(decl.type, pycparser.c_ast.FuncDecl):
                continue
            allStruct.append(decl.name)
    result = []
    [result.append(s) for s in allStruct if not s in result]
    return result


def getOneStruct(header_loc_list, struct, prefix, allStruct):
    """获取一个结构体的数据内容

    Parameters
    ----------
    header_loc_list : list
        存储了所有头文件的位置
    struct : str
        要检查的结构体名称
    prefix : str
        前缀，当成员变量是结构体的时候会用到
    allStruct : list
        存储了头文件中所有结构体名称

    Returns
    -------
    list
        存储了要检查的结构体的所有信息

    Notes
    -----
    [description]
    """
    structInfo = []
    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', r'-Iutils/fake_libc_include'])
        for decl in ast:
            # 如果是函数声明，则跳过
            if isinstance(decl.type, pycparser.c_ast.FuncDecl):
                continue
            # 找到要获取数据的某个结构体后，进行遍历
            if decl.name == struct:
                for data in decl.type.type.decls:
                    info = ""
                    dataType = ""
                    try:
                        dataType = " ".join(data.type.type.names)
                        # 如果是没有名字的变量
                        if data.name is None:
                            data.name = "noName?" + str(uuid.uuid4()) + "?"
                        # 如果是普通的变量
                        info = dataType + " " + prefix + data.name
                    except AttributeError:
                        # 如果是二维数组
                        if isinstance(data.type.type, pycparser.c_ast.ArrayDecl):
                            dataType = " ".join(data.type.type.type.type.names)
                            info = dataType + " " + prefix + data.name + "[" + data.type.dim.value + "]" + "[" + data.type.type.dim.value + "]"
                        # 如果是一维数组
                        elif isinstance(data.type, pycparser.c_ast.ArrayDecl):
                            dataType = " ".join(data.type.type.type.names)
                            info = list()
                            for i in range(0, int(data.type.dim.value)):
                                info.append((dataType + " " + prefix + data.name + "[" + str(i) + "]", data.coord.file + "?" + str(data.coord.line)))
                        # 如果是结构体
                        elif isinstance(data.type.type, pycparser.c_ast.Struct):
                            info = analyzeInternalStruct(data.type.type.decls, prefix + data.name)
                    # 如果数据类型是定义的某个结构体，则递归查看信息
                    if dataType in allStruct:
                        # TODO 如果结构体成员是二维数组
                        if isinstance(data.type.type, pycparser.c_ast.ArrayDecl):
                            print("Need add code to analyze two-dimensional array...")
                        # 如果结构体成员是一维数组
                        elif isinstance(data.type, pycparser.c_ast.ArrayDecl):
                            print("Analyzing one-dimensional array...")
                            info = []
                            for i in range(int(data.type.dim.value)):
                                info.extend(
                                    getOneStruct(header_loc_list, dataType, prefix + data.name + "[" + str(i) + "].",
                                                 allStruct))
                        # 如果结构体成员不是数组
                        else:
                            info = getOneStruct(header_loc_list, dataType, prefix + data.name + ".", allStruct)
                    # 如果指定了bitsize(:n),则获取bitsize
                    if data.bitsize:
                        info += ":" + data.bitsize.value

                    # 加上变量所在的文件与行数
                    # 如果info内嵌结构体的返回信息，就不用再转换为元组了，因为已经是list(tuple(name, loc))
                    if data.coord is None:
                        info = (info, data.bitsize.coord.file + "?" + str(data.bitsize.coord.line))
                    elif isinstance(info, str):
                        info = (info, data.coord.file + "?" + str(data.coord.line))

                    if isinstance(info, tuple):
                        structInfo.append(info)
                    else:
                        structInfo.extend(info)
    # 可能是因为pycparser的特性，有的地方会重复分析
    # 目前没想到什么好的解决办法，只能通过遍历列表去掉重复的元素
    # result用于存储去重的structInfo
    result = []
    [result.append(info) for info in structInfo if not info in result]
    return result


def analyzeInternalStruct(decls, struct):
    """分析内嵌结构体的数据

    Parameters
    ----------
    decls : [type]
        pycparser解析来的数据，里面存储了各种变量名，类型等
    struct : str
        内嵌结构体外一层的结构体的名称

    Returns
    -------
    list
        返回内嵌结构体的成员变量列表

    Notes
    -----
    [description]
    """
    internalInfoList = []
    for data in decls:
        try:
            # 假如内嵌了无名变量
            if data.name is None:
                internalInfoList.append(
                    (" ".join(data.type.type.names) + " " + struct + ".noName?" + str(uuid.uuid4()) + "?:" + str(
                        data.bitsize.value),
                     data.bitsize.coord.file + "?" + str(data.bitsize.coord.line)))
                continue
            # 查看是否指定了bitsize
            # 将data的所在文件与行数的信息也加入到列表中
            if data.bitsize:
                internalInfoList.append(
                    (" ".join(data.type.type.names) + " " + struct + "." + data.name + ":" + str(data.bitsize.value),
                     data.coord.file + "?" + str(data.coord.line)))
            else:
                internalInfoList.append(
                    (" ".join(data.type.type.names) + " " + struct + "." + data.name,
                     data.coord.file + "?" + str(data.coord.line)))
        except AttributeError:
            try:
                # 这里作一下判断，因为内嵌结构体的时候有两种写法
                # 第一个if适用的内嵌结构体的形式是 struct Test{ ... };
                if isinstance(data.type, pycparser.c_ast.Struct):
                    internalInfoList.extend(analyzeInternalStruct(data.type.decls, struct + "." + data.type.name))
                # 第二个if适用的内嵌结构体的形式是 struct { ... }Test;
                elif isinstance(data.type.type, pycparser.c_ast.Struct):
                    internalInfoList.extend(analyzeInternalStruct(data.type.type.decls, struct + "." + data.name))
            except AttributeError:
                print("error!")
    return internalInfoList


def analyzeHeader(header_loc_list):
    '''
    @description: 通过pycparser获取AST分析头文件。
                注意：pycparser只能分析头文件，分析c文件时会出错; 定义结构体时最好把结构体名写在大括号后面。
    @param {*} header_loc_list 头文件位置列表，可以是一个也可以是多个
    @return {*} 返回类型是列表内嵌元组，每个元组是一个结构体。元组第一个元素是结构体名称
    '''
    infoList = []
    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', r'-Iutils/fake_libc_include'])
        # ast.show()
        info = ""
        for decl in ast:
            # print(decl)
            if isinstance(decl.type, pycparser.c_ast.FuncDecl):
                continue
            print("==================" + decl.name + "==================")
            tempList = []
            tempList.append(decl.name)
            for data in decl.type.type.decls:
                info = ""
                dataType = ""
                try:
                    # 如果是普通的变量
                    dataType = " ".join(data.type.type.names)
                    info = dataType + " " + data.name
                except AttributeError:
                    # 如果是二维数组
                    if isinstance(data.type.type, pycparser.c_ast.ArrayDecl):
                        dataType = " ".join(data.type.type.type.type.names)
                        info = dataType + " " + data.name + "[" + data.type.dim.value + "]" + "[" + data.type.type.dim.value + "]"
                    # 如果是一维数组
                    elif isinstance(data.type, pycparser.c_ast.ArrayDecl):
                        dataType = " ".join(data.type.type.type.names)
                        info = dataType + " " + data.name + "[" + data.type.dim.value + "]"
                    # 如果是结构体
                    elif isinstance(data.type.type, pycparser.c_ast.Struct):
                        info = analyzeInternalStruct(data.type.type.decls, data.name)
                # 如果指定了bitsize(:n),则获取bitsize
                if data.bitsize:
                    info += ":" + data.bitsize.value
                if isinstance(info, str):
                    tempList.append(info)
                else:
                    tempList.extend(info)
            infoList.append(tuple(tempList))
    return infoList


import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
