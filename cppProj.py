'''
Author: Radon
Date: 2022-04-12 11:56:47
LastEditors: Radon
LastEditTime: 2022-05-21 14:54:33
Description: Hi, say something
'''
import clang.cindex
import subprocess
import os
import queue

# yapf: disable
# ========== GLOBAL VARIABLE ==========
GLB_STRUCT_HASH     = 1145141919810         # 结构体HASH, 用于在遍历AST时确定结构体的名称和其别名
GLB_AST_LIST        = list()                # or dict? <filename, cursor>
GLB_STRUCT_DICT     = dict()                # key: hash, value: structs
GLB_STRUCT_QUEUE    = queue.Queue()         # 队列
GLB_STRUCT_INFO     = list()                # 存储结构体各变量信息的list
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

    global GLB_STRUCT_HASH

    for cur in cursor.get_children():

        # 根据节点的hash值确定结构体的名称, 当hash值和之前不一样时证明遍历到了新的结构体
        if cur.kind == clang.cindex.CursorKind.STRUCT_DECL and cur.hash != GLB_STRUCT_HASH:

            # 更新HASH并追加列表
            GLB_STRUCT_HASH = cur.hash
            structList.append(list())
            structList[-1].append(cur.spelling)

            # HASH与结构体名称存入字典
            structDict[GLB_STRUCT_HASH] = structList[-1]

        # 若hash值和之前一样, 证明还在当前结构体里
        elif cur.kind == clang.cindex.CursorKind.TYPEDEF_DECL:
            structList[-1].append(cur.spelling)

        preTravStruct(cur, headerList, structList, structDict)


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

    # structList是一个二维列表, structList[i][0]是结构体的名称, struct[i][1 - (n-1)]是结构体的别名. 因此, [i][0]可能为空字符串
    structList = list()

    # structDict是一个字典, key是结构体STRUCT_DECL节点的哈希值, value是其对应的结构体名与别名list
    structDict = dict()

    for cursor in GLB_AST_LIST:
        preTravStruct(cursor, header, structList, structDict)

    return structList, structDict


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
    global GLB_STRUCT_QUEUE, GLB_STRUCT_INFO

    for cur in cursor.get_children():

        # 查看一个变量是不是结构体变量
        varType = cur.type.spelling.split()[-1]  # 获取变量类型
        isStructVar = False
        for k, v in GLB_STRUCT_DICT.items():  # 查看变量类型是否能在GLB_STRUCT_DICT中找到
            if varType in v:  # 如果能找到, 证明是结构体变量, 加入队列作为待分析的对象
                GLB_STRUCT_QUEUE.put((k, GLB_PREFIX + cur.spelling))
                isStructVar = True

        # 若不是结构体变量, 正常分析
        if not isStructVar and cur.kind == clang.cindex.CursorKind.FIELD_DECL:
            var = cur.type.spelling + " " + GLB_PREFIX + cur.spelling
            GLB_STRUCT_INFO.append(var)


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


def analyzeOneStruct(structDict: dict, structHash: int) -> list:
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
    GLB_STRUCT_DICT = structDict
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

    structInfo = GLB_STRUCT_INFO.copy()
    print(structInfo)
    return structInfo


# TODO: 初始化
def init():
    pass


if __name__ == '__main__':
    GLB_AST_LIST = list()

    srcList = []
    headerList = [r"C:\Users\77257\Desktop\LocalFiles\Project_VSCode\python\fuzzing-tool-14\example\test.h"]

    # STEP 0: init
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

    # STEP 1: 获取所有结构体
    structList, structDict = getAllStruct(headerList)

    # STEP 2: 获取指定结构体内容
    struct = "ms"
    sHash = 114514

    for k, v in structDict.items():
        if struct in v:
            sHash = k

    analyzeOneStruct(structDict, sHash)