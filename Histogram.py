import matplotlib.pyplot as plt
import numpy as np

def cycleHistogram():
    # 统计数据
    number = (1,2,3,4,5,6,7,8,9,10)
    targetCycle = [24,42,2,43,79,92,15,16,5,46]
    noTargetCycle = [84,200,133,200,200,200,44,49,200,18]
    barWidth = 0.3
    indexTarget = np.arange(len(number))        # 有目标的横坐标
    indexNoTarget = indexTarget + barWidth      # 无目标的横坐标

    # 画出柱状图
    plt.bar(indexTarget, height=targetCycle, width=barWidth, color="b", label="有目标")
    plt.bar(indexNoTarget, height=noTargetCycle, width=barWidth, color="r", label="无目标")

    for a,b in zip(indexTarget,targetCycle):
        plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)
    for a,b in zip(indexNoTarget,noTargetCycle):
        if b == 200:
            plt.text(a,b+0.05,"%d+"%b,ha="center",va="bottom",fontsize=15)
        else:
            plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)

    plt.legend(prop={"size":15})
    plt.xlabel("序号",fontsize=15)
    plt.xticks(indexTarget+barWidth/2,number,fontsize=15)
    plt.ylabel("循环次数（次）",fontsize=15)
    plt.yticks(fontsize=15)
    plt.title("有目标与无目标对比",fontsize=18)
    
    plt.show()

def timeHistogram():
    # 统计数据
    number = (1,2,3,4,5,6,7,8,9,10)
    targetCycle = [50,93,4,101,193,206,37,38,11,95]
    noTargetCycle = [195,400,302,400,400,400,108,108,400,62]
    barWidth = 0.3
    indexTarget = np.arange(len(number))        # 有目标的横坐标
    indexNoTarget = indexTarget + barWidth      # 无目标的横坐标

    # 画出柱状图
    plt.bar(indexTarget, height=targetCycle, width=barWidth, color="dodgerblue", label="有目标")
    plt.bar(indexNoTarget, height=noTargetCycle, width=barWidth, color="orangered", label="无目标")

    for a,b in zip(indexTarget,targetCycle):
        plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)
    for a,b in zip(indexNoTarget,noTargetCycle):
        if b == 400:
            plt.text(a,b+0.05,"%d+"%b,ha="center",va="bottom",fontsize=15)
        else:
            plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)

    plt.legend(prop={"size":15})
    plt.xlabel("序号",fontsize=15)
    plt.xticks(indexTarget+barWidth/2,number,fontsize=15)
    plt.ylabel("测试时间（秒）",fontsize=15)
    plt.yticks(fontsize=15)
    plt.title("有目标与无目标对比",fontsize=18)
    
    plt.show()

def multiTarCycleHistogram():
    # 统计数据
    number = (1,2,3,4,5,6,7,8,9,10)
    targetCycle = [13,28,17,10,12,25,2,60,23,6]
    noTargetCycle = [200,200,151,200,102,108,151,200,38,136]
    barWidth = 0.3
    indexTarget = np.arange(len(number))        # 有目标的横坐标
    indexNoTarget = indexTarget + barWidth      # 无目标的横坐标

    # 画出柱状图
    plt.bar(indexTarget, height=targetCycle, width=barWidth, color="b", label="有目标")
    plt.bar(indexNoTarget, height=noTargetCycle, width=barWidth, color="r", label="无目标")

    for a,b in zip(indexTarget,targetCycle):
        plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)
    for a,b in zip(indexNoTarget,noTargetCycle):
        if b == 200:
            plt.text(a,b+0.05,"%d+"%b,ha="center",va="bottom",fontsize=15)
        else:
            plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)

    plt.legend(prop={"size":15})
    plt.xlabel("序号",fontsize=15)
    plt.xticks(indexTarget+barWidth/2,number,fontsize=15)
    plt.ylabel("循环次数（次）",fontsize=15)
    plt.yticks(fontsize=15)
    plt.title("多目标情况下有目标与无目标对比",fontsize=18)
    
    plt.show()

def multiTarTimeHistogram():
    # 统计数据
    number = (1,2,3,4,5,6,7,8,9,10)
    targetCycle = [28,61,36,21,19,42,4,103,38,13]
    noTargetCycle = [400,400,312,400,221,216,344,400,85,313]
    barWidth = 0.3
    indexTarget = np.arange(len(number))        # 有目标的横坐标
    indexNoTarget = indexTarget + barWidth      # 无目标的横坐标

    # 画出柱状图
    plt.bar(indexTarget, height=targetCycle, width=barWidth, color="dodgerblue", label="有目标")
    plt.bar(indexNoTarget, height=noTargetCycle, width=barWidth, color="orangered", label="无目标")

    for a,b in zip(indexTarget,targetCycle):
        plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)
    for a,b in zip(indexNoTarget,noTargetCycle):
        if b == 400:
            plt.text(a,b+0.05,"%d+"%b,ha="center",va="bottom",fontsize=15)
        else:
            plt.text(a,b+0.05,"%d"%b,ha="center",va="bottom",fontsize=15)

    plt.legend(prop={"size":15})
    plt.xlabel("序号",fontsize=15)
    plt.xticks(indexTarget+barWidth/2,number,fontsize=15)
    plt.ylabel("测试时间（秒）",fontsize=15)
    plt.yticks(fontsize=15)
    plt.title("多目标情况下有目标与无目标对比",fontsize=18)
    
    plt.show()

if __name__ == "__main__":
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    multiTarCycleHistogram()
    multiTarTimeHistogram()