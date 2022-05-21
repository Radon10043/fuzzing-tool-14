from PyQt5 import QtWidgets
import sys
import os
import re
import subprocess
import uuid

import pycparser.c_ast
import clang.cindex


# 变量无名异常
class VariableNoNameError(BaseException):
    pass


def findFunction(lineNum, source):
    """根据行号寻找可疑代码所在函数

    Parameters
    ----------
    lineNum : int
        可疑代码所在行
    source : str
        源文件路径

    Returns
    -------
    [type]
        [description]

    Notes
    -----
    [description]
    """
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


def analyze(source_loc_str):
    """通过cppcheck进行静态分析，获取可能有缺陷的代码及其所在行
    根据可疑代码所在行遍历AST获取可疑函数

    Parameters
    ----------
    source_loc_str : str
        源文件地址

    Returns
    -------
    list
        可疑函数列表

    Notes
    -----
    [description]
    """
    source_loc_list = source_loc_str.split("\n")
    for source in source_loc_list:
        if not os.path.exists(source):
            return "被测文件不存在!"

    path = os.path.dirname(source_loc_list[0])  # 设定存储位置
    if not os.path.exists(os.path.join(path, "in")):
        os.mkdir(os.path.join(path, "in"))

    # 运行cppcheck
    suspLoc = []
    cmd = "cppcheck --output-file=" + os.path.join(path, "in", "AnalyzeResult.txt") + " " + re.sub("\n", " ", source_loc_str)
    os.system(cmd)
    f = open(os.path.join(path, "in", "AnalyzeResult.txt"))
    lines = f.readlines()
    f.close()
    for line in lines:
        if "error:" in line:
            suspLoc.append(line.split(": error:")[0])

    # 遍历ast, 获取可疑函数
    obj = analyzeCpp()
    funcList, funcDict = obj.getAllCppFuncs(source_loc_list)
    suspFuncList = list()  # 可疑函数列表
    for loc in suspLoc:
        suspFunc = "ERROR!"
        splitList = loc.split(":")
        path = splitList[0] + ":" + splitList[1]  # 可疑代码所在文件路径
        lineNum = int(splitList[2])  # 可疑代码行号
        minDistance = -1  # 取函数行号小于可疑代码行号，且距离可疑代码最短的函数为可疑代码所在函数
        for key, value in funcDict.items():
            if path in value.keys():
                if value[path] < lineNum and minDistance == -1:
                    minDistance = lineNum - value[path]
                    suspFunc = key
                elif value[path] < lineNum and lineNum - value[path] < minDistance:
                    minDistance = lineNum - value[path]
                    suspFunc = key
        suspFuncList.append(suspFunc)
    return suspFuncList


def getAllStruct_clang(header_loc_list):
    """获得所有头文件中所有结构体信息

    Parameters
    ----------
    header_loc_list : list
        头文件列表

    Returns
    -------
    list
        二位列表，存储了所有头文件中结构体信息
        [0]是结构体名字，剩下的是别名

    Notes
    -----
    [description]
    """
    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = os.path.join(os.path.dirname(libclangPath), "libclang.dll")
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    # 获取所有结构体
    structTwoDimList = list()
    for header in header_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(header)
        headerstructTwoDimList = traverseASTToGetAllStruct(tu.cursor)
        # 去重
        [structTwoDimList.append(struct) for struct in headerstructTwoDimList if not struct in structTwoDimList]

    return structTwoDimList


def traverseASTToGetAllStruct(cursor):
    """遍历AST获得一个文件中的所有结构体信息

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        根节点

    Returns
    -------
    list
        一个文件中结构体的所有信息
        二维列表，每个列表中第一个元素表示第一个名字，剩下的是别名

    Notes
    -----
    [description]
    """
    struct = list()
    headerStructList = list()
    for cur in cursor.get_children():
        if cur.kind == clang.cindex.CursorKind.STRUCT_DECL:
            if len(struct) > 0:
                headerStructList.append(struct.copy())
                struct.clear()
            struct.append(cur.spelling)
            print(cur.spelling, ",", cur.kind)
        elif cur.kind == clang.cindex.CursorKind.TYPEDEF_DECL:
            struct.append(cur.spelling)
    headerStructList.append(struct)
    return headerStructList


def getAllStruct(header_loc_list):
    """获取头文件中所有结构体的名称，header_loc_list是一个列表

    Parameters
    ----------
    header_loc_list : list
        里面存储了所有要解析的头文件的位置

    Returns
    -------
    list
        列表里存储了所有结构体的名称

    Notes
    -----
    [description]
    """
    allStruct = list()
    fake_lib_loc = os.path.dirname(os.path.abspath(__file__))
    fake_lib_loc = os.path.join(fake_lib_loc, "fake_lib", "fake_libc_include")

    # 获取所有头文件中结构体的名称
    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', '-I' + fake_lib_loc])
        for decl in ast:
            # 如果当前decl不是结构体，则跳过
            try:
                decl.type.type.coord.file = decl.type.type.coord.file.replace("\\\\", "\\")
                if isinstance(decl.type.type, pycparser.c_ast.Struct) and decl.type.type.coord.file == header:
                    allStruct.append(decl.name)
            except:
                continue
    result = []
    [result.append(s) for s in allStruct if not s in result]
    return result


def getTypedefDict(header_loc_list):
    """获取源程序中typedef的信息

    Parameters
    ----------
    header_loc_list : list
        头文件列表

    Returns
    -------
    dict
        typedef信息字典，key是别名，value是声明
        即 typedef [value] [key]

    Notes
    -----
    [description]
    """
    typedefDict = dict()

    # 获取typedef相关信息
    fake_lib_loc = os.path.dirname(os.path.abspath(__file__))
    fake_lib_loc = os.path.join(fake_lib_loc, "fake_lib", "fake_libc_include")
    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', '-I' + fake_lib_loc])
        for decl in ast:
            try:
                if isinstance(decl.type.type, pycparser.c_ast.IdentifierType):
                    typedefDict[decl.name] = " ".join(decl.type.type.names)
            except:
                continue

    return typedefDict


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
    structInfo = list()
    fake_lib_loc = os.path.dirname(os.path.abspath(__file__))
    fake_lib_loc = os.path.join(fake_lib_loc, "fake_lib", "fake_libc_include")

    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', '-I' + fake_lib_loc])
        for decl in ast:
            # 如果不是结构体，则跳过
            try:
                if not isinstance(decl.type.type, pycparser.c_ast.Struct):
                    continue
            except:
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
                            info = list()
                            for i in range(int(data.type.dim.value)):
                                for j in range(int(data.type.type.dim.value)):
                                    info.append((dataType + " " + prefix + data.name + "[" + str(i) + "][" + str(j) + "]",
                                                 data.coord.file + "?" + str(data.coord.line)))
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
                                info.extend(getOneStruct(header_loc_list, dataType, prefix + data.name + "[" + str(i) + "].", allStruct))
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
                internalInfoList.append((" ".join(data.type.type.names) + " " + struct + ".noName?" + str(uuid.uuid4()) + "?:" + str(data.bitsize.value),
                                         data.bitsize.coord.file + "?" + str(data.bitsize.coord.line)))
                continue
            # 查看是否指定了bitsize
            # 将data的所在文件与行数的信息也加入到列表中
            if data.bitsize:
                internalInfoList.append((" ".join(data.type.type.names) + " " + struct + "." + data.name + ":" + str(data.bitsize.value),
                                         data.coord.file + "?" + str(data.coord.line)))
            else:
                internalInfoList.append((" ".join(data.type.type.names) + " " + struct + "." + data.name, data.coord.file + "?" + str(data.coord.line)))
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
    """通过pycparser获取AST分析头文件

    Parameters
    ----------
    header_loc_list : list
        头文件位置列表，可以是一个也可以是多个

    Returns
    -------
    list
        列表内嵌元组，每个元组是一个结构体。元组第一个元素是结构体名称

    Notes
    -----
    [description]
    """
    infoList = []
    for header in header_loc_list:
        ast = pycparser.parse_file(header, use_cpp=True, cpp_path='clang', cpp_args=['-E', r'-Iutils\fake_libc_include'])
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
                        info = dataType + " " + data.name + \
                            "[" + data.type.dim.value + "]" + \
                            "[" + data.type.type.dim.value + "]"
                    # 如果是一维数组
                    elif isinstance(data.type, pycparser.c_ast.ArrayDecl):
                        dataType = " ".join(data.type.type.type.names)
                        info = dataType + " " + data.name + \
                            "[" + data.type.dim.value + "]"
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
        libclangPath = os.path.join(libclangPath, "libclang.dll")  # 获得libclang的地址
        if clang.cindex.Config.loaded == True:
            print("clang.cindex.Config.loaded == True:")
        else:
            clang.cindex.Config.set_library_file(libclangPath)
            print("install path")

        funcSet = set()  # 存储所有函数的集合
        funcDict = dict()  # 存储函数信息的字典 <函数名, <所在文件, 行>>
        index = clang.cindex.Index.create()
        for source in source_loc_list:
            tu = index.parse(source)
            self.preorderTraverse(tu.cursor, source, funcSet, funcDict)  # 前序遍历AST获得所有函数名称
        funcList = sorted(list(funcSet))  # 函数名称存入funcList
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
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
