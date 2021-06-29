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
from PyQt5.QtCore import pyqtSignal

import callgraph as cg
import instrument as instr
import staticAnalysis as sa

def mkdir(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False
        
def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]

def loadData(fileName):
    file = open(fileName,'r')#read file
    weightedEdges = []
    elementList = []
    for line in file:
        data = line.split(',')
        elementList.append(data[0])
        elementList.append(data[1])
        allNode.append(data[0])
        allNode.append(data[1])
        elementList.append(float(1/int(data[2])))
        elementTuple = tuple(elementList)
        elementList.clear()
        weightedEdges.append(elementTuple)
    file.close()
    return weightedEdges

def getDistance_shortest(graph,nodeSet,target):
    G = nx.Graph()
    G.add_weighted_edges_from(graph)
    shortest = 999.0
    distance = 0
    for node in nodeSet:
        distance = nx.dijkstra_path_length(G,node,target)
        if distance < shortest:
            shortest = distance
    return shortest

def getDistance_average(graph,nodeSet,target):
    G = nx.Graph()
    G.add_weighted_edges_from(graph)
    distance = 0
    for node in nodeSet:
        distance += nx.dijkstra_path_length(G,node,target)
    distance = distance/len(nodeSet)
    return distance

def getTestcase(position):
    testcase = []
    files = os.listdir(position)
    for file in files:
        position2 = position + "\\" + file
        with open(position2, "r", encoding="utf-8") as f:
            testcase.append(f.read())
            f.close()
    return testcase

def checkCrash(testcase, returncode, coverNode):           #这里的检测缺陷方法是否合适？
    global crash_code
    global crashNode
    # print("coverNode:",coverNode)
    if returncode != 0:
        # print("there is a crash.")
        if not returncode in crash_code:
            print("returncode:",returncode)
            crash_code.append(returncode)
            if len(coverNode) == 0:
                pass
            else:
                crashNode.extend(coverNode)
            return True
        if not set(crashNode) > set(coverNode):
            crashNode.extend(coverNode)
            print("Crash code repeat, but cover node not equal.")
            return True
    return False

def getFitness(testcase,program_loc,callGraph,maxTimeout):
    testcase = str(testcase)
    coverNode = []
    p=Popen([program_loc],stdout=PIPE,stdin=PIPE,stderr=STDOUT)
    try:
        out = p.communicate(input=bytes(testcase,encoding="utf8"),timeout=maxTimeout)[0]
    except TimeoutExpired:
        p.kill()
        out = b"timeout"
    p.kill()
    output = out.decode().split("\n")
    for j in range(0,len(output)):
        if "execute-" in output[j]:
            coverNode.append(get_str_btw(output[j],"execute-","\r"))
            coverNode = sorted(set(coverNode),key=coverNode.index)
    global crashes
    if p.returncode != 0:
        crashes += 1
    crashResult = checkCrash(testcase,p.returncode,coverNode)
    # 适应度部分已简化
    distance = 1
    fitness = 1/distance
    return (testcase,distance,fitness,coverNode,crashResult)

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

def fuzz(source_loc,ui,uiFuzz,fuzzThread):
    if not os.path.exists(source_loc):
        fuzzThread.fuzzInfoSgn.emit("\n\n\t\t被测文件不存在!")
        return "not exist!"

    now_loc = re.sub(source_loc.split("\\")[-1],"",source_loc)      # 当前所在目录
    instrument_loc = now_loc + "instrument.c"
    output_loc = now_loc                                            # 输出exe和obj的位置
    program_loc = now_loc + "instrument.exe"    #可执行文件位置
    testcase_loc = now_loc + "in"             #初始测试用例位置
    graph_loc = now_loc + "graph_cg.txt"   #调用图位置

    instr.instrument(source_loc,instrument_loc,output_loc) 
    cg.createCallGraph(source_loc,graph_loc)



    # dll = ctypes.cdll.LoadLibrary("D:\\VS2015Project\\FuzzExperiment\\Project8\\Project8\\cmutate.dll")
    # dll.mutate.restype = ctypes.c_uint64            # 由于py的bug，需要将调用方法的restype做出调整
    # example = bytes("abcdefg",encoding="utf8")      # 传入字节
    # r1 = int(random.random()*10000)
    # r2 = random.randint(1,127)
    # res = dll.mutate(example,r1,r2)
    # res = ctypes.string_at(res)
    # print("res:",res.decode("utf8"))

    # p=Popen([program_loc],stdout=PIPE,stdin=PIPE,stderr=STDOUT)
    # try:
    #     info = p.communicate(input=bytes("303453",encoding="utf8"),timeout=10)
    #     out = info[0]
    # except TimeoutExpired:
    #     out = b"timeout"
    #     print("超时")
    # p.kill()
    # print(p.returncode)
    # print(out.decode())



    # if not os.path.exists(testcase_loc):
    #     print("input file not exist!")
    #     return 
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
    uniq_crash = 1         # 标记要保存的能使程序异常退出的测试用例
    mutateNum = 1           # 统计总共变异了多少次
    maxMutateTC = 200       # 最多保留多少个变异的测试用例
    maxTimeout = 20         # 最大超时时间
    maxHit = 10             # 击中当前目标多少次后就更换目标
    maxTCLen = 10           # 测试用例最大长度
    mutateTime = 0          # 测试用例生成时间
    executeTime = 0         # 执行总时间

    maxMutateTC = int(ui.TCNumPerCyc.text())
    maxTimeout = int(ui.timeoutLEdit.text())

    # 获取目标部分已被注释掉
    # targetSet = ui.targetSetInfo.toPlainText()
    # targetSet = re.sub("[^A-Za-z1-9_]","",targetSet)
    # if len(targetSet) == 0:
    #     print("No target!")
    #     return
    # targetSet = targetSet.split("\n")
    # print("targetSet:",targetSet)
    # print(targetSet)

    # cg.createCallGraph(source_loc,graph_loc)
    # instr.instrument(source_loc,instrument_loc,output_loc) 

    start = time.time()
    end = time.time()



    callGraph = loadData(graph_loc)
    global allNode
    allNode = sorted(set(allNode),key=allNode.index)

    # testcase = getTestcase(testcase_loc)
    testcase = ["12cde","ab345"]
    mkdir(now_loc + "\\out\\testcases")
    mkdir(now_loc+"\\out\\crash")

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
            return
        # 运行.exe文件并向其中输入，根据插桩的内容获取覆盖信息
        executeStart = time.time()
        executeNum = len(testcase)
        for i in range(0,len(testcase)):
            global crashNode
            crashNode = sorted(set(crashNode))
            returnData = getFitness(testcase[i],program_loc,callGraph,maxTimeout)
            distance = returnData[1]
            fitness = returnData[2]
            coverNode = returnData[3]
            crash = returnData[4]
            if crash:
                crashFile = open(now_loc + "\\out\\crash\\crash" + str(uniq_crash) + ".txt", mode="w")
                crashFile.write(str(testcase[i]))
                crashFile.close()
                uniq_crash += 1
            for node in returnData[3]:
                allCoveredNode.append(node)
            allCoveredNode = sorted(set(allCoveredNode),key=allCoveredNode.index)
            #计算覆盖率
            coverage[1] = len(allCoveredNode)/len(allNode)
            if coverage[1] > coverage[0]:
                # 把能让覆盖率增加的测试用例保存到output\testcase文件夹中
                coverage[0] = coverage[1]
                testN = open(now_loc + "\\out\\testcases\\test" + str(count_test).zfill(6) + ".txt", mode="w")
                testN.write(str(testcase[i]))
                testN.close()
                count_test += 1
            TC_data.append([testcase[i],distance,fitness,coverNode])
        # TC_data存储了测试用例及所对应的距离、适应度和覆盖到的点，是一个二维列表，并根据距离从小到大进行排序
        executeEnd = time.time()
        TC_data = sorted(TC_data,key=itemgetter(1))
        mkdir(now_loc + "\\out\\mutate\\cycle"+str(cycle))
        testcase.clear()
        mutateStart = time.time()               # 记录变异开始时间
        checkpoint = mutateNum
        while mutateNum-checkpoint<maxMutateTC:
            # 所有人变异概率平等，均是50%
            pm = 50.0
            for data in TC_data:
                if random.randint(0,100)<pm:    # 小于阈值就进行下列变异操作
                    mutateFile = open(now_loc + "\\out\\mutate\\cycle"+str(cycle)+"\\mutate" + str(mutateNum).zfill(6) + ".txt", mode="w")
                    # temp = mutate(data[0])
                    temp = CMutate(data[0],maxTCLen)
                    testcase.append(temp)
                    mutateFile.write(str(temp))
                    mutateNum += 1
                    mutateFile.close()
                if mutateNum-checkpoint>=maxMutateTC:
                    break
        cycle += 1
        end=time.time()
        
        mutateTime = end - mutateStart
        executeTime = executeEnd - executeStart
        fuzzInfo = "\n测试时间\t\t\t"+str(int(end-start))+"s\n"
        fuzzInfo += "循环次数\t\t\t"+str(cycle)+"\n"
        fuzzInfo += "变异测试用例数量\t\t"+str(mutateNum-1)+"\n"
        fuzzInfo += "缺陷数量\t\t\t"+str(uniq_crash-1)+"("+str(crashes)+")\n"
        fuzzInfo += "测试用例生成速度\t\t"+str(int(maxMutateTC/mutateTime))+"个/s\n"
        fuzzInfo += "测试用例执行速度\t\t"+str(int(executeNum/executeTime))+"个/s\n"
        fuzzThread.fuzzInfoSgn.emit(fuzzInfo)

    print("\n",allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs"%(cycle,coverage[1],end-start))

def initGloablVariable():
    global crash_code
    global crashNode
    global allNode
    global crashes
    crash_code.clear()
    crashNode.clear()
    allNode.clear()
    crashes = 0

crash_code = []         # 存储异常退出导致的错误代码
crashNode = []          # 触发错误覆盖到了哪些结点，如果覆盖到crashNode中没有的结点，就将该结点
                        # 添加到crashNode中，并保存测试用例
allNode = []            # 储存了图里的所有结点
crashes = 0             # 统计触发了多少次缺陷

if __name__ == "__main__":
    source_loc = "C:\\Users\\Radon\\Desktop\\fuzztest\\main.c"
    ui = "111"
    uiFuzz = "222"
    fuzzThread = "fuzzThread"
    fuzz(source_loc,ui,uiFuzz,fuzzThread)