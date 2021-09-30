'''
Author: Radon
Date: 2021-05-16 10:03:05
LastEditors: Radon
LastEditTime: 2021-09-30 15:10:39
Description: Some public function
'''

from PyQt5 import QtWidgets
import sys
import os
import re
import subprocess
import clang.cindex


def getAllFunctions(source_loc_list):
    """使用clang对程序进行分析生成AST树，并获得所有函数

    Parameters
    ----------
    source_loc_list : list
        C文件地址列表

    Returns
    -------
    list
        所有函数

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

    # 获取所有函数
    funcList = list()
    for source in source_loc_list:
        index = clang.cindex.Index.create()
        tu = index.parse(source)
        preorderTraverseToGetAllFunctions(tu.cursor, funcList, source_loc_list)
    funcList = sorted(set(funcList))
    return funcList


def preorderTraverseToGetAllFunctions(cursor, funcList, source_loc_list):
    """遍历获得所有函数

    Parameters
    ----------
    cursor : clang.cindex.Cursor
        根节点
    funcList : list
        函数列表

    Notes
    -----
    [description]
    """

    for cur in cursor.get_children():
        try:
            if cur.location.file and cur.location.file.name in source_loc_list:
                if cur.kind == clang.cindex.CursorKind.CXX_METHOD or cur.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                    funcList.append(cur.spelling)
        except:
            pass
        preorderTraverseToGetAllFunctions(cur, funcList, source_loc_list)


def genSeed(header_loc_list, struct, structDict):
    """写一个生成初始种子的cpp文件，并编译和执行它

    Parameters
    ----------
    header_loc_list : list
        里面存储了所有头文件的路径
    struct : str
        用户所选择的结构体名称
    structDict : dict
        Ui_dialog_seed里的字典，其中存储了分析得到的结构体和它的成员变量的信息

    Returns
    -------
    [type]
        [description]

    Notes
    -----
    [description]
    """
    # 先设置好相关的位置信息
    root = os.path.join(os.path.dirname(header_loc_list[0]), "in")
    if not os.path.exists(root):
        os.mkdir(root)
    genSeedPath = os.path.join(root, "genSeed.cpp")
    # 开始写代码，先include相关内容
    code = "#include <iostream>\n#include <Windows.h>\n#include <fstream>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc_list:
        code += "#include \"" + header + "\"\n"
    code += "using namespace std;\n\n"
    code += "int main(){\n"
    # 新建结构体变量，并向它的成员变量赋值
    code += "\t" + struct + " data;\n"
    for key, value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        if "noName" in dataName:
            continue
        code += "\tdata." + dataName + " = " + str(value["value"]) + ";\n"
    # 赋值结束后，向seed文件中写入内容
    code += "\n\tofstream f(\"seed\");"
    code += "\n\tf.write((char*)&data, sizeof(data));"
    code += "\n\tf.close();"
    code += "\n\treturn 0;\n}"
    # 写完代码后，编译并执行，在第一个头文件的同目录下会生成seed，它就是种子测试用例
    f = open(genSeedPath, mode="w")
    f.write(code)
    f.close()
    # 编辑命令集合
    cmds = []
    cmds.append("g++ -o genSeed.exe genSeed.cpp")
    cmds.append("genSeed.exe")
    # 切换目录并执行命令
    os.chdir(root)
    for cmd in cmds:
        os.system(cmd)
    header_loc_save_file_path = os.path.join(root, "header_loc_list.txt")
    header_loc_save_file_file = open(header_loc_save_file_path, mode="w", encoding="utf")
    for one_header in header_loc_list:
        header_loc_save_file_file.write(one_header)
        header_loc_save_file_file.write("\n")
    header_loc_save_file_file.close()


def gen_test_case_from_structDict(header_loc_list, struct, structDict, path):
    """根据structDict中的value，生成指定测试用例

    Parameters
    ----------
    header_loc_list : list
        里面存储了所有头文件的路径
    struct : str
        用户所选择的结构体名称
    structDict : dict
        Ui_dialog_seed里的字典，其中存储了分析得到的结构体和它的成员变量的信息
    path : str
        [description]

    Returns
    -------
    [type]
        [description]

    Notes
    -----
    [description]
    """
    # 先设置好相关的位置信息
    cycle_path = path.split("mutate")[0] + "mutate" + path.split("mutate")[1]
    mutate_file_name = "mutate" + path.split("mutate")[2]
    # 开始写代码，先include相关内容
    code = "#include <iostream>\n#include <Windows.h>\n#include <fstream>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc_list:
        code += "#include \"" + header.strip() + "\"\n"
    code += "using namespace std;\n\n"
    code += "int main(){\n"
    # 新建结构体变量，并向它的成员变量赋值
    code += "\t" + struct + " data;\n"
    for key, value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        if "noName" in dataName:
            continue
        code += "\tdata." + dataName + " = " + str(value["value"]) + ";\n"
    code += "\n\tofstream f(\"" + mutate_file_name + "\");"
    code += "\n\tf.write((char*)&data, sizeof(data));"
    code += "\n\tf.close();"
    code += "\n\treturn 0;\n}"
    f = open(path + "_gen.cpp", mode="w")
    f.write(code)
    f.close()
    # 编辑命令集合
    cmds = []
    cmds.append("g++ -o gen.exe " + path + "_gen.cpp")
    cmds.append("gen.exe")
    # 切换目录并执行命令
    os.chdir(cycle_path)
    for cmd in cmds:
        os.system(cmd)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
