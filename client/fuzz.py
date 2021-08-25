import ctypes, _ctypes
import json
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

import public
from util.check_code import calculate_check_code_from_dec


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


def getFitness(testcase, targetSet, senderAddress, receiverAddress, callGraph, maxTimeout, dllDict, isMutateInRange):
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
    dllDict : dict
        编译好的dll文件存储在该dict中，key是str，value是CDLL
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
    # 启动线程2，用于监控
    thread2 = threading.Thread(target=threadMonitor, name="thread_monitor", args=(senderAddress,))
    thread2.start()

    # 测试用例是bytes
    data = testcase
    # 如果需要将变异体设置在用户指定的范围内的话，就调用相应的函数
    if isMutateInRange:
        dllDict["mutate"].setValueInRange(data)

    # 发送测试用例
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
    # 计算距离
    distance = 500
    for target in targetSet:
        distance += getDistance_average(callGraph, coverNode, target)
    # 如果距离计算结果是0，或者这个测试用例触发了缺陷，就统一将距离设置为1
    # 因为测试用例触发了缺陷的话程序就崩溃了，导致无法获得覆盖信息
    if distance == 0 or isCrash:
        distance = 1
    fitness = 1 / distance
    crashResult = isCrash == 10
    timeout = False
    return (testcase, distance, fitness, coverNode, crashResult, timeout)


def mutate(testcase, mutateSavePath, dllDict):
    """根据南京大学徐安孜同学写的例子对变异进行了改写，
    使用预先编译好的dll文件对测试用例进行变异

    Parameters
    ----------
    testcase : bytes
        测试用例
    mutateSavePath : str
        变异测试用例的保存路径, dll会将变异后的测试用例保存到指定位置
    dllDict : dict
        编译好的dll文件存储在该dict中，key是str，value是CDLL

    Notes
    -----
    [description]
    """

    # 将对测试用例进行变异并保存为二进制文件和txt文件
    mutateStartTime = time.time()
    test_case_visualization_file_path = mutateSavePath + ".txt"
    mutateSavePath_backup = mutateSavePath
    txtSavePath = bytes(test_case_visualization_file_path, encoding="utf8")
    mutateSavePath = bytes(mutateSavePath, encoding="utf8")
    r = random.randint(0, 255)
    dllDict["mutate"].mutate(testcase, mutateSavePath, r)
    dllDict["mutate"].testcaseVisualization(testcase, txtSavePath)
    mutateTime = time.time() - mutateStartTime

    # 校验
    checkStartTime = time.time()
    # structDict = json.load(open(test_case_visualization_file_path.split("out")[0] + "\\in\\input.json"))
    # check_code_name, check_code_field = None, list()
    # structName = None
    # for struct_name in structDict.keys():
    #     structName = struct_name
    #     for var_type_name in structDict[struct_name].keys():
    #         if structDict[struct_name][var_type_name]["checkCode"]:
    #             check_code_name = var_type_name
    #         elif structDict[struct_name][var_type_name]["checkField"]:
    #             check_code_field.append(var_type_name)
    # if check_code_name is None and len(check_code_field) == 0:
    #     print("没有设置校验字段和校验码位置，跳过校验步骤")
    #     checkTime = time.time() - checkStartTime
    #     return (mutateTime, checkTime)
    # elif check_code_name is None and len(check_code_field) != 0 or check_code_name is not None and len(
    #         check_code_field) == 0:
    #     print("校验字段或校验码有一个未设置，跳过校验步骤")
    #     checkTime = time.time() - checkStartTime
    #     return (mutateTime, checkTime)
    # check_code_field_value_list = list()
    # f = open(test_case_visualization_file_path, mode="r")
    # testcase_file_str_list = f.readlines()
    # f.close()
    # for one_line in testcase_file_str_list:
    #     var_name = one_line.split(":")[0]
    #     var_value = one_line.split(":")[1].strip()
    #     for one_check_code_field in check_code_field:
    #         if var_name in one_check_code_field:
    #             check_code_field_value_list.append(int(var_value))
    # check_code_method = open(test_case_visualization_file_path.split("out")[0] + "\\in\\checkCodeMethod.txt",
    #                          encoding="utf", mode="r").readline()
    # check_code = calculate_check_code_from_dec(dec_data_list=check_code_field_value_list,
    #                                            method=check_code_method.split("_")[0],
    #                                            algorithm=check_code_method.split("_")[1])
    # structDict[structName][check_code_name]["value"] = check_code
    # header_loc = open(test_case_visualization_file_path.split("out")[0] + "\\in\\header_loc.txt", mode="r",
    #                   encoding="utf").readlines()  # 读取头文件
    # public.gen_test_case_from_structDict(header_loc, structName, structDict=structDict, path=mutateSavePath_backup)
    # print("check code is:" + check_code)
    checkTime = time.time() - checkStartTime

    return (mutateTime, checkTime)


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


def generateReport(header_loc_list, fuzzInfoDict):
    """生成测试报告

    Parameters
    ----------
    header_loc_list : list
        存储了所有源文件的位置
    fuzzInfoDict : [type]
        存储了模糊测试相关信息的字典

    Notes
    -----
    [description]
    """
    basic_loc = re.sub(header_loc_list[0].split("/")[-1], "", header_loc_list[0])
    allCoveredNode = fuzzInfoDict["已覆盖结点"]
    report_loc = basic_loc + "out/测试报告.txt"

    reportContent = "=============================测试报告============================\n"
    reportContent += "测试对象: "
    for source in header_loc_list:
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


def fuzz(header_loc_list, ui, uiPrepareFuzz, uiFuzz, fuzzThread):
    """模糊测试的函数, 是该项目核心的函数之一

    Parameters
    ----------
    header_loc_list : list
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

    # 当前所在目录
    now_loc = re.sub(header_loc_list[0].split("/")[-1], "", header_loc_list[0])
    # 可执行文件位置
    program_loc = now_loc + "instrument.exe"
    # 初始测试用例位置
    seed_loc = now_loc + "in/seed"
    # 调用图位置
    graph_loc = now_loc + "in/callgraph.txt"

    # 加载所需的DLL文件，并将CDLL存入一个字典，以便调用
    mutateDll = ctypes.cdll.LoadLibrary(now_loc + "in/mutate.dll")
    instrumentDll = ctypes.cdll.LoadLibrary(now_loc + "in/insFunc.dll")
    dllDict = {"mutate": mutateDll, "instrument": instrumentDll}

    # 设置地址
    senderAddress = uiPrepareFuzz.senderIPLabel.text()
    receiverAddress = uiPrepareFuzz.receiverIPLabel.text()

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
    mutateTime = 0  # 测试用例生成时间
    executeTime = 0  # 执行总时间

    maxMutateTC = int(ui.TCNumPerCyc.text())
    maxTimeout = int(ui.timeoutLEdit.text())
    # 设置目标集
    targetSet = fuzzThread.targetSetInfo
    print("targetSet:", targetSet)
    # 变异体是否需要在用户指定的范围内
    isMutateInRange = ui.isMutateInRangeCheckBox.isChecked()

    start = time.time()
    end = time.time()

    # 统计所有的函数，读取调用图
    callGraph = loadData(graph_loc)
    global allNode
    allNode = uiPrepareFuzz.allNodes
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
        stopNum = int(ui.TCNumsLineEdit.text()) + 1
        condition = "mutateNum<" + str(stopNum)

    # Ready to start fuzz!
    global crashes
    while eval(condition):
        # 运行.exe文件并向其中输入，根据插桩的内容获取覆盖信息
        executeStart = time.time()
        executeNum = len(testcase)

        uiFuzz.textBrowser.append("\n\n")
        for i in range(0, len(testcase)):
            print()
            uiFuzz.textBrowser.append("正在执行第" + str(i + 1) + "个测试用例")
            returnData = getFitness(testcase[i], targetSet, senderAddress, receiverAddress, callGraph, maxTimeout,
                                    dllDict,
                                    isMutateInRange)
            distance = returnData[1]
            fitness = returnData[2]
            coverNode = returnData[3]
            crash = returnData[4]
            timeout = returnData[5]
            if crash:
                crashFile = open(now_loc + "/out/crash/crash" + str(uniq_crash), mode="wb")
                crashFile.write(crashTC)
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

        checkpoint = mutateNum
        mutateAndCheckTime = list()
        uiFuzz.textBrowser.append("校验中...")
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
                    mutateAndCheckTime.append(mutate(data[0], mutateSavePath, dllDict))
                    mutateNum += 1
                pTargetMutate -= (98.0 / maxMutateTC)
                if mutateNum - checkpoint >= maxMutateTC:
                    break

        # 读取文件夹下的变异的测试用例, 赋值到testcase
        testcase.clear()
        mutateSavePath = now_loc + "/out/mutate/cycle" + str(cycle) + "/"
        files = os.listdir(mutateSavePath)
        for file in files:
            # 跳过后缀名为txt的可视化文件
            if "." in file:
                continue
            f = open(mutateSavePath + file, mode="rb")
            testcase.append(f.read())
            f.close()
        cycle += 1
        end = time.time()

        # 生成简短的测试信息
        mutateTime = 0
        checkTime = 0
        for data in mutateAndCheckTime:
            mutateTime += data[0]
            checkTime += data[1]
        # 防止除0
        if mutateTime == 0:
            mutateTime = 0.1
        if executeTime == 0:
            executeTime = 0.1
        executeTime = executeEnd - executeStart
        fuzzInfo = "\n测试时间\t\t\t" + str(int(end - start)) + "s\n"
        fuzzInfo += "循环次数\t\t\t" + str(cycle) + "\n"
        fuzzInfo += "变异测试用例数量\t\t" + str(mutateNum - 1) + "\n"
        fuzzInfo += "缺陷数量\t\t\t" + str(uniq_crash - 1) + "(" + str(crashes) + ")\n"
        fuzzInfo += "测试用例生成速度\t\t" + str(int(maxMutateTC / mutateTime)) + "个/s\n"
        fuzzInfo += "测试用例执行速度\t\t" + str(int(executeNum / executeTime)) + "个/s\n"
        fuzzInfo += "测试用例校验速度\t\t" + str(int(checkTime / maxMutateTC)) + "s/个\n"
        fuzzThread.fuzzInfoSgn.emit(fuzzInfo)
        if uiFuzz.stop == True:
            break

    # 生成测试报告
    fuzzThread.fuzzInfoSgn.emit(fuzzInfo)

    # 防止除0
    if mutateTime == 0:
        mutateTime = 0.1
    if executeTime == 0:
        executeTime = 0.1
    fuzzInfoDict = {"测试时间": str(int(end - start)),
                    "测试对象": header_loc_list[0].split("/")[-1],
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
    generateReport(header_loc_list, fuzzInfoDict)
    uiFuzz.textBrowser.append("\n已生成测试报告! 点击<查看结果>按钮以查看")

    print("\n", allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs" % (cycle, coverage[1], end - start))
    # 释放dll资源
    _ctypes.FreeLibrary(mutateDll._handle)
    _ctypes.FreeLibrary(instrumentDll._handle)


def initGloablVariable():
    """初始化全局变量

    Notes
    -----
    在模糊测试开始前需要初始化一下全局变量
    """
    global crash_code
    global crashNode
    global allNode
    global isCrash
    global crashTC
    global crashes
    crash_code.clear()
    crashNode.clear()
    allNode = ["main"]
    isCrash = 0
    crashTC = bytes()
    crashes = 0


# ================全局变量=====================================================================
crash_code = []  # 存储异常退出导致的错误代码
crashNode = []  # 触发错误覆盖到了哪些结点，如果覆盖到crashNode中没有的结点，就将该结点
# 添加到crashNode中，并保存测试用例
allNode = []  # 储存了图里的所有结点
isCrash = 0  # 计算没有相应的测试用例数量
crashTC = bytes()  # 存储触发缺陷的测试用例
crashes = 0  # 统计触发了多少次缺陷
returnUDPInfo = []  # 存储发送回来的UDP数据包
# ============================================================================================


import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()
