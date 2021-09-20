import ctypes
import os
import random
import re
import shutil
import socket
import threading
import json
import time
from subprocess import *
from util.check_code import CheckCode

ROOT = "D:\\fuzzing-tool-14"
returnUDPInfo = []
allNode = []
isCrash = False  # 计算没有相应的测试用例数量
crashTC = bytes()  # 存储触发缺陷的测试用例




def parse_array(text):
    # loc|sign|filename
    loc_sign_fn = text.strip().split("|")
    loc = [int(i) for i in loc_sign_fn[0].split(',')]
    sign = [int(i) for i in loc_sign_fn[1].split(',')]
    fn = loc_sign_fn[2]
    return loc, sign, fn


def mkdir(path, del_if_exist=True):
    '''
    @description: 创建文件夹
    @param {*} path 文件夹的路径
    @return {*} True表示创建成功，False表示文件夹已存在，创建失败
    '''
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    elif del_if_exist:
        shutil.rmtree(path)
        os.makedirs(path)


def getCoverNode(num):
    '''
    @description: 获取一个数的二进制中1所在的位置, 主要用于查看覆盖到了哪些点
    @param {*} num 数字, 结构体中插装变量返回的值
    @return {*}
    '''
    cover = []
    coverNode = []
    loc = 0
    while num:
        if num & 1:
            cover.append(loc)
        num = num >> 1
        loc += 1
    global allNode
    for data in cover:
        coverNode.append(allNode[data])
    coverNode.append("main")
    return coverNode


def threadMonitor(senderAddress):
    '''
    @description: 线程2-启动python监控方，用于收集C++返回的UDP
    @param {*}
    @return {*}
    '''
    global returnUDPInfo
    returnUDPInfo.clear()
    monitorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建 socket 对象
    print(senderAddress)
    host = senderAddress.split(':')[0]
    port = int(senderAddress.split(':')[1])
    monitorSocket.bind((host, port))
    # monitorSocket.bind(("", 9999))  # 绑定端口
    data, client_addr = monitorSocket.recvfrom(1024)
    monitorSocket.close()
    print("data:", data)
    returnUDPInfo = str(bytes(data))


def getCoverage(fn_json, tmp_fn_bin, senderAddress, receiverAddress, maxTimeout, dllDict):
    thread2 = threading.Thread(target=threadMonitor, name="thread_monitor", args=(senderAddress,))
    thread2.start()
    print(fn_json)
    print(tmp_fn_bin)
    dllDict['mutate'].json2bytes.argtypes = ctypes.c_char_p, ctypes.c_char_p
    dllDict['mutate'].json2bytes.restype = None
    f1 = ctypes.c_char_p(bytes(fn_json, encoding='utf8'))
    f2 = ctypes.c_char_p(bytes(tmp_fn_bin, encoding='utf8'))
    dllDict['mutate'].json2bytes(f1,f2 )
    # 测试用例是bytes
    with open(tmp_fn_bin, "rb") as f:
        data = f.read()
    global isCrash
    global crashTC
    try:
        s = socket.socket()
        host = receiverAddress.split(":")[0]
        port = int(receiverAddress.split(":")[1])
        s.connect((host, port))
        s.send(data)
        s.close()
        isCrash = 0
        crashTC = data
    except BaseException as e:
        print("测试用例发送失败:", e)
        isCrash += 1

    # 等待线程2结束
    thread2.join(maxTimeout)

    # 读取返回的UDP包的内容
    global returnUDPInfo
    try:
        print(returnUDPInfo)
        returnUDPInfo = returnUDPInfo.split(",")
        returnUDPInfo.pop(-1)
        returnUDPInfo[0] = re.sub("[^0-9]", "", returnUDPInfo[0])
        returnUDPInfo = [int(data) for data in returnUDPInfo]
        print("returnData", returnUDPInfo)
        # 获得覆盖的结点
        instrValue = dllDict["instrument"].getInstrumentValue(bytes(returnUDPInfo))
        print("instrValue:", instrValue)
        coverNode = getCoverNode(instrValue)
        print("coverNode:", coverNode)
    except BaseException as e:
        print("解析失败: ", e)
        coverNode = ["main"]

    crashResult = isCrash == 10
    timeout = False
    return (data, coverNode, crashResult, crashTC)


def mutate(a, add=True, delete=True):
    res = bytearray()
    for i in range(0, len(a)):
        prob = random.random()
        number = random.randint(0, 255)
        step = random.randint(1, 2)
        if prob <= 0.1 and delete:
            continue
        elif prob <= 0.2 and add:
            res.append(number)
            i -= 1
        elif prob <= 0.8:
            res.append(a[i] ^ number)
        else:
            res.append(a[i])
    return bytes(res)


"""
        "变量名21": {
            "value": "var3",
            "lower": 30,
            "upper": 50,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位",
            "checkCode": False,
            "checkField": False
        },
"""
def gen_training_data(PATH_PREFIX, struct, num):
    # population = [bytearray([1, 2, 3, 4]), bytearray([0, 10, 100, 200])]
    for i in range(0, num):
        tmp = {}
        for key in struct.keys():
            if struct[key]["mutation"] and i != 0:
                lower = float(struct[key]["lower"])
                upper = float(struct[key]["upper"])
                if len(struct[key]["enum"]) == 0:
                    p = random.random()
                    if p < 0.1:
                        tmp[key] = lower
                    elif p < 0.2:
                        tmp[key] = upper
                    else:
                        tmp[key] = random.uniform(lower, upper)
                else:
                    idx = random.randint(0, len(struct[key]["enum"])-1)
                    tmp[key] = struct[key]["enum"][idx]
            else:
                tmp[key] = struct[key]["value"]
        fn = os.path.join(PATH_PREFIX, "input_" + str(i).zfill(10)+".json")
        json.dump(tmp, open(fn, "w"))



def genSeed(header_loc_list, struct, structDict, checkCodeMethod, hasCheckCode):
    check_code = CheckCode()
    check_code.init4str(checkCodeMethod)
    # 先设置好相关的位置信息
    root = re.sub(header_loc_list[0].split("/")[-1], "", header_loc_list[0]) + "/in/"
    if not os.path.exists(root):
        os.mkdir(root)
    genSeedPath = root + "genSeed.cpp"
    # 开始写代码，先include相关内容
    code = "#include <iostream>\n#include <Windows.h>\n#include <fstream>\n"
    code += "#include \"" + check_code.header_file_path + "\"\n"
    # 把用户选择的头文件位置也include
    for header in header_loc_list:
        code += "#include \"" + header + "\"\n"
    code += "using namespace std;\n\n"
    code += "int main(){\n"
    checkCodePart = ""
    count_check_code = 0
    checkFieldName = ""
    # 新建结构体变量，并向它的成员变量赋值
    code += "\t" + struct + " data;\n"
    for key, value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        if "noName" in dataName:  # 跳过无名变量
            continue
        if hasCheckCode:  # 存在校验码就搞这些
            if value["checkField"]:  # 这个是校验字段，添加主代码，然后将这个值方法checkList里
                code += "\tdata." + dataName + " = " + str(value["value"]) + ";\n"
                checkCodePart += "\tcheckList[" + str(count_check_code) + "] = " + str(value["value"]) + ";\n"
                count_check_code += 1
                continue
            elif value["checkCode"]:
                checkFieldName = dataName
                continue
        code += "\tdata." + dataName + " = " + str(value["value"]) + ";\n"
    if hasCheckCode:
        code += "\tunsigned int checkList[" + str(count_check_code) + "];\n"
        code += checkCodePart
        code += "\tdata." + checkFieldName + " = " + check_code.code + "\n"
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
    header_loc_list_save_file_path = root + "header_loc_list.txt"
    header_loc_list_save_file_file = open(header_loc_list_save_file_path, mode="w", encoding="utf")
    for one_header in header_loc_list:
        header_loc_list_save_file_file.write(one_header)
        header_loc_list_save_file_file.write("\n")
    header_loc_list_save_file_file.close()


