import ctypes
import os
import random
import re
import shutil
import socket
import threading
import time
from operator import itemgetter
from subprocess import *

import networkx as nx

import callgraph as cg
import instrument as instr
import public


def mkdir(path):
    '''
    @description: 创建文件夹
    @param {*} path 文件夹的路径
    @return {*} True表示创建成功，False表示文件夹已存在，创建失败
    '''
    path = path.strip()
    path = path.rstrip("/")
    isExists = os.path.exists(path)
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
    file = open(fileName, 'r')  # read file
    weightedEdges = []
    elementList = []
    for line in file:
        data = line.split(',')
        elementList.append(data[0])
        elementList.append(data[1])
        elementList.append(float(1 / int(data[2])))
        elementTuple = tuple(elementList)
        elementList.clear()
        weightedEdges.append(elementTuple)
    file.close()
    return weightedEdges


def getDistance_shortest(graph, nodeSet, target):
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
            distance = nx.dijkstra_path_length(G, node, target)
            if distance < shortest:
                shortest = distance
        except:
            shortest = 999.0
    return shortest


def getDistance_average(graph, nodeSet, target):
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
            distance += nx.dijkstra_path_length(G, node, target)
        distance = distance / len(nodeSet)
    except:
        distance = 999.0
    # for node in nodeSet:
    #     distance += nx.dijkstra_path_length(G,node,target)
    # distance = distance/len(nodeSet)
    return distance


def getDirContent(position):
    content = []
    files = os.listdir(position)  # 读取position下的文件列表
    for file in files:  # 挨个读取txt文件
        position2 = position + "/" + file
        with open(position2, "r", encoding="utf-8") as f:  # 用with open as的话不必加close()
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
    prog = os.path.dirname(os.path.abspath(__file__)) + "/getudp.py"
    try:
        out = getstatusoutput(prog)
    except BaseException as e:
        print("监视程序出错:", e)
        out = [[],[]]
    # print("getudp.py: ", out)
    global returnUDPInfo
    returnUDPInfo = out[1]


def getFitness(testcase, targetSet, program_loc, callGraph, maxTimeout, MAIdll, isMutateInRange):
    """根据南京大学徐安孜同学的例子重新写了一下获取适应度的函数

    Parameters
    ----------
    testcase : bytes
        需要发送的测试用例，是一个字节序列
    targetSet : list
        目标集
    program_loc : str
        被测程序所在位置
    callGraph : list
        函数调用图，需要借此来计算测试用例和目标集之间的举例，从而计算适应度
    maxTimeout : int
        超时时间
    MAIdll : CDLL
        预先编译好的dll文件
    isMutateInRange : bool
        变异体的值是否要在用户指定的范围内

    Returns
    -------
    tuple
        返回(测试用例, 距离, 适应度, 覆盖点, 是否触发缺陷, 是否超时)

    Notes
    -----
    在目标制导的模糊测试中，根据适应度的高低决定测试用例分配到的
    变异机会的多少，适应度越高的测试用例更有可能变异出覆盖到目标
    的测试用例，因此它得到的变异机会更多，反之则会更少
    """
    # 先启动线程2，用于监控
    thread2 = threading.Thread(target=threadMonitor, name="thread_monitor", )
    thread2.start()
    # 启动线程2后，稍微等下，如果线程1速度快了可能会导致线程2无法获得返回的UDP包
    # 从而陷入一直等待线程2结束的状态
    time.sleep(0.2)
    # 一段时间后，启动线程1，注意args是一个元组，结尾必须有逗号
    thread1 = threading.Thread(target=threadReceiver, name="thread_receiver", args=(program_loc,))
    thread1.start()

    # 形参的测试用例bytes
    data = testcase
    # 发送前，将测试用例的插装变量设置为0
    MAIdll.setInstrumentValueToZero(data)
    # 如果需要将变异体设置在用户指定的范围内的话，就调用相应的函数
    if isMutateInRange:
        MAIdll.setValueInRange(data)

    # 发送测试用例
    s = socket.socket()
    host = socket.gethostname()
    port = 8888
    s.connect((host, port))
    s.send(data)
    s.close()
    # 等待线程1和线程2结束
    thread1.join()
    thread2.join(maxTimeout)

    # 读取返回的UDP包的内容
    global returnUDPInfo
    try:
        returnUDPInfo = returnUDPInfo.split(",")
        returnUDPInfo.pop(-1)
        returnUDPInfo[0] = re.sub("[^0-9]", "", returnUDPInfo[0])
        returnUDPInfo = [int(data) for data in returnUDPInfo]
        print("returnData", returnUDPInfo)
        # 获得覆盖的结点
        instrValue = MAIdll.getInstrumentValue(bytes(returnUDPInfo))
        print("instrValue:", instrValue)
        coverNode = getCoverNode(instrValue)
        print("coverNode:", coverNode)
    except BaseException as e:
        print("解析失败: ", e)
        coverNode = ["main"]
    # 计算距离
    distance = 500
    for target in targetSet:
        distance += getDistance_average(callGraph, coverNode, target)
    # 如果距离计算结果是0，或者这个测试用例触发了缺陷，就统一将距离设置为1
    # 因为测试用例触发了缺陷的话程序就崩溃了，导致无法获得覆盖信息
    if distance == 0 or isCrash:
        distance = 1
    fitness = 1 / distance
    crashResult = isCrash
    timeout = False
    return (testcase, distance, fitness, coverNode, crashResult, timeout)


def mutate(testcase, mutateSavePath, MAIdll):
    """根据南京大学徐安孜同学写的例子对变异进行了改写，
    使用预先编译好的dll文件对测试用例进行变异

    Parameters
    ----------
    testcase : bytes
        测试用例
    mutateSavePath : str
        变异测试用例的保存路径, dll会将变异后的测试用例保存到指定位置
    MAIdll : CDLL
        预先编译好的dll文件，里面有变异操作

    Notes
    -----
    [description]
    """
    # 将对测试用例进行变异并保存
    mutateSavePath = bytes(mutateSavePath, encoding="utf8")
    r = random.randint(0, 255)
    MAIdll.mutate(testcase, mutateSavePath, r)


def crossover(population):
    # pc是概率阈值，选择单点交叉还是多点交叉，生成新的交叉个体
    pop_len = len(population)
    for i in range(pop_len - 1):
        # if(random.random()<pc):

        cpoint = random.randint(0, len(population[0]))
        # 在种群个数内随机生成单点交叉点
        temporary1 = []
        temporary2 = []

        temporary1.extend(population[i][0:cpoint])
        temporary1.extend(population[i + 1][cpoint:len(population[i])])
        # 将tmporary1作为暂存器，暂时存放第i个染色体中的前0到cpoint个基因，
        # 然后再把第i+1个染色体中的后cpoint到第i个染色体中的基因个数，补充到temporary1后面

        temporary2.extend(population[i + 1][0:cpoint])
        temporary2.extend(population[i][cpoint:len(population[i])])
        # 将tmporary2作为暂存器，暂时存放第i+1个染色体中的前0到cpoint个基因，
        # 然后再把第i个染色体中的后cpoint到第i个染色体中的基因个数，补充到temporary2后面
        population[i] = temporary1
        population[i + 1] = temporary2
        # 第i个染色体和第i+1个染色体基因重组/交叉完成
    print(population)


def generateReport(source_loc_list, fuzzInfoDict):
    """生成测试报告

    Parameters
    ----------
    source_loc_list : list
        存储了所有源文件的位置
    fuzzInfoDict : [type]
        存储了模糊测试相关信息的字典

    Notes
    -----
    [description]
    """
    basic_loc = re.sub(source_loc_list[0].split("/")[-1], "", source_loc_list[0])
    allCoveredNode = fuzzInfoDict["已覆盖结点"]
    report_loc = basic_loc + "out/测试报告.txt"

    reportContent = "=============================测试报告============================\n"
    reportContent += "测试对象: "
    for source in source_loc_list:
        reportContent += source.rstrip("\n").split("/")[-1] + ","
    reportContent = reportContent.rstrip(",") + "\n"
    reportContent += "循环次数: " + fuzzInfoDict["循环次数"] + "轮\n"
    reportContent += "测试时间: " + fuzzInfoDict["测试时间"] + "s\n"
    reportContent += "已保存测试用例数量: " + fuzzInfoDict["已保存测试用例"] + "个\n"
    reportContent += "已检测到缺陷数量: " + fuzzInfoDict["已检测到缺陷数量"] + "个\n"
    reportContent += "已触发缺陷次数: " + fuzzInfoDict["已触发缺陷次数"] + "次\n"
    reportContent += "================================================================\n"

    reportContent += "制导目标数量: " + fuzzInfoDict["制导目标数量"] + "个\n"
    reportContent += "测试用例生成速度: " + fuzzInfoDict["生成速度"] + "个/s\n"
    reportContent += "测试用例执行速度: " + fuzzInfoDict["执行速度"] + "个/s\n"
    reportContent += "已生成测试用例: " + fuzzInfoDict["已生成测试用例"] + "个\n"
    reportContent += "超时测试用例数量: " + fuzzInfoDict["超时测试用例数量"] + "个\n"
    reportContent += "已发现结点数量: " + fuzzInfoDict["已发现结点数量"] + "个\n"
    reportContent += "已覆盖结点数量: " + str(len(allCoveredNode)) + "个\n"
    reportContent += "整体覆盖率:" + fuzzInfoDict["整体覆盖率"] + "%\n"
    reportContent += "================================================================\n\n"

    # TODO 考虑一下下面的东西怎么改
    # testcases = getDirContent(basic_loc+"out/testcases")
    # savedCrashes = getDirContent(basic_loc+"out/crash")
    # for i in range(len(testcases)):
    #     reportContent += "已保存的测试用例"+str(i+1)+": "+testcases[i]+"\n"
    # for i in range(len(savedCrashes)):
    #     reportContent += "已触发缺陷的测试用例"+str(i+1)+": "+savedCrashes[i]+"\n"
    reportContent += "已发现结点名称: " + str(allNode) + "\n"
    reportContent += "已覆盖结点名称: " + str(allCoveredNode) + "\n"
    reportContent += "\n当前位置: \t\t\t" + basic_loc + "out\n"
    reportContent += "已保存的测试用例位置: \t" + basic_loc + "out/testcases\n"
    reportContent += "已保存的触发缺陷用例位置: \t" + basic_loc + "out/crash\n"
    reportContent += "所有变异体位置: \t\t" + basic_loc + "out/mutate\n"
    reportContent += "保存的超时测试用例位置: \t" + basic_loc + "out/timeout\n"
    f = open(report_loc, mode="w")
    f.write(reportContent)
    f.close()


def fuzz(source_loc_list, ui, uiFuzz, fuzzThread):
    """模糊测试的函数, 是该项目核心的函数之一

    Parameters
    ----------
    source_loc_list : list
        存储了所有C文件的位置
    ui : Ui_MainWindow
        主页面，即Ui_window
    uiFuzz : Ui_Dialog
        模糊测试信息页面，即Ui_dialog_fuzz
    fuzzThread : QThread
        模糊测试线程

    Returns
    -------
    str
        当模糊测试出现异常时，会返回str类型的数据

    Notes
    -----
    该方法实现了模糊测试的过程，包括变异，保存覆盖新代码的测试
    用例，保存触发缺陷的测试用例等
    """
    for source in source_loc_list:
        if not os.path.exists(source):
            print(source)
            fuzzThread.fuzzInfoSgn.emit("\n\n\t\t被测文件不存在!")
            return "source not exist!"

    # 当前所在目录
    now_loc = re.sub(source_loc_list[0].split("/")[-1], "", source_loc_list[0])
    # 输出exe和obj的位置
    output_loc = now_loc
    # 可执行文件位置
    program_loc = now_loc + "instrument.exe"
    # 初始测试用例位置
    seed_loc = now_loc + "in/seed"
    # 调用图位置
    graph_loc = now_loc + "graph_cg.txt"
    # 插装后的文件位置，因为是多文件，所以这里用了列表
    instrument_loc = []

    # 因为要多文件编译，所以记录一下每个文件的位置，以便生成插装的源文件
    for source in source_loc_list:
        sourceName = source.split("/")[-1]
        instrument_loc.append(re.sub(sourceName, "ins_" + sourceName, source))

    # 获取插装变量的名字，并进行插装与编译
    # 如果存在旧的插装程序，则需要先删除
    if os.path.exists(program_loc):
        os.remove(program_loc)
    instrument_var = open(now_loc + "in/instrument.txt").readline()
    instrument_var = instrument_var.split(" ")[-1].split(":")[0].rstrip("\n")
    # 尝试生成instrument.exe，如果失败了，表示被测程序的源码可能有误
    try:
        instr.instrument(source_loc_list, instrument_loc, output_loc, instrument_var)
    except:
        return "编译程序失败，请检查代码是否正确!"

    # 创建函数调用图
    cg.createCallGraph(source_loc_list, graph_loc)

    # 加载所需的DLL文件
    # MAI是Mutate And Instrument的缩写
    MAIdll = ctypes.cdll.LoadLibrary(now_loc + "in/mutate_instru.dll")

    # 如果已经有out了, 就删掉它
    if os.path.exists(now_loc + "/out"):
        shutil.rmtree(now_loc + "/out")

    coverage = [0, 0]
    allCoveredNode = []  # 储存了所有被覆盖到的结点
    coverNode = []  # 储存了某个测试用例覆盖的节点
    callGraph = []
    testcase = []  # 存储测试用例
    testcaseData = []  # 将测试用例、距离、适应度拼接成一个二维列表
    targetSet = []  # 目标集
    cycle = 0  # 轮回次数
    count_test = 1  # 标记要保存的测试用例序号
    uniq_crash = 1  # 标记要保存的能使程序异常退出的测试用例
    count_timeout = 1  # 超时测试用例数量
    mutateNum = 1  # 统计总共变异了多少次
    maxMutateTC = 200  # 最多保留多少个变异的测试用例
    maxTimeout = 20  # 最大超时时间
    maxTCLen = 10  # 测试用例最大长度
    mutateTime = 0  # 测试用例生成时间
    executeTime = 0  # 执行总时间

    maxMutateTC = int(ui.TCNumPerCyc.text())
    maxTimeout = int(ui.timeoutLEdit.text())
    # 设置目标集
    targetSet = ui.targetSetInfo.toPlainText()
    targetSet = re.sub("[^A-Za-z1-9_\n]", "", targetSet)
    targetSet = targetSet.split("\n")
    print("targetSet:", targetSet)
    # 变异体是否需要在用户指定的范围内
    isMutateInRange = ui.isMutateInRangeCheckbox.isChecked()

    start = time.time()
    end = time.time()

    # 统计所有的函数，读取调用图
    callGraph = loadData(graph_loc)
    global allNode
    allNode = public.getAllFunctions(source_loc_list)
    allNode = sorted(set(allNode), key=allNode.index)
    print("allNode:", allNode)

    # 读取初始种子测试用例
    testcase.append(open(seed_loc, mode="rb").read())
    # testcase[0] = [str(data) for data in testcase[0]]
    mkdir(now_loc + "/out/testcases")
    mkdir(now_loc + "/out/crash")
    mkdir(now_loc + "/out/timeout")

    # 设置终止条件
    if ui.stopByCrash.isChecked():
        condition = "uniq_crash < 2"
    elif ui.stopByTime.isChecked():
        fuzzTime = int(ui.fuzzTime.text())
        if ui.timeUnit.currentText() == "分钟":
            fuzzTime *= 60
        else:
            fuzzTime *= 3600
        condition = "end-start<" + str(fuzzTime)
    else:
        stopNum = int(ui.stopByTCNum.text()) + 1
        condition = "mutateNum<" + str(stopNum)

    # Ready to start fuzz!
    global crashes
    while eval(condition):
        # 运行.exe文件并向其中输入，根据插桩的内容获取覆盖信息
        executeStart = time.time()
        executeNum = len(testcase)

        for i in range(0, len(testcase)):
            uiFuzz.textBrowser.append("正在执行第" + str(i) + "个测试用例")
            returnData = getFitness(testcase[i], targetSet, program_loc, callGraph, maxTimeout, MAIdll, isMutateInRange)
            distance = returnData[1]
            fitness = returnData[2]
            coverNode = returnData[3]
            crash = returnData[4]
            timeout = returnData[5]
            if crash:
                crashFile = open(now_loc + "/out/crash/crash" + str(uniq_crash), mode="wb")
                crashFile.write(testcase[i])
                crashFile.close()
                uniq_crash += 1
                crashes += 1
            if timeout:
                timeoutFile = open(now_loc + "/out/timeout/timeout" + str(count_timeout), mode="wb")
                timeoutFile.write(testcase[i])
                timeoutFile.close()
                count_timeout += 1
            for node in returnData[3]:
                allCoveredNode.append(node)
            allCoveredNode = sorted(set(allCoveredNode), key=allCoveredNode.index)
            # 计算覆盖率
            coverage[1] = len(allCoveredNode) / len(allNode)
            if coverage[1] > coverage[0]:
                # 把能让覆盖率增加的测试用例保存到output\testcase文件夹中
                coverage[0] = coverage[1]
                testN = open(now_loc + "/out/testcases/test" + str(count_test).zfill(6), mode="wb")
                testN.write(testcase[i])
                testN.close()
                count_test += 1
            testcaseData.append([testcase[i], distance, fitness, coverNode])

        # testcaseData存储了测试用例及所对应的距离、适应度和覆盖到的点，是一个二维列表，并根据距离从小到大进行排序
        executeEnd = time.time()
        testcaseData = sorted(testcaseData, key=itemgetter(1))
        mkdir(now_loc + "/out/mutate/cycle" + str(cycle))
        mutateStart = time.time()  # 记录变异开始时间
        checkpoint = mutateNum
        while mutateNum - checkpoint < maxMutateTC:
            pTargetMutate = 98.0
            pNoTargetMutate = 50.0
            if len(targetSet) == 0:
                pm = pNoTargetMutate
            else:
                pm = pTargetMutate
            pm = 98.0
            for data in testcaseData:
                if random.randint(0, 100) < pm:  # 小于阈值就进行下列变异操作
                    mutateSavePath = now_loc + "/out/mutate/cycle" + str(cycle) + "/mutate" + str(mutateNum).zfill(6)
                    mutate(data[0], mutateSavePath, MAIdll)
                    mutateNum += 1
                pTargetMutate -= (98.0 / maxMutateTC)
                if mutateNum - checkpoint >= maxMutateTC:
                    break

        # 读取文件夹下的变异的测试用例, 赋值到testcase
        testcase.clear()
        mutateSavePath = now_loc + "/out/mutate/cycle" + str(cycle) + "/"
        files = os.listdir(mutateSavePath)
        for file in files:
            f = open(mutateSavePath + file, mode="rb")
            testcase.append(f.read())
        cycle += 1
        end = time.time()

        # 生成简短的测试信息
        mutateTime = end - mutateStart
        executeTime = executeEnd - executeStart
        fuzzInfo = "\n测试时间\t\t\t" + str(int(end - start)) + "s\n"
        fuzzInfo += "循环次数\t\t\t" + str(cycle) + "\n"
        fuzzInfo += "变异测试用例数量\t\t" + str(mutateNum - 1) + "\n"
        fuzzInfo += "缺陷数量\t\t\t" + str(uniq_crash - 1) + "(" + str(crashes) + ")\n"
        fuzzInfo += "测试用例生成速度\t\t" + str(int(maxMutateTC / mutateTime)) + "个/s\n"
        fuzzInfo += "测试用例执行速度\t\t" + str(int(executeNum / executeTime)) + "个/s\n"
        fuzzThread.fuzzInfoSgn.emit(fuzzInfo)
        if uiFuzz.stop == True:
            break

    # 生成测试报告
    fuzzThread.fuzzInfoSgn.emit(fuzzInfo)
    fuzzInfoDict = {"测试时间": str(int(end - start)),
                    "测试对象": source_loc_list[0].split("/")[-1],
                    "循环次数": str(cycle),
                    "制导目标数量": str(len(targetSet)),
                    "生成速度": str(int(maxMutateTC / mutateTime)),
                    "执行速度": str((int(executeNum / executeTime))),
                    "已生成测试用例": str(mutateNum - 1),
                    "已保存测试用例": str(count_test - 1),
                    "已检测到缺陷数量": str(uniq_crash - 1),
                    "已触发缺陷次数": str(crashes),
                    "超时测试用例数量": str(count_timeout - 1),
                    "已发现结点数量": str(len(allNode)),
                    "已覆盖结点": allCoveredNode,
                    "整体覆盖率": str(int(coverage[1] * 100))}
    generateReport(source_loc_list, fuzzInfoDict)
    uiFuzz.textBrowser.append("\n已生成测试报告! 点击<查看结果>按钮以查看")

    print("\n", allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs" % (cycle, coverage[1], end - start))


def initGloablVariable():
    """初始化全局变量

    Notes
    -----
    在模糊测试开始前需要初始化一下全局变量
    """
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
crash_code = []  # 存储异常退出导致的错误代码
crashNode = []  # 触发错误覆盖到了哪些结点，如果覆盖到crashNode中没有的结点，就将该结点
# 添加到crashNode中，并保存测试用例
allNode = []  # 储存了图里的所有结点
isCrash = 0  # 程序的返回值
crashes = 0  # 统计触发了多少次缺陷
returnUDPInfo = []  # 存储发送回来的UDP数据包
# ============================================================================================


import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
