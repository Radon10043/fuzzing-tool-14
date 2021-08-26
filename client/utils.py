import os
import random
import re
import shutil
import socket
import threading
import time
import json
import ctypes
from subprocess import *

isCrash = 0
ROOT = "D:\\fuzzing-tool-14"
returnUDPInfo = []
allNode = []


def struct2TC(struct):
    TC = {}
    for key, value in struct["Datagram"].items():
        dataName = key.split(" ")[-1].split(":")[0]
        dataValue = value["value"]
        TC[dataName] =dataValue
    return TC


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


def getCoverage(testcase, senderAddress, receiverAddress, maxTimeout, dllDict):
    crash = False
    thread2 = threading.Thread(target=threadMonitor, name="thread_monitor", args=(senderAddress,))
    thread2.start()

    # 测试用例是bytes
    data = testcase
    try:
        s = socket.socket()
        host = receiverAddress.split(":")[0]
        port = int(receiverAddress.split(":")[1])
        s.connect((host, port))
        s.send(data)
        s.close()
    except BaseException as e:
        print("测试用例发送失败:", e)

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
        crash = True

    crashResult = isCrash == 10
    timeout = False
    return (testcase, coverNode, crash, timeout)


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


def gen_training_data(PATH_PREFIX, seed_fn, num, dll):
    # population = [bytearray([1, 2, 3, 4]), bytearray([0, 10, 100, 200])]
    population = [open(seed_fn, "rb").read()]
    while len(population) <= num:
        new_population = []
        for tc in population:
            new_population.append(mutate(tc, add=False, delete=False))
            if len(new_population) + len(population) >= num:
                break
        population += new_population
    # res = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
    for i, tc in enumerate(population):
        if i >= num:
            break
        input_fn = os.path.join(PATH_PREFIX, "seeds", "input_" + str(i).zfill(10))
        if i / num > 0.4:
            dll['mutate'].setValueInRange(tc)
        input_fn = bytes(input_fn, encoding="utf8")
        dll["mutate"].mutate(tc, input_fn, 0xffffffff)
    return population


if __name__ == "__main__":
    """
    fn = "D:\\fuzzing-tool-14\\example\\in\\structDict.json"
    res = json.load(open(fn, "r"))
    json.dump(struct2TC(res), open("D:\\fuzzing-tool-14\\tmp.json", "w"))
    """
    MAIdll = ctypes.cdll.LoadLibrary("D:\\fuzzing-tool-14\\example\\in\\mutate_instru.dll")

    MAIdll.serialize()