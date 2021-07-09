from subprocess import *
from operator import itemgetter
import random
import os
import numpy as np
import networkx as nx
import shutil
import re
import time
import ctypes
import platform
import socket
import threading
from PyQt5.QtCore import pyqtSignal

import callgraph as cg
import instrument as instr
import staticAnalysis as sa
import public


def mkdir(path):
    '''
    @description: 创建文件夹
    @param {*} path 文件夹的路径
    @return {*} True表示创建成功，False表示文件夹已存在，创建失败
    '''
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


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


def loadData(fileName):
    '''
    @description: 获取调用图的数据
    @param {*} fileName 调用图位置
    @return {*}
    '''
    file = open(fileName,'r')#read file
    weightedEdges = []
    elementList = []
    for line in file:
        data = line.split(',')
        elementList.append(data[0])
        elementList.append(data[1])
        elementList.append(float(1/int(data[2])))
        elementTuple = tuple(elementList)
        elementList.clear()
        weightedEdges.append(elementTuple)
    file.close()
    return weightedEdges


def getDistance_shortest(graph,nodeSet,target):
    '''
    @description: 获取覆盖结点集合与目标结点之间的最短距离
    @param {*} graph 图, 需要根据图计算距离
    @param {*} nodeSet 结点集合
    @param {*} target 目标结点
    @return {*}
    '''
    G = nx.Graph()
    G.add_weighted_edges_from(graph)
    shortest = 999.0
    distance = 999.0
    for node in nodeSet:
        try:
            distance = nx.dijkstra_path_length(G,node,target)
            if distance < shortest:
                shortest = distance
        except:
            shortest = 999.0
    return shortest


def getDistance_average(graph,nodeSet,target):
    '''
    @description: 获取结点集合与目标结点之间的平均距离
    @param {*} graph 图, 需要根据图计算距离
    @param {*} nodeSet 结点集合
    @param {*} target 目标结点
    @return {*}
    '''
    G = nx.Graph()
    G.add_weighted_edges_from(graph)
    distance = 0
    try:
        for node in nodeSet:
            distance += nx.dijkstra_path_length(G,node,target)
        distance = distance/len(nodeSet)
    except:
        distance = 999.0
    # for node in nodeSet:
    #     distance += nx.dijkstra_path_length(G,node,target)
    # distance = distance/len(nodeSet)
    return distance

def getDirContent(position):
    content = []
    files = os.listdir(position)        # 读取position下的文件列表
    for file in files:                  # 挨个读取txt文件
        position2 = position + "\\" + file
        with open(position2, "r", encoding="utf-8") as f:   # 用with open as的话不必加close()
            content.append(f.read())
    return content


def threadReceiver(program_loc):
    '''
    @description: 线程1-启动C++接收方，用于接收由py发送的测试用例
    @param {*}
    @return {*}
    '''
    global isCrash
    isCrash = 0
    prog = program_loc
    out = getstatusoutput(prog)
    isCrash = out[0]


def threadMonitor():
    '''
    @description: 线程2-启动python监控方，用于收集C++返回的UDP
    @param {*}
    @return {*}
    '''
    global returnUDPInfo
    # 启动同目录下的getudp.py
    prog = os.path.dirname(os.path.abspath(__file__)) + "\\getudp.py"
    out = getstatusoutput(prog)
    # print("getudp.py: ", out)
    global returnUDPInfo
    returnUDPInfo = out[1]


def getFitness(testcase, targetSet, program_loc, callGraph, maxTimeout, MAIdll):
    '''
    @description: 根据南京大学徐安孜同学的例子重新写了一下获取适应度的函数，但还有待补充的地方
    @param {*} testcase 需要发送的测试用例，是一个内部元素均为str的list
    @param {*} targetSet 目标集
    @param {*} program_loc 程序位置
    @param {*} callGraph 函数调用图，需要借此来计算测试用例和目标集之间的举例，从而计算适应度
    @param {*} maxTimeout 超时时间
    @return {*} 返回(测试用例, 距离, 适应度, 覆盖点, 是否触发缺陷, 是否超时)，返回结果是一个元组
    '''
    # 先启动线程2，用于监控
    thread2 = threading.Thread(target = threadMonitor, name = "thread_monitor",)
    thread2.start()
    # 启动线程2后，稍微等下，如果线程1速度快了可能会导致线程2无法获得返回的UDP包
    # 从而陷入一直等待线程2结束的状态
    time.sleep(0.2)
    # 一段时间后，启动线程1，注意args是一个元组，结尾必须有逗号
    thread1 = threading.Thread(target = threadReceiver, name = "thread_receiver", args = (program_loc, ))
    thread1.start()
    # 形参的测试用例bytes
    data = testcase
    # 发送前，将测试用例的插装变量设置为0
    MAIdll.setInstrumentValueToZero(data)
    # 发送测试用例
    s = socket.socket()
    host = socket.gethostname()
    port = 8888
    s.connect((host, port))
    s.send(data)
    s.close()
    # 等待线程1和线程2结束
    thread1.join()
    thread2.join()

    # 读取返回的UDP包的内容
    global returnUDPInfo
    returnUDPInfo = returnUDPInfo.split(",")
    returnUDPInfo.pop(-1)
    returnUDPInfo[0] = re.sub("[^0-9]","",returnUDPInfo[0])
    returnUDPInfo = [int(data) for data in returnUDPInfo]
    print("returnData", returnUDPInfo)
    # 获得覆盖的结点
    instrValue = MAIdll.getInstrumentValue(bytes(returnUDPInfo))
    print("instrValue:", instrValue)
    coverNode = getCoverNode(instrValue)
    print("coverNode:",coverNode)
    # 计算距离
    distance = 500
    for target in targetSet:
        distance += getDistance_average(callGraph, coverNode, target)
    fitness = 1/distance
    crashResult = isCrash
    timeout = False
    return (testcase,distance,fitness,coverNode,crashResult,timeout)


def mutate(testcase, mutateSavePath, MAIdll):
    '''
    @description: 根据南京大学徐安孜同学写的例子对变异进行了改写，由于均是数字，所以做一下和数字有关的操作就好
    @param {*} testcase 传入的测试用例是一个字节序列
    @param {*} mutateSavePath 变异测试用例的保存路径, 与原本流程不同, 在这里直接将变异后的测试用例保存到本地
    @return {*}
    '''
    # 将对测试用例进行变异并保存
    mutateSavePath = bytes(mutateSavePath, encoding="utf8")
    r = random.randint(0,255)
    MAIdll.mutate(testcase, mutateSavePath, r)


def crossover(population):
    # pc是概率阈值，选择单点交叉还是多点交叉，生成新的交叉个体
    pop_len=len(population)
    for i in range(pop_len-1):
        # if(random.random()<pc):

        cpoint=random.randint(0,len(population[0]))
        #在种群个数内随机生成单点交叉点
        temporary1=[]
        temporary2=[]

        temporary1.extend(population[i][0:cpoint])
        temporary1.extend(population[i+1][cpoint:len(population[i])])
        #将tmporary1作为暂存器，暂时存放第i个染色体中的前0到cpoint个基因，
        #然后再把第i+1个染色体中的后cpoint到第i个染色体中的基因个数，补充到temporary1后面

        temporary2.extend(population[i+1][0:cpoint])
        temporary2.extend(population[i][cpoint:len(population[i])])
        # 将tmporary2作为暂存器，暂时存放第i+1个染色体中的前0到cpoint个基因，
        # 然后再把第i个染色体中的后cpoint到第i个染色体中的基因个数，补充到temporary2后面
        population[i]=temporary1
        population[i+1]=temporary2
        # 第i个染色体和第i+1个染色体基因重组/交叉完成
    print(population)

def CMutate(testcase,maxTCLen):
    p1 = random.randint(1,100)
    if p1 >= 50:
        p2 = random.randint(1,maxTCLen) # 1,10
        if p2>= len(testcase):
            testcase += "a"
        else:
            testcase = testcase.rstrip(testcase[-1])
    dll = ctypes.cdll.LoadLibrary("./cmutate.dll")
    dll.mutate.restype = ctypes.c_uint64            # 由于py的bug，需要将调用方法的restype做出调整
    example = bytes(testcase,encoding="utf8")      # 传入字节
    r1 = int(random.random()*10000)
    r2 = random.randint(1,127)
    res = dll.mutate(example,r1,r2)
    res = ctypes.string_at(res)
    res = res.decode("utf8")
    print("res:",res)
    return res

def generateReport(source_loc,fuzzInfoDict):
    basic_loc = re.sub(source_loc.split("\\")[-1],"",source_loc)
    allCoveredNode =  fuzzInfoDict["已覆盖结点"]
    report_loc = basic_loc+"out\\测试报告.txt"
    reportContent = "________________________________________________________________\n"
    reportContent+= "|\t\t\t测试报告\t\t\t|\n"
    reportContent+= "|——————————————————————————|\n"
    reportContent+= "|            测试时间： "+fuzzInfoDict["测试时间"]+"s\t|     已保存测试用例： "+fuzzInfoDict["已保存测试用例"]+"个\t|\n"
    reportContent+= "|            测试对象："+fuzzInfoDict["测试对象"]+"\t|  已检测到缺陷数量： "+fuzzInfoDict["已检测到缺陷数量"]+"个\t|\n"
    reportContent+= "|            循环次数："+fuzzInfoDict["循环次数"]+"次\t|     已触发缺陷次数： "+fuzzInfoDict["已触发缺陷次数"]+"次\t|\n"
    reportContent+= "|——————————————————————————|\n"
    reportContent+= "|     制导目标数量： "+fuzzInfoDict["制导目标数量"]+"个\t|  超时测试用例数量： "+fuzzInfoDict["超时测试用例数量"]+"个\t|\n"
    reportContent+= "|            生成速度： "+fuzzInfoDict["生成速度"]+"个/s\t|     已发现结点数量： "+fuzzInfoDict["已发现结点数量"]+"\t|\n"
    reportContent+= "|            执行速度： "+fuzzInfoDict["执行速度"]+"个/s\t|     已覆盖结点数量： "+str(len(allCoveredNode))+"\t|\n"
    reportContent+= "|  已生成测试用例： "+fuzzInfoDict["已生成测试用例"]+"个\t|            整体覆盖率： "+fuzzInfoDict["整体覆盖率"]+"%\t|\n"
    reportContent+= "|——————————————————————————|\n"
    # testcases = getDirContent(basic_loc+"out\\testcases")
    # savedCrashes = getDirContent(basic_loc+"out\\crash")
    # for i in range(len(testcases)):
    #     reportContent += "已保存的测试用例"+str(i+1)+": "+testcases[i]+"\n"
    # for i in range(len(savedCrashes)):
    #     reportContent += "已触发缺陷的测试用例"+str(i+1)+": "+savedCrashes[i]+"\n"
    reportContent += "已发现结点名称: "+str(allNode)+"\n"
    reportContent += "已覆盖结点名称: "+str(allCoveredNode)+"\n"
    reportContent += "\n当前位置: \t\t\t"+basic_loc+"out\n"
    reportContent += "已保存的测试用例位置: \t"+basic_loc+"out\\testcases\n"
    reportContent += "已保存的触发缺陷用例位置: \t"+basic_loc+"out\crash\n"
    reportContent += "所有变异体位置: \t\t"+basic_loc+"out\\mutate\n"
    reportContent += "保存的超时测试用例位置: \t"+basic_loc+"out\\timeout\n"
    f = open(report_loc,mode="w")
    f.write(reportContent)
    f.close()


def fuzz(source_loc,ui,uiFuzz,fuzzThread):
    '''
    @description: 模糊测试的函数, 是该项目核心的函数之一
    @param {*} source_loc 列表, 其中存储了所有C文件的位置
    @param {*} ui 主页面
    @param {*} uiFuzz 模糊测试页面
    @param {*} fuzzThread 模糊测试页面新开的测试线程, 单线程的话在测试期间会卡住
    @return {*}
    '''
    for source in source_loc:
        if not os.path.exists(source):
            print(source)
            fuzzThread.fuzzInfoSgn.emit("\n\n\t\t被测文件不存在!")
            return "source not exist!"

    # 当前所在目录
    now_loc = re.sub(source_loc[0].split("\\")[-1],"",source_loc[0])
    # 输出exe和obj的位置
    output_loc = now_loc
    # 可执行文件位置
    program_loc = now_loc + "instrument.exe"
    # 初始测试用例位置
    seed_loc = now_loc + "in\\seed"
    # 调用图位置
    graph_loc = now_loc + "graph_cg.txt"
    # 插装后的文件位置，因为是多文件，所以这里用了列表
    instrument_loc = []

    # 因为要多文件编译，所以记录一下每个文件的位置，以便生成插装的源文件
    for source in source_loc:
        sourceName = source.split("\\")[-1]
        instrument_loc.append(re.sub(sourceName, "ins_" + sourceName, source))

    # 获取插装变量的名字
    instrument_var = open(now_loc + "in\\instrument.txt").readline()
    instrument_var = instrument_var.split(" ")[-1].split(":")[0].rstrip("\n")
    instr.instrument(source_loc, instrument_loc, output_loc, instrument_var)
    # 创建函数调用图
    cg.createCallGraph(source_loc,graph_loc)

    # 加载所需的DLL文件
    # MAI是Mutate And Instrument的缩写
    MAIdll = ctypes.cdll.LoadLibrary(now_loc + "in\\mutate_instru.dll")

    # 如果已经有out了, 就删掉它
    if os.path.exists(now_loc+"\\out"):
        shutil.rmtree(now_loc + "\\out")

    coverage = [0,0]
    allCoveredNode = []     # 储存了所有被覆盖到的结点
    coverNode = []          # 储存了某个测试用例覆盖的节点
    callGraph = []
    testcase = []           # 存储测试用例
    TC_data = []            # 将测试用例、距离、适应度拼接成一个二维列表
    targetSet = []          # 目标集
    cycle = 0               # 轮回次数
    count_test = 1          # 标记要保存的测试用例序号
    uniq_crash = 1          # 标记要保存的能使程序异常退出的测试用例
    count_timeout = 1       # 超时测试用例数量
    mutateNum = 1           # 统计总共变异了多少次
    maxMutateTC = 200       # 最多保留多少个变异的测试用例
    maxTimeout = 20         # 最大超时时间
    maxTCLen = 10           # 测试用例最大长度
    mutateTime = 0          # 测试用例生成时间
    executeTime = 0         # 执行总时间

    maxMutateTC = int(ui.TCNumPerCyc.text())
    maxTimeout = int(ui.timeoutLEdit.text())
    # 设置目标集
    targetSet = ui.targetSetInfo.toPlainText()
    targetSet = re.sub("[^A-Za-z1-9_\n]","",targetSet)
    # if len(targetSet) == 0:
    #     print("No target!")
    #     return
    targetSet = targetSet.split("\n")
    print("targetSet:",targetSet)

    start = time.time()
    end = time.time()


    # 统计所有的函数，读取调用图
    callGraph = loadData(graph_loc)
    global allNode
    allNode = public.getAllFunctions(source_loc)
    allNode = sorted(set(allNode),key=allNode.index)
    print("allNode:", allNode)

    # 读取初始种子测试用例
    testcase.append(open(seed_loc, mode="rb").read())
    # testcase[0] = [str(data) for data in testcase[0]]
    mkdir(now_loc + "\\out\\testcases")
    mkdir(now_loc+"\\out\\crash")
    mkdir(now_loc+"\\out\\timeout")

    # 设置终止条件
    if ui.stopByCrash.isChecked():
        condition = "uniq_crash < 2"
    elif ui.stopByTime.isChecked():
        fuzzTime = int(ui.fuzzTime.text())
        if ui.timeUnit.currentText() == "分钟":
            fuzzTime *= 60
        else:
            fuzzTime *= 3600
        condition = "end-start<"+str(fuzzTime)
    else:
        stopNum = int(ui.stopByTCNum.text())+1
        condition = "mutateNum<"+str(stopNum)

    # Ready to start fuzz!
    while eval(condition):
        if uiFuzz.stop == True:
            break
        # 运行.exe文件并向其中输入，根据插桩的内容获取覆盖信息
        executeStart = time.time()
        executeNum = len(testcase)
        for i in range(0,len(testcase)):
            uiFuzz.textBrowser.append("正在执行第"+str(i)+"个测试用例")
            returnData = getFitness(testcase[i],targetSet,program_loc,callGraph,maxTimeout,MAIdll)
            distance = returnData[1]
            fitness = returnData[2]
            coverNode = returnData[3]
            crash = returnData[4]
            timeout = returnData[5]
            if crash:
                crashFile = open(now_loc + "\\out\\crash\\crash" + str(uniq_crash), mode="wb")
                crashFile.write(testcase[i])
                crashFile.close()
                uniq_crash += 1
            if timeout:
                timeoutFile = open(now_loc + "\\out\\timeout\\timeout" + str(count_timeout), mode="wb")
                timeoutFile.write(testcase[i])
                timeoutFile.close()
                count_timeout += 1
            for node in returnData[3]:
                allCoveredNode.append(node)
            allCoveredNode = sorted(set(allCoveredNode),key=allCoveredNode.index)
            #计算覆盖率
            coverage[1] = len(allCoveredNode)/len(allNode)
            if coverage[1] > coverage[0]:
                # 把能让覆盖率增加的测试用例保存到output\testcase文件夹中
                coverage[0] = coverage[1]
                testN = open(now_loc + "\\out\\testcases\\test" + str(count_test).zfill(6), mode="wb")
                testN.write(testcase[i])
                testN.close()
                count_test += 1
            TC_data.append([testcase[i],distance,fitness,coverNode])
        # TC_data存储了测试用例及所对应的距离、适应度和覆盖到的点，是一个二维列表，并根据距离从小到大进行排序
        executeEnd = time.time()
        TC_data = sorted(TC_data,key=itemgetter(1))
        mkdir(now_loc + "\\out\\mutate\\cycle"+str(cycle))
        mutateStart = time.time()               # 记录变异开始时间
        checkpoint = mutateNum
        while mutateNum - checkpoint < maxMutateTC:
            pTargetMutate = 98.0
            pNoTargetMutate = 50.0
            if len(targetSet) == 0:
                pm = pNoTargetMutate
            else:
                pm = pTargetMutate
            pm = 98.0
            for data in TC_data:
                if random.randint(0,100) < pm:    # 小于阈值就进行下列变异操作
                    mutateSavePath = now_loc + "\\out\\mutate\\cycle"+str(cycle)+"\\mutate" + str(mutateNum).zfill(6)
                    mutate(data[0], mutateSavePath, MAIdll)
                    mutateNum += 1
                pTargetMutate -= (98.0/maxMutateTC)
                if mutateNum - checkpoint >= maxMutateTC:
                    break
        # 读取文件夹下的变异的测试用例, 赋值到testcase
        testcase.clear()
        mutateSavePath = now_loc + "\\out\\mutate\\cycle"+str(cycle)+"\\"
        files = os.listdir(mutateSavePath)
        for file in files:
            f = open(mutateSavePath + file, mode = "rb")
            testcase.append(f.read())
        cycle += 1
        end=time.time()
        # 生成简短的测试信息
        mutateTime = end - mutateStart
        executeTime = executeEnd - executeStart
        fuzzInfo = "\n测试时间\t\t\t"+str(int(end-start))+"s\n"
        fuzzInfo += "循环次数\t\t\t"+str(cycle)+"\n"
        fuzzInfo += "变异测试用例数量\t\t"+str(mutateNum-1)+"\n"
        fuzzInfo += "缺陷数量\t\t\t"+str(uniq_crash-1)+"("+str(crashes)+")\n"
        fuzzInfo += "测试用例生成速度\t\t"+str(int(maxMutateTC/mutateTime))+"个/s\n"
        fuzzInfo += "测试用例执行速度\t\t"+str(int(executeNum/executeTime))+"个/s\n"
        fuzzThread.fuzzInfoSgn.emit(fuzzInfo)

    # 生成测试报告
    fuzzThread.fuzzInfoSgn.emit(fuzzInfo)
    fuzzInfoDict = {"测试时间" : str(int(end-start)),
                    "测试对象" : source_loc[0].split("\\")[-1],
                    "循环次数" : str(cycle),
                    "制导目标数量" : str(len(targetSet)),
                    "生成速度" : str(int(maxMutateTC/mutateTime)),
                    "执行速度" : str((int(executeNum/executeTime))),
                    "已生成测试用例" : str(mutateNum-1),
                    "已保存测试用例" : str(count_test-1),
                    "已检测到缺陷数量" : str(uniq_crash-1),
                    "已触发缺陷次数" : str(crashes),
                    "超时测试用例数量" : str(count_timeout-1),
                    "已发现结点数量" : str(len(allNode)),
                    "已覆盖结点" : allCoveredNode,
                    "整体覆盖率" : str(int(coverage[1]*100))}
    generateReport(source_loc[0],fuzzInfoDict)
    uiFuzz.textBrowser.append("\n已生成测试报告! 点击<查看结果>按钮以查看")

    print("\n",allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs"%(cycle,coverage[1],end-start))


def initGloablVariable():
    '''
    @description: 初始化全局变量
    @param {*}
    @return {*}
    '''
    global crash_code
    global crashNode
    global allNode
    global crashes
    crash_code.clear()
    crashNode.clear()
    allNode = ["main"]
    isCrash = 0
    crashes = 0

# ================全局变量=====================================================================
crash_code = []         # 存储异常退出导致的错误代码
crashNode = []          # 触发错误覆盖到了哪些结点，如果覆盖到crashNode中没有的结点，就将该结点
                        # 添加到crashNode中，并保存测试用例
allNode = []            # 储存了图里的所有结点
isCrash = 0             # 程序的返回值
crashes = 0             # 统计触发了多少次缺陷
returnUDPInfo = []      # 存储发送回来的UDP数据包
# ============================================================================================

if __name__ == "__main__":
    data = bytes([251, 17, 111, 96, 45, 48, 0, 0, 22, 10, 16, 15, 13, 13, 101, 0, 214, 0, 0, 0, 153, 162, 1, 0, 30, 71, 202, 129, 247, 87, 182, 25, 30, 197, 1, 0, 121, 0, 0, 2, 200, 1, 1, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 2, 0, 7, 4, 62, 0, 114, 91, 1, 232, 78, 0, 248, 228, 1, 44, 112, 1])
    dll = ctypes.cdll.LoadLibrary("C:\\Users\\Radon\\Desktop\\fuzztest\\4th\\example_21.7.5\\in\\mutate_instru.dll")
    dll.setInstrumentValueToZero(data)
    print("instrValue:", dll.getInstrumentValue(data))