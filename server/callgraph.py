'''
Author: Radon
Date: 2020-09-28 13:18:56
LastEditors: Radon
LastEditTime: 2021-08-11 21:41:29
Description: Hi, say something
'''
import re

import public


def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]


'''
@description: 创建函数调用图
@param {*} source_loc 列表, 其中存储了所有源文件的位置
@param {*} graph_loc 调用图保存的路径
@return {*}
'''


def createCallGraph(source_loc_list, graph_loc):
    """生成函数调用图

    Parameters
    ----------
    source_loc : list
        存储源文件位置的列表
    graph_loc : str
        调用图生成位置, e.g. /path/to/callgraph.txt

    Notes
    -----
    [description]
    """
    f_graph = open(graph_loc, mode="w+")
    graph = []
    customize = []  # 这个列表用于存储自定义的函数

    for source in source_loc_list:
        brace = 0
        try:
            f_source = open(source, encoding="utf8")
            lines = f_source.readlines()
        except:
            f_source = open(source)
            lines = f_source.readlines()
        lines = public.deleteNote(lines)

        start = "empty"
        for line in lines:
            # 如果行内有#define #pragma 和 #include的话, 为了防止分析结果错误, 跳过这一行
            if "#define" in line or "#pragma" in line or "#include" in line:
                continue
            # 如果行内有左括号且brace == 0, 证明这一行定义了某个函数
            if "(" in line and brace == 0:
                start = line.split("(")[0].split(" ")[-1]
                start = re.sub("[^A-Za-z1-9_]", "", start)
                if not start in customize:
                    customize.append(start)
            # 如果行内有左括号且brace != 0, 证明这一行调用了某个函数
            elif "(" in line and brace != 0:
                words = re.sub("[^A-Za-z1-9_(]", " ", line).split("(")
                for end in words:
                    end = end.split(" ")[-1]
                    if end in customize:
                        path = start + "," + end
                        # 先把路径信息存到一个list中，下面是在write前检测一下是否已存在这个路径（这是针对调用多次同一函数的情况）
                        found = False
                        for i in range(0, len(graph)):
                            if path in graph[i]:
                                print("I found it!\n")
                                found = True
                                break
                        if found == False:
                            graph.append(path + ",1")
                        else:
                            path = graph.pop(i).split(",")
                            weight = int(path[2]) + 1
                            graph.append(path[0] + "," + path[1] + "," + str(weight))
            if "{" in line:
                brace += 1
            if "}" in line:
                brace -= 1

    print("graph:", graph)
    for i in range(0, len(graph)):
        f_graph.write(graph[i] + "\n")
    f_graph.close()
    f_source.close()

    # 将所有结点写入nodes.txt
    nodes_loc = re.sub(graph_loc.split("/")[-1], "", graph_loc) + "nodes.txt"
    f_nodes = open(nodes_loc, mode="w")
    nodes = public.getAllFunctions(source_loc_list)
    for node in nodes:
        f_nodes.write(node + "\n")
    f_nodes.close()


import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
