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


def threadReceiver(program_loc):
    global isCrash
    isCrash = 0
    # prog = "D:\\fuzzing-tool-14\\example\\main.exe"
    # prog = os.path.join(os.curdir, "example", "main.exe")
    out = getstatusoutput(program_loc)
    isCrash = out[0]
    print("Receiver print:\n", out[1])


'''
@description: 线程2-启动python监控方，用于收集C++返回的UDP
@param {*}
@return {*}
'''


def threadMonitor():
    global returnUDPInfo
    # prog = "D:\\fuzzing-tool-14\\example\\cppudptest\\getudp.py"
    prog = prog = os.path.dirname(os.path.abspath(__file__)) + "/getudp.py"
    out = getstatusoutput(prog)
    # print("getudp.py: ", out)
    returnUDPInfo = out[1]


def getCoverage(testcase, program_loc, MAIdll):
    """
    @param {*} testcase 需要发送的测试用例，类型为bytes
    @param {*} program_loc 程序位置
    @return {*} 返回(测试用例, 距离, 适应度, 覆盖点, 是否触发缺陷, 是否超时)，返回结果是一个元组
    """

    # print("old", testcase)
    # MAIdll.setInstrumentValueToZero(testcase)
    # MAIdll.setValueInRange(testcase)
    # print("new", testcase)
    # 先启动线程2，用于监控
    thread2 = threading.Thread(target=threadMonitor, name="thread_monitor", )
    thread2.start()
    # 启动线程2后，稍微等下，如果线程1速度快了可能会导致线程2无法获得返回的UDP包
    # 从而陷入一直等待线程2结束的状态
    time.sleep(0.2)
    # 一段时间后，启动线程1
    thread1 = threading.Thread(target=threadReceiver, args=(program_loc,), name="thread_receiver")
    thread1.start()
    # 形参的测试用例是str类型的list，转换成int后再转为byte
    # data = bytes([int(data) for data in testcase])
    # 发送测试用例
    s = socket.socket()
    host = socket.gethostname()
    port = 8888
    s.connect((host, port))
    # s.send(data)
    s.send(testcase)
    s.close()
    # 等待线程1和线程2结束
    thread1.join()
    thread2.join()
    # 读取返回的UDP包的内容
    global returnUDPInfo
    returnUDPInfo = returnUDPInfo.split(",")
    returnUDPInfo.pop(-1)
    returnUDPInfo[0] = re.sub("[^0-9]", "", returnUDPInfo[0])
    returnUDPInfo = [int(data) for data in returnUDPInfo]
    print("returnData", returnUDPInfo)
    # 获得覆盖的结点
    instrValue = MAIdll.getInstrumentValue(bytes(returnUDPInfo))
    print("instrValue:", instrValue)
    crashResult = isCrash
    coverNode = getCoverNode(instrValue)
    print("coverNode:", coverNode)

    timeout = False
    return testcase, coverNode, crashResult, timeout


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


def gen_training_data(PATH_PREFIX, seed_fn, num, MAIdll):
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
        with open(input_fn, "wb") as f:
            MAIdll.setValueInRange(tc)
            f.write(tc)
    return population


if __name__ == "__main__":
    """
    fn = "D:\\fuzzing-tool-14\\example\\in\\structDict.json"
    res = json.load(open(fn, "r"))
    json.dump(struct2TC(res), open("D:\\fuzzing-tool-14\\tmp.json", "w"))
    """
    MAIdll = ctypes.cdll.LoadLibrary("D:\\fuzzing-tool-14\\example\\in\\mutate_instru.dll")

    MAIdll.serialize()