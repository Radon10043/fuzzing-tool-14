'''
Author: Radon
Date: 2021-05-16 10:03:05
LastEditors: Radon
LastEditTime: 2021-08-23 17:37:14
Description: Some public function
'''

from PyQt5 import QtWidgets
import sys
import os
import re
import subprocess
import clang.cindex


def deleteNote(source):
    '''
    @description: 删除程序中的注释
    @param {*} source 代码列表，source = f.readlines()
    @return {*}
    '''
    skip = False
    for i in range(len(source)):
        if "//" in source[i]:
            source[i] = source[i].split("//")[0] + "\n"
        if "/*" in source[i]:
            skip = True
            if "*/" in source[i]:
                skip = False
                source[i] = source[i].split("/*")[0] + "\n"
        elif "*/" in source[i]:
            skip = False
            source[i] = "\n"
        if skip == True:
            source[i] = "\n"
    return source


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
    libclangPath = re.sub(libclangPath.split(
        "\\")[-1], "", libclangPath) + "libclang.dll"
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
        preorderTraverseToGetAllFunctions(tu.cursor, funcList)
    funcList = sorted(set(funcList))
    return funcList


def preorderTraverseToGetAllFunctions(cursor, funcList):
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
        if cur.kind == clang.cindex.CursorKind.CXX_METHOD or cur.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            funcList.append(cur.spelling)
        preorderTraverseToGetAllFunctions(cur, funcList)




def genSeed(header_loc, struct, structDict):
    '''
    @description: 写一个生成初始种子的cpp文件，并编译和执行它
    @param {*} header_loc 列表，里面存储了所有头文件的路径
    @param {*} struct 用户所选择的结构体名称
    @param {*} structDict Ui_dialog_seed里的字典，其中存储了分析得到的结构体和它的成员变量的信息
    @return {*}
    '''
    # 先设置好相关的位置信息
    root = re.sub(header_loc[0].split("/")[-1], "", header_loc[0]) + "/in/"
    if not os.path.exists(root):
        os.mkdir(root)
    genSeedPath = root + "genSeed.cpp"
    # 开始写代码，先include相关内容
    code = "#include <iostream>\n#include <Windows.h>\n#include <fstream>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc:
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
    header_loc_save_file_path = root + "header_loc.txt"
    header_loc_save_file_file = open(
        header_loc_save_file_path, mode="w", encoding="utf")
    for one_header in header_loc:
        header_loc_save_file_file.write(one_header)
        header_loc_save_file_file.write("\n")
    header_loc_save_file_file.close()


def gen_test_case_from_structDict(header_loc, struct, structDict, path):
    """
    @description: 根据structDict中的value，生成指定测试用例
    @param {*} header_loc 列表，里面存储了所有头文件的路径
    @param {*} struct 用户所选择的结构体名称
    @param {*} structDict Ui_dialog_seed里的字典，其中存储了分析得到的结构体和它的成员变量的信息
    @return {*}
    """
    # 先设置好相关的位置信息
    cycle_path = path.split("mutate")[0] + "mutate" + path.split("mutate")[1]
    mutate_file_name = "mutate" + path.split("mutate")[2]
    # 开始写代码，先include相关内容
    code = "#include <iostream>\n#include <Windows.h>\n#include <fstream>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc:
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


def genMutate(header_loc, struct, structDict):
    '''
    @description: 写一个mutate.c, 以便测试时进行变异操作
    @param {*} header_loc 列表, 里面存储了所有头文件得位置
    @param {*} struct 用户所选择得结构体名称
    @param {*} structDict 结构体字典
    @return {*}
    '''
    # 先设置好相关的位置信息
    root = re.sub(header_loc[0].split("/")[-1], "", header_loc[0]) + "/in/"
    if not os.path.exists(root):
        os.mkdir(root)
    genMutatePath = root + "mutate.c"

    # 开始写代码，先include相关内容
    code = "#include <stdio.h>\n#include <stdbool.h>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc:
        code += "#include \"" + header + "\"\n"
    # mutate函数中有三个形参: struct data是发送数据的结构体, seedPath是变异后的文件保存路径, 精确到.txt
    # r是一个随机数, 用于与原来的值进行异或
    code += "\nvoid mutate(" + struct + " data, char* savePath, int r){\n"
    # 变异操作
    for key, value in structDict[struct].items():
        if not value["mutation"]:
            continue
        dataName = key.split(" ")[-1].split(":")[0]
        code += "\tdata." + dataName + " ^= r;\n"
    # 变异体写入文件
    code += "\n\tFILE* f;"
    code += "\n\tf = fopen(savePath, \"wb\");"
    code += "\n\tfwrite(&data, sizeof(data), 1, f);"
    code += "\n\tfclose(f);\n"
    code += "}\n\n"

    # 写一个将结构体的值设定在用户指定范围内的方法
    code += "void setValueInRange(" + struct + " data){\n"
    code += "\t" + struct + "* temp = &data;\n"
    for key, value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        if "noName" in dataName:
            continue
        code += "\ttemp->" + dataName + " = (temp->" + dataName + " % ((" + str(
            value["upper"]) + ") - (" + str(value["lower"]) + "))) + (" + str(value["lower"]) + ");\n"
    code += "}\n\n"

    # 写一个将结构体可视化的方法，savePath需要以.txt结尾
    code += "void testcaseVisualization(" + \
        struct + " data, char* savePath){\n"
    code += "\tFILE* f = fopen(savePath, \"w\");\n"
    for key, value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        if "noName" in dataName:
            continue
        code += "\tfprintf(f, \"" + dataName + \
            ": %u\\n\", data." + dataName + ");\n"
    code += "\tfclose(f);\n"
    code += "}\n"

    mutateFile = open(genMutatePath, mode="w")
    mutateFile.write(code)

    # 生成.dll文件，在这里生成的话会出现问题，所以改到了在Ui_window.py生成
    # command: gcc -shared -o mutate_instru.dll mutate_instru.c


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
