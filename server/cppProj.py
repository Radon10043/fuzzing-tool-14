'''
Author: Radon
Date: 2022-04-12 11:56:47
LastEditors: Radon
LastEditTime: 2022-06-04 20:32:31
Description: Hi, say something
'''
import clang.cindex
import subprocess
import os
import queue

import staticAnalysis as sa

# yapf: disable
# ========== GLOBAL VARIABLE ==========
GLB_STRUCT_HASH     = 1145141919810         # 结构体HASH, 用于在遍历AST时确定结构体的名称和其别名
GLB_AST_LIST        = list()                # or dict? <filename, cursor>
GLB_STRUCT_DICT     = dict()                # key: hash, value: structs
GLB_STRUCT_QUEUE    = queue.Queue()         # 队列
GLB_STRUCT_INFO     = list()                # list(tuple(name, loc))
GLB_TEMP_DICT       = dict()
GLB_PREFIX          = ""                    # 结构体前缀
# =====================================
# yapf: enable


def preTravFunc(cursor: clang.cindex.Cursor, funcList: list, srcList: list):
    """遍历AST, 获取所有函数信息

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        树的结点?
    funcList : list
        函数列表
    srcList : list
        源文件列表

    Notes
    -----
    _description_
    """
    for cur in cursor.get_children():
        try:
            if cur.location.file and cur.location.file.name in srcList:

                # 如果节点类型是函数, 就加入到函数列表中
                if cur.kind == clang.cindex.CursorKind.CXX_METHOD or cur.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                    funcList.append(cur.spelling)

        except:
            pass
        preTravFunc(cur, funcList, srcList)


def getAllFunc(srcList: list) -> list:
    """获取所有函数

    Parameters
    ----------
    srcList : list
        源文件列表

    Returns
    -------
    list
        包含所有函数的列表

    Notes
    -----
    _description_
    """
    # 加载dll
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = os.path.join(os.path.dirname(libclangPath), "libclang.dll")
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    # 获取所有函数
    funcList = list()
    for src in srcList:
        index = clang.cindex.Index.create()
        tu = index.parse(src)
        preTravFunc(tu.cursor, funcList, srcList)
    funcList = sorted(set(funcList))

    # 返回包含所有函数名的列表
    return funcList


def preTravStruct(cursor: clang.cindex.Cursor, headerList: list, structList: list, structDict: dict):
    """获取所有结构体及其别名

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        AST的结点?
    headerList : list
        头文件列表
    structList : list
        结构体列表, 格式如下:
        structList[i][0]是结构体的名称, struct[i][1 - (n-1)]是结构体的别名
        structList[i][0]可能为空字符串 ( typedef struct { ... } name )
    structDicyt: dict
        结构体字典, key是STURCT_DECL的HASH, value是结构体名称和别名

    Notes
    -----
    _description_
    """

    global GLB_STRUCT_HASH, GLB_TEMP_DICT

    for cur in cursor.get_children():

        if cur.hash in GLB_TEMP_DICT.keys():
            GLB_TEMP_DICT[cur.hash].append((cur.type.spelling, cur.spelling))
        else:
            GLB_TEMP_DICT[cur.hash] = [(cur.type.spelling, cur.spelling)]

        # 根据节点的hash值确定结构体的名称, 当hash值和之前不一样时证明遍历到了新的结构体
        if cur.kind == clang.cindex.CursorKind.STRUCT_DECL and cur.hash != GLB_STRUCT_HASH:

            # 更新HASH并追加列表
            GLB_STRUCT_HASH = cur.hash
            structList.append(list())
            structList[-1].append(cur.spelling)

            # HASH与结构体名称存入字典
            structDict[GLB_STRUCT_HASH] = structList[-1]

        # 若hash值和之前一样, 证明还在当前结构体里
        elif cur.kind == clang.cindex.CursorKind.TYPEDEF_DECL and cur.underlying_typedef_type.kind == clang.cindex.TypeKind.ELABORATED:  # ELABORATED?
            structList[-1].append(cur.spelling)

        # preTravStruct(cur, headerList, structList, structDict)


def getAllStruct(headerList: list) -> list:
    """获取所有结构体及其别名

    Parameters
    ----------
    headerList : list
        头文件列表

    Returns
    -------
    list
        结构体列表

    Notes
    -----
    _description_
    """

    global GLB_STRUCT_DICT

    # structList是一个二维列表, structList[i][0]是结构体的名称, struct[i][1 - (n-1)]是结构体的别名. 因此, [i][0]可能为空字符串
    structList = list()

    # structDict是一个字典, key是结构体STRUCT_DECL节点的哈希值, value是其对应的结构体名与别名list
    structDict = dict()

    for cursor in GLB_AST_LIST:
        preTravStruct(cursor, headerList, structList, structDict)

    GLB_STRUCT_DICT = structDict

    return structList


def analyzeInterStruct(cursor: clang.cindex.Cursor):
    for cur in cursor.get_children():
        print(cur.spelling)
        analyzeInterStruct(cur)


def preTravOneStruct(cursor: clang.cindex.Cursor):
    """遍历节点获取一个结构体的信息

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        节点

    Notes
    -----
    _description_
    """
    global GLB_STRUCT_QUEUE, GLB_STRUCT_INFO, GLB_PREFIX

    recursion = False       # 是否递归的标志
    recurCur = cursor       # 要递归遍历的节点

    for cur in cursor.get_children():

        bitsize = cur.get_bitfield_width()

        # 判断变量是否为数组
        varTypeList = cur.type.spelling.split()
        arrLen = 0
        if cur.type.kind == clang.cindex.TypeKind.CONSTANTARRAY:
            arrLen = varTypeList.pop(-1)
            arrLen = arrLen.lstrip("[").rstrip("]")  # arrLen是数组长度

        # 将arrLen转换为int类型, 目前只支持一维数组
        try:
            arrLen = int(arrLen)
        except:
            print("High dim arr?")
            continue

        # 查看一个变量是不是结构体变量
        varType = " ".join(varTypeList)  # 获取变量类型
        isStructVar = False
        for k, v in GLB_STRUCT_DICT.items():  # 查看变量类型是否能在GLB_STRUCT_DICT中找到
            if varType in v:  # 如果能找到, 证明是结构体变量, 加入队列作为待分析的对象

                if arrLen:  # 如果是结构体数组的话, 依次加入队列
                    for i in range(arrLen):
                        GLB_STRUCT_QUEUE.put((k, GLB_PREFIX + cur.spelling + "[" + str(i) + "]"))
                else:
                    GLB_STRUCT_QUEUE.put((k, GLB_PREFIX + cur.spelling))

                isStructVar = True

        # 如果结构体里嵌套了结构体, 要递归分析 ... struct { struct {} }
        if recursion:
            GLB_PREFIX += cur.spelling + "."
            preTravOneStruct(recurCur)
            GLB_PREFIX = GLB_PREFIX[:(0 - len(cur.spelling) - 1)]
            recursion = False
            continue

        # 遇到嵌套时, 本次不递归, 下次获得结构体名字后递归
        if "struct " in cur.type.spelling:
            recursion = True
            recurCur = cur

        # 获取位置
        filename = cur.location.file.name
        line = cur.location.line
        loc = filename + "?" + str(line)

        # 若不是结构体变量, 正常分析
        if not isStructVar and cur.kind == clang.cindex.CursorKind.FIELD_DECL:
            var = varType + " " + GLB_PREFIX + cur.spelling

            # 若用户指定了位大小
            if bitsize != -1:
                var += ":" + str(bitsize)

            if arrLen:  # 如果是数组的话, 依次加入GLB_STRUCT_INFO
                for i in range(arrLen):
                    GLB_STRUCT_INFO.append((var + "[" + str(i) + "]", loc))
            else:
                GLB_STRUCT_INFO.append((var, loc))


def findStruct(cursor: clang.cindex.Cursor, structHash: int):
    """在cursor中寻找和目标结构体hash能对应的节点, 找到后遍历ast

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        ast的节点
    structHash : int
        要分析的结构体的hash

    Notes
    -----
    _description_
    """
    for cur in cursor.get_children():
        if cur.kind == clang.cindex.CursorKind.STRUCT_DECL and cur.hash == structHash:
            preTravOneStruct(cur)


def analyzeOneStruct(structName: str) -> list:
    """分析一个结构体, 获取所有变量的信息

    Parameters
    ----------
    structDict : dict
        key是hash, value是结构体所有名字的dict
    structHash : int
        要分析的结构体的hash

    Returns
    -------
    list
        存储所有结构体变量的list?

    Notes
    -----
    _description_
    """
    # 全局变量用于帮助分析嵌套结构体
    global GLB_STRUCT_DICT, GLB_STRUCT_QUEUE, GLB_PREFIX

    GLB_PREFIX = ""

    for k, v in GLB_STRUCT_DICT.items():
        if structName in v:
            structHash = k

    GLB_STRUCT_QUEUE.put((structHash, GLB_PREFIX))

    structInfo = list()

    # 在分析结构体过程中, 遇到结构体变量时, 其结构体对应的hash和前缀会存入GLB_STRUCT_QUEUE
    # 根据嵌套层数的不同分别进行分析 (有点像bfs?)
    while not GLB_STRUCT_QUEUE.empty():
        n = GLB_STRUCT_QUEUE.qsize()

        while n:
            n -= 1

            qTuple = GLB_STRUCT_QUEUE.get()
            nextHash = qTuple[0]
            GLB_PREFIX = qTuple[1]
            if len(GLB_PREFIX):  # 前缀不为空时, 加个 .
                GLB_PREFIX += "."

            # 遍历所有header的AST, 找到了对应结构体的节点后就进行分析
            for cursor in GLB_AST_LIST:
                findStruct(cursor, nextHash)

    rawStructInfo = GLB_STRUCT_INFO.copy()

    # 去重
    infoSet = set()
    for tup in rawStructInfo:
        if tup[0] in infoSet:
            continue
        infoSet.add(tup[0])
        structInfo.append(tup)

    return structInfo


def getAllHeaders(root: str) -> list:
    """获取根目录下所有头文件的绝对地址

    Parameters
    ----------
    root : str
        根目录地址

    Returns
    -------
    list
        存储所有头文件绝对地址的列表

    Notes
    -----
    _description_
    """
    headerList = list()

    q = queue.Queue()  # 队列用于存储文件夹的地址
    q.put(root)

    while not q.empty():
        path = q.get()
        for f in os.listdir(path):
            nf = os.path.join(path, f)
            if os.path.isdir(nf):  # 如果遍历到的东西是文件夹, 加入队列, 遍历它里面的内容寻找头文件
                q.put(nf)
            elif nf.endswith(".h"):  # 遍历到的东西是头文件的话, 加入列表
                headerList.append(nf)

    return headerList


def getAllCSrcs(root: str) -> list:
    """获取根目录下所有C文件的绝对地址

    Parameters
    ----------
    root : str
        根目录地址

    Returns
    -------
    list
        存储所有[.c]文件绝对地址的列表

    Notes
    -----
    _description_
    """
    srcList = list()

    q = queue.Queue()  # 队列用于存储文件夹的地址
    q.put(root)

    while not q.empty():
        path = q.get()
        for f in os.listdir(path):
            nf = os.path.join(path, f)
            if os.path.isdir(nf):  # 如果遍历到的东西是文件夹, 加入队列, 遍历它里面的内容寻找头文件
                q.put(nf)
            elif nf.endswith(".c"):  # 遍历到的东西是头文件的话, 加入列表
                srcList.append(nf)

    return srcList


def getAllCppSrcs(root: str) -> list:
    """获取根目录下所有Cpp文件的绝对地址

    Parameters
    ----------
    root : str
        根目录地址

    Returns
    -------
    list
        存储所有[.cc],[.cpp],[.cxx]文件绝对地址的列表

    Notes
    -----
    _description_
    """
    srcList = list()

    q = queue.Queue()  # 队列用于存储文件夹的地址
    q.put(root)

    while not q.empty():
        path = q.get()
        for f in os.listdir(path):
            nf = os.path.join(path, f)
            if os.path.isdir(nf):  # 如果遍历到的东西是文件夹, 加入队列, 遍历它里面的内容寻找头文件
                q.put(nf)
            elif nf.endswith(".cpp") or nf.endswith(".cxx") or nf.endswith(".cc"):  # 遍历到的东西是头文件的话, 加入列表
                srcList.append(nf)

    return srcList


def prevTravTypedef(cursor: clang.cindex.Cursor, typedefDict: dict):
    """遍历ast, 获取typedef变量的信息

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        节点
    typedefDict : dict
        字典

    Notes
    -----
    _description_
    """
    invalidSet = {clang.cindex.TypeKind.ELABORATED, clang.cindex.TypeKind.INVALID}
    for cur in cursor.get_children():
        if not cur.underlying_typedef_type.kind in invalidSet:
            typedefDict[cur.spelling] = cur.underlying_typedef_type.spelling


def getTypedefDict() -> dict:
    """获取typedefDict
    key: 别名, value: 原名

    Returns
    -------
    dict
        key: 别名, value: 原名

    Notes
    -----
    _description_
    """
    typedefDict = dict()
    for cursor in GLB_AST_LIST:
        prevTravTypedef(cursor, typedefDict)
    return typedefDict


def init(headerList: list):
    """初始化

    Parameters
    ----------
    headerList : list
        _description_

    Notes
    -----
    _description_
    """
    global GLB_AST_LIST

    GLB_AST_LIST = list()

    # init
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = os.path.join(os.path.dirname(libclangPath), "libclang.dll")
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")

    # 获取所有ast
    for header in headerList:
        index = clang.cindex.Index.create()
        tu = index.parse(header)
        GLB_AST_LIST.append(tu.cursor)


if __name__ == '__main__':
    root = r"C:\Users\77257\Desktop\example\example"

    srcList = getAllCppSrcs(root)
    headerList = getAllHeaders(root)

    # STEP 0: init
    libclangPath = subprocess.getstatusoutput("where clang")[1]
    libclangPath = os.path.join(os.path.dirname(libclangPath), "libclang.dll")
    if clang.cindex.Config.loaded == True:
        print("clang.cindex.Config.loaded == True:")
    else:
        clang.cindex.Config.set_library_file(libclangPath)
        print("install path")
    init(headerList)

    # STEP 1: 获取所有结构体
    structList = getAllStruct(headerList)

    tDict = getTypedefDict()

    # STEP 2: 获取指定结构体内容
    analyzeOneStruct("Datagram")

    print("Hm?")