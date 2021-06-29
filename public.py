'''
Author: Radon
Date: 2021-05-16 10:03:05
LastEditors: Radon
LastEditTime: 2021-06-29 12:46:15
Description: Some pulic function
'''

import re, time, os
from win32 import win32api

'''
@description: 删除程序中的注释
@param {*} source 代码列表，source = f.readlines()
@return {*}
'''
def deleteNote(source):
    skip = False
    for i in range(len(source)):
        if "//" in source[i]:
            source[i]=source[i].split("//")[0]+"\n"
        if "/*" in source[i]:
            skip = True
            if "*/" in source[i]:
                skip = False
                source[i]=source[i].split("/*")[0]+"\n"
        elif "*/" in source[i]:
            skip=False
            source[i]="\n"
        if skip==True:
            source[i]="\n"
    return source

'''
@description: 获取所有定义的函数
@param {*} source_locs 所有源文件地址的字符串，用\n隔开
@return {*} 返回包含所有自定义函数的列表
'''
def getAllFunctions(source_locs):
    if isinstance(source_locs, str):
        source_loc = source_locs.split("\n")
    elif isinstance(source_locs, list):
        source_loc = source_locs
    funcList = []
    for source in source_loc:
        try:
            f = open(source,encoding="utf8")
            lines = f.readlines()
        except UnicodeDecodeError:
            f = open(source)
            lines = f.readlines()
        brace = 0
        f.close()
        lines = deleteNote(lines)
        for line in lines:
            if "(" in line and brace == 0:
                code = line.split("(")[0]
                code.rstrip()
                code = re.sub("[^A-Za-z0-9_]","+",code)
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
    root = re.sub(header_loc[0].split("\\")[-1],"",header_loc[0]) + "\\in\\"
    if not os.path.exists(root):
        os.mkdir(root)
    genSeedPath = root + "genSeed.cpp"
    # 开始写代码，先include相关内容
    code = "#include <iostream>\n#include <Windows.h>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc:
        code += "#include \"" + header + "\"\n"
    code += "using namespace std;\n\n"
    code += "int main(){\n"
    # 新建结构体变量，并向它的成员变量赋值
    code += "\t" + struct + " data;\n"
    for key,value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        code += "\tdata." + dataName + " = " + str(value["value"]) + ";\n"
    # 赋值结束后，向seed.txt文件中写入内容
    code += "\n\tunsigned char* p = (unsigned char*)&data;\n\t"
    code += "FILE *f = fopen(\"seed.txt\", \"w\");\n\t"
    code += "for (; p < (unsigned char*)&data + sizeof(data); p++) {\n\t\t"
    code += "fprintf(f, \"%d\", *p);\n\t\t"
    code += "if (p != (unsigned char*)&data + sizeof(data) - 1) fprintf(f, \",\");\n\t"
    code += "}\n\tfclose(f);\n\treturn 0;\n}"
    # 写完代码后，编译并执行，在第一个头文件的同目录下会生成seed.txt，它就是种子测试用例
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
    root = re.sub(header_loc[0].split("\\")[-1],"",header_loc[0]) + "\\in\\"
    if not os.path.exists(root):
        os.mkdir(root)
    genMutatePath = root + "mutate_instru.c"
    # 开始写代码，先include相关内容
    code = "#include <stdio.h>\n#include <stdbool.h>\n"
    # 把用户选择的头文件位置也include
    for header in header_loc:
        code += "#include \"" + header + "\"\n"
    code += "\n"
    # mutate函数中有三个形参: struct data是发送数据的结构体, seedPath是变异后的文件保存路径, 精确到.txt
    # r是一个随机数, 用于与原来的值进行异或
    code += "void mutate(" + struct + " data, char* savePath, int r){\n"
    # 变异操作
    for key,value in structDict[struct].items():
        if not value["mutation"]:
            continue
        dataName = key.split(" ")[-1].split(":")[0]
        code += "\tdata." + dataName + " ^= r;\n"
    # 变异体写入文件
    code += "\tunsigned char* p = (unsigned char*)&data;\n\tFILE* f = fopen(savePath, \"w\");\n"
    code += "\tfor (; p < (unsigned char*)&data + sizeof(data); p++) {\n"
    code += "\t\tfprintf(f,\"%d\", *p);\n"
    code += "\t\tif (p != (unsigned char*)&data + sizeof(data)-1)\n"
    code += "\t\t\tfprintf(f, \",\");\n"
    code += "\t}\n\tfclose(f);"
    code += "}\n\n"
    # 写一个获取插装变量的值的函数
    for key,value in structDict[struct].items():
        if not value["instrument"]:
            continue
        dataType = key.split(" ")
        dataType.pop(-1)
        dataType = " ".join(dataType)
        dataName = key.split(" ")[-1].split(":")[0]
        code += dataType + " getInstrumentValue(" + struct + " data){\n"
        code += "\treturn data." + dataName + ";\n"
    code +="}"
    mutateFile = open(root + "mutate_instru.c", mode="w")
    mutateFile.write(code)
    # 生成.dll文件
    # 这里还有点问题，根据代码生成的dll文件执行过程中会出错，但手动生成的就不会出错
    os.chdir(root)
    os.system("gcc -shared -o mutate_instru.dll mutate_instru.c")
    # gcc -shared -o mutate_instru.dll mutate_instru.c

import ctypes
if __name__ == "__main__":
    MAIdll = ctypes.cdll.LoadLibrary("C:\\Users\\Radon\\Desktop\\fuzztest\\4th\\example\\in\\mutate_instru.dll")
    temp = [102,0,33,92,90,0,0,0,21,6,19,11,47,48,100,0,96,0,0,0,0,0,0,0,107,0,0,0,44,0,0,0,1,1,0,0,76,0,0,0,107,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,111,16,64,0,116,45,1,108,117,1,71,42,1,60,39,1]
    temp = bytes(temp)
    res = MAIdll.getInstrumentValue(temp)
    print(res)