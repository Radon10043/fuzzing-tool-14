'''
Author: Radon
Date: 2020-09-28 13:18:56
LastEditors: Radon
LastEditTime: 2022-01-09 12:31:10
Description: 调用图相关的函数
'''
from PyQt5 import QtWidgets
import sys
import re
import subprocess
import clang.cindex
import os

import public


def createCallGraph(source_loc_list, graph_loc):
    """根据clang获得AST，并查看函数调用关系

    Parameters
    ----------
    source_loc_list : list
        C文件地址列表
    graph_loc : str
        /path/to/callgraph.txt

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

    # 根据AST获得调用图
    callgraph = dict()
    for source in source_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(source)
        preorderTraverseToGetCallgraph(source_loc_list, tu.cursor, "", callgraph)

    # 将调用图与所有结点写入文件
    with open(graph_loc, mode="w") as f:
        for key, value in callgraph.items():
            f.write(key + "," + str(value) + "\n")
    nodes = public.getAllFunctions(source_loc_list)
    nodes_loc = os.path.join(os.path.dirname(graph_loc), "nodes.txt")
    with open(nodes_loc, mode="w") as f:
        for node in nodes:
            f.write(node + "\n")


def preorderTraverseToGetCallgraph(source_loc_list, cursor, start, callgraph):
    """遍历获得调用关系

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        根节点
    start : str
        起始函数，查看start调用了谁
    callgraph : dict
        调用情况

    Notes
    -----
    [description]
    """
    for cur in cursor.get_children():
        try:
            if cur.location.file.name in source_loc_list:
                if cur.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                    start = cur.spelling
                if cur.kind == clang.cindex.CursorKind.CALL_EXPR:
                    call = start + "," + cur.spelling
                    if call in callgraph.keys():
                        callgraph[call] += 1
                    else:
                        callgraph[call] = 1
        except:
            pass
        preorderTraverseToGetCallgraph(source_loc_list, cur, start, callgraph)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
