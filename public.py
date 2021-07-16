'''
Author: Radon
Date: 2021-05-16 10:03:05
LastEditors: Radon
LastEditTime: 2021-07-14 14:19:37
Description: Some pulic function
'''

from PyQt5 import QtWidgets
import sys
import os
import re

'''
@description: 删除程序中的注释
@param {*} source 代码列表，source = f.readlines()
@return {*}
'''


def deleteNote(source):
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
    '''
    @description: 获取所有定义的函数
    @param {*} source_loc_list 列表，存储了所有源文件地址
    @return {*} 返回包含所有自定义函数的列表
    '''
    funcList = []
    for source in source_loc_list:
        try:
            f = open(source, encoding="utf8")
            lines = f.readlines()
        except UnicodeDecodeError:
            f = open(source)
            lines = f.readlines()
        brace = 0
        f.close()
        lines = deleteNote(lines)
        for line in lines:
            # 程序有时候会误认为#pragma comment(lib, "ws2_32.lib")是函数，还没想到好方法
            if "#pragma" in line:
                continue
            # 有左括号且没在{}内就认为有可能是函数
            if "(" in line and brace == 0:
                code = line.split("(")[0]
                code.rstrip()
                code = re.sub("[^A-Za-z0-9_]", "+", code)
                funcList.append(code.split("+")[-1])
            if "{" in line:
                brace += 1
            if "}" in line:
                brace -= 1
        funcList = sorted(set(funcList))
    return funcList


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


def genMutate(header_loc, struct, structDict):
    '''
    @description: 写一个mutate_instru.c, 并生成相应得.dll, 以便测试时进行变异操作和读取插桩变量的值
    @param {*} header_loc 列表, 里面存储了所有头文件得位置
    @param {*} struct 用户所选择得结构体名称
    @param {*} structDict 结构体字典
    @return {*}
    '''
    # 先设置好相关的位置信息
    root = re.sub(header_loc[0].split("/")[-1], "", header_loc[0]) + "/in/"
    if not os.path.exists(root):
        os.mkdir(root)
    genMutatePath = root + "mutate_instru.c"

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

    # 写一个获取插装变量的值的函数
    for key, value in structDict[struct].items():
        if not value["instrument"]:
            continue
        dataType = key.split(" ")
        dataType.pop(-1)
        dataType = " ".join(dataType)
        dataName = key.split(" ")[-1].split(":")[0]
        code += dataType + " getInstrumentValue(" + struct + " data){\n"
        code += "\treturn data." + dataName + ";\n"
    code += "}\n\n"

    # 写一个将插装值设置为0的方法
    code += "void setInstrumentValueToZero(" + struct + " data){\n"
    code += "\t" + struct + "* temp = &data;\n"
    code += "\ttemp->" + dataName + " = 0;\n"
    code += "}\n\n"

    # 写一个将结构体的值设定在用户指定范围内的方法
    code += "void setValueInRange(" + struct + " data){\n"
    code += "\t" + struct + "* temp = &data;\n"
    # 先将插装变量置为0
    code += "\ttemp->" + dataName + " = 0;\n"
    for key, value in structDict[struct].items():
<<<<<<< HEAD
        # if not value["mutation"]:
        #     continue
=======
>>>>>>> upstream/main
        dataName = key.split(" ")[-1].split(":")[0]
        code += "\ttemp->" + dataName + " %= " + str(value["upper"]) + ";\n"
    code += "}"

    mutateFile = open(root + "mutate_instru.c", mode="w")
    mutateFile.write(code)

    # 生成.dll文件，在这里生成的话会出现问题，所以改到了在Ui_window.py生成
    # gcc -shared -o mutate_instru.dll mutate_instru.c


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
