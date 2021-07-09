import ctypes
import nn
import random
import socket
import time
import os
import public
import re
import utils
import instrument as instr
import threading
from shutil import copyfile, rmtree
from subprocess import *

from fuzz import getFitness

HOST = '127.0.0.1'
PORT = 12012

num_index = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
loc = []
sign = []
seed_len = 0
round_cnt = 0
mut_cnt = 0
cover_node = {}
input_len = 0
old_edge_map = {}
program_loc = "D:\\fuzzer_new\\example\\main.exe"
# overall coverage achieved by now
program_cov = set()
# coverage achieved by current execution

fast = 1
stage_num = 1
cov_gain = 0

"""
def update_program_cov():
    global program_cov
    global cov_gain
    res = 0
    for edge in cur_cov.keys():
        if edge in program_cov.keys():
            if cur_cov[edge] > program_cov[edge]:
                program_cov[edge] = cur_cov[edge]
                if res != 2:
                    res = 1
        else:
            cov_gain += 1
            program_cov[edge] = cur_cov[edge]
            res = 2
    return res
"""


def calc_edge_gain(edge_map):
    cnt = 0
    for i in edge_map.values():
        cnt += i
    return cnt


def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]


def cal_cur_cov(edge_set):
    global cur_cov
    cur_cov = {}
    for edge in edge_set:
        if edge not in cur_cov.keys():
            cur_cov[edge] = 1
        else:
            cur_cov[edge] += 1


"""
def run_target(cmd, t=1):
    coverNode = []
    crash = False
    timeout = False
    global cur_cov
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    try:
        out = p.communicate(timeout=t)[0]
    except TimeoutExpired:
        p.kill()
        timeout = True
        out = b"timeout"
    p.kill()
    if p.returncode != 0:
        crash = True
    output = out.decode().split("\n")
    for j in range(0,len(output)):
        if "execute-" in output[j]:
            coverNode.append(get_str_btw(output[j],"execute-","\r"))
            #coverNode = sorted(set(coverNode), key=coverNode.index)
            cal_cur_cov(coverNode)
    return crash, timeout
"""


def write_to_testcase(fn, buf):
    with open(fn, "wb") as f:
        f.write(buf)


def fuzz(source_loc, ui, uiFuzz, fuzzThread):
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

    # now_loc = re.sub(source_loc[0].split("\\")[-1],"",source_loc[0])      # 当前所在目录
    now_loc = utils.ROOT
    output_loc = os.path.join(now_loc, "example")  # 输出exe和obj的位置
    program_loc = os.path.join(now_loc, "example", "instrument.exe")  # 可执行文件位置
    seed_loc = os.path.join(now_loc, "example", "in", "seed")  # 初始测试用例位置

    # 插装后的文件位置，因为是多文件，所以这里用了列表
    instrument_loc = []
    instr_var_loc = os.path.join(now_loc, "example", "in", "instrument.txt")
    # 因为要多文件编译，所以记录一下每个文件的位置，以便生成插装的源文件
    for source in source_loc:
        sourceName = source.split("\\")[-1]
        instrument_loc.append(re.sub(sourceName, "ins_" + sourceName, source))

    # 获取插装变量的名字
    # instrument_var = open(now_loc + "in\\instrument.txt").readline()
    instrument_var = open(instr_var_loc).readline()
    instrument_var = instrument_var.split(" ")[-1].split(":")[0].rstrip("\n")
    instr.instrument(source_loc, instrument_loc, output_loc, instrument_var)

    coverage = [0, 0]
    allCoveredNode = []  # 储存了所有被覆盖到的结点
    coverNode = []  # 储存了某个测试用例覆盖的节点
    callGraph = []
    testcase = []  # 存储测试用例
    TC_data = []  # 将测试用例、距离、适应度拼接成一个二维列表
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

    start = time.time()
    end = time.time()

    allNode = public.getAllFunctions(source_loc)
    allNode = sorted(set(allNode), key=allNode.index)
    utils.allNode = allNode
    print("allNode:", allNode)
    MAIdll = ctypes.cdll.LoadLibrary(os.path.join(now_loc, "example", "in", "mutate_instru.dll"))

    # 待修改
    testcase = open(seed_loc, "rb").read()

    # testcase[0] = [str(data) for data in testcase[0]]
    utils.mkdir(now_loc + "\\AIFuzz\\seeds")
    utils.mkdir(now_loc + "\\AIFuzz\\splice_seeds")
    utils.mkdir(now_loc + "\\AIFuzz\\mutations")
    utils.mkdir(now_loc + "\\AIFuzz\\crashes")
    utils.mkdir(now_loc + "\\AIFuzz\\bitmaps")
    # uiFuzz.text_browser_nn.append("测试文件夹准备完成...\n")
    utils.gen_training_data(os.path.join(utils.ROOT, "AIFuzz"), seed_loc, 10)
    # uiFuzz.text_browser_nn.append("已生成初始训练数据...\n")
    fuzzThread.nnInfoSgn.emit("模型训练信息：\n已经生成初始训练数据...\n")

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

    exec_thread = FuzzExecThread(ui, uiFuzz, fuzzThread, program_loc, MAIdll, allNode)
    nn_thread = nn.NN(ui, uiFuzz, fuzzThread, len(testcase), allNode, 10, program_loc, MAIdll)

    nn_thread.start()
    time.sleep(1)
    exec_thread.start()
    # Ready to start fuzz!
    while eval(condition):
        if uiFuzz.stop == True:
            break
        # 运行.exe文件并向其中输入，根据插桩的内容获取覆盖信息

    # 生成测试报告
    fuzzThread.fuzzInfoSgn.emit(fuzzInfo)
    fuzzInfoDict = {"测试时间": str(int(end - start)),
                    "测试对象": source_loc[0].split("\\")[-1],
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
    generateReport(source_loc[0], fuzzInfoDict)
    uiFuzz.textBrowser.append("\n已生成测试报告! 点击<查看结果>按钮以查看")

    print("\n", allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs" % (cycle, coverage[1], end - start))


class FuzzExec():
    def __init__(self, ui, ui_fuzz, fuzz_thread, program_loc, MAIdll, all_nodes, nn):
        self.ui = ui
        self.uiFuzz = ui_fuzz
        self.fuzzThread = fuzz_thread
        self.program_loc = program_loc
        self.MAIdll = MAIdll
        self.dir = os.path.abspath(os.path.join(utils.ROOT, "AIFuzz"))
        self.round_cnt = 0
        self.mut_cnt = 0
        self.mut_time = 0
        self.fast = 1
        self.stage = 1
        self.exec_cnt = 0
        self.exec_time = 0
        self.crash_cnt = 0
        self.cov_gain_cnt = 0
        self.all_nodes = set(all_nodes)
        self.program_cov = set()
        self.nn = nn

    def update_program_cov(self, cov):
        if cov.issubset(self.program_cov):
            return False
        else:
            self.program_loc = self.program_loc | cov
            return True

    def dry_run(self, dir, stage):
        files = os.listdir(dir)
        for f in files:
            fn = os.path.join(os.path.abspath(dir), f)
            # crash, timeout = run_target([program_loc, fn])
            tc = open(fn, "rb").read()
            _, cur_cov, crash, _ = utils.getCoverage(tc, self.program_loc, self.MAIdll)
            if crash:
                crash_fn = os.path.join(self.dir, "crashes", str(self.round_cnt) + "_" + str(self.crash_cnt))
                copyfile(fn, crash_fn)
                self.crash_cnt += 1
            ret = self.update_program_cov(cur_cov)
            if ret != 0 and stage == 1:
                cov_fn = os.path.join(self.dir, "seeds", "id_" + str(self.round_cnt) + "_" + str(self.cov_gain_cnt))
                copyfile(fn, cov_fn)
                self.cov_gain_cnt += 1

    def fuzz_loop(self, sock):
        self.dry_run(os.path.join(self.dir, "splice_seeds"), 1)
        dest = os.path.join(self.dir, "gradient_info")
        src = os.path.join(self.dir, "gradient_info_p")
        copyfile(src, dest)
        retrian = False
        n = len(self.program_cov)

        with open(dest, "r") as f:
            for line in f:
                loc, sign, fn = utils.parse_array(line)
                self.gen_mutate(loc, sign, fn)

        n1 = len(self.program_cov)

        self.round_cnt += 1
        utils.mkdir(os.path.join(self.dir, 'mutations', str(self.round_cnt)))
        if n1 - n >= 10 or self.fast == 0:
            sock.send(b"train")
            self.fast = 1
            print("fast stage\n")
        else:
            sock.send(b"sloww")
            self.fast = 0
            print("slow stage\n")

    def gen_mutate(self, loc, sign, seed_fn):
        flag = True
        out_buf = open(seed_fn, "rb").read()
        save_dir = os.path.join(self.dir, "mutations", str(self.round_cnt), seed_fn.split("\\")[-1])
        for iter in range(0, 3):
            out_buf1 = bytearray(out_buf)
            out_buf2 = bytearray(out_buf)
            low_index = num_index[iter]
            up_index = num_index[iter + 1]
            up_step = 0
            low_step = 0
            for index in range(low_index, up_index):
                if index >= len(sign):
                    break
                if sign[index] == 1:
                    cur_up_step = 255 - out_buf[loc[index]]
                    if cur_up_step > up_step:
                        up_step = cur_up_step
                    cur_low_step = out_buf[loc[index]]
                    if cur_low_step > low_step:
                        low_step = cur_low_step
                else:
                    cur_up_step = out_buf[loc[index]]
                    if cur_up_step > up_step:
                        up_step = cur_up_step
                    cur_low_step = 255 - out_buf[loc[index]]
                    if cur_low_step > low_step:
                        low_step = cur_low_step

            # print(iter, low_step, up_step)
            flag = True
            for step in range(0, up_step):
                for index in range(low_index, up_index):
                    if index >= len(sign):
                        flag = False
                        break
                    mut_val = int(out_buf1[loc[index]]) + sign[index]
                    if mut_val < 0:
                        out_buf1[loc[index]] = 0
                    elif mut_val > 255:
                        out_buf1[loc[index]] = 255
                    else:
                        out_buf1[loc[index]] = mut_val

                # fn = os.path.join(self.dir, 'mutations', str(self.round_cnt),
                #                  "input_{:d}_{:06d}".format(iter, self.mut_cnt))
                fn = os.path.join(save_dir, str(self.mut_cnt))
                write_to_testcase(fn, out_buf1)
                self.mut_cnt += 1
                if not flag:
                    break
                """
                crash, timeout = run_target([program_loc, fn])
                if crash:
                    mut_fn = "crashes/crash_{:d}_{:06d}".format(round_cnt, mut_cnt)
                    write_to_testcase(mut_fn, out_buf1)
                elif timeout and tmout_cnt < 20:
                    tmout_cnt = tmout_cnt + 1
                    crash, timeout = run_target([program_loc, fn], 2)
                    if crash:
                        mut_fn = "crashes/crash_{:d}_{:06d}".format(round_cnt, mut_cnt)
                        write_to_testcase(mut_fn, out_buf1)

                ret = update_program_cov()
                if ret == 2:
                    mut_fn = "seeds/id_{:d}_{:d}_{:06d}_cov".format(round_cnt, iter, mut_cnt)
                    write_to_testcase(mut_fn, out_buf1)
                elif ret == 1:
                    mut_fn = "seeds/id_{:d}_{:d}_{:06d}".format(round_cnt, iter, mut_cnt)
                    write_to_testcase(mut_fn, out_buf1)
                """

            flag = True
            for step in range(0, low_step):
                for index in range(low_index, up_index):
                    if index >= len(sign):
                        flag = False
                        break
                    mut_val = int(out_buf2[loc[index]]) - sign[index]
                    if mut_val < 0:
                        out_buf2[loc[index]] = 0
                    elif mut_val > 255:
                        out_buf2[loc[index]] = 255
                    else:
                        out_buf2[loc[index]] = mut_val

                # fn = os.path.join(self.dir, 'mutations', str(self.round_cnt),
                #                  "input_{:d}_{:06d}".format(iter, self.mut_cnt))
                fn = os.path.join(save_dir, str(self.mut_cnt))
                write_to_testcase(fn, out_buf2)
                self.mut_cnt += 1
                if not flag:
                    break
                """
                crash, timeout = run_target([program_loc, fn])
                if crash:
                    mut_fn = "crashes/crash_{:d}_{:06d}".format(round_cnt, mut_cnt)
                    write_to_testcase(mut_fn, out_buf2)
                elif timeout and tmout_cnt < 20:
                    tmout_cnt = tmout_cnt + 1
                    crash, timeout= run_target([program_loc, fn], 2)
                    if crash:
                        mut_fn = "crashes/crash_{:d}_{:06d}".format(round_cnt, mut_cnt)
                        write_to_testcase(mut_fn, out_buf2)

                ret = update_program_cov()
                if ret == 2:
                    mut_fn = "seeds/id_{:d}_{:d}_{:06d}_cov".format(round_cnt, iter, mut_cnt)
                    write_to_testcase(mut_fn, out_buf2)
                elif ret == 1:
                    mut_fn = "seeds/id_{:d}_{:d}_{:06d}".format(round_cnt, iter, mut_cnt)
                    write_to_testcase(mut_fn, out_buf2)
                """
            if not flag:
                break
        self.dry_run(save_dir, 1)

    def run(self):
        step = 0
        s = socket.socket()
        s.connect((HOST, PORT))
        seeds_dir = os.path.join(self.dir, "seeds")
        utils.mkdir(os.path.join(self.dir, "mutations", "0"))
        self.nn.gen_grad(b'train')
        while True:
            1==1
            """
            if not s.recvfrom(5):
                print("received failed\n")
            else:
                print("receive\n\n\n")
                if step == 0:
                    self.dry_run(seeds_dir, 2)
                    step = 1
                self.fuzz_loop(s)
            """



"""
def fuzz_loop(file, sock):
    global round_cnt
    global mut_cnt
    global fast
    global stage_num
    dry_run("./splice_seeds/", 1)
    copyfile("gradient_info_p", file)
    line_cnt = 0
    retrain_interval = 1000
    if round_cnt == 0:
        retrain_interval = 500
    with open(file, "r") as f:
        for line in f:
            line_cnt += 1
            if line_cnt == retrain_interval:
                round_cnt += 1
                #mut_cnt = 0
                os.mkdir('mutations/'+str(round_cnt))
                if fast == 0:
                    sock.send(b"train")
                    fast = 1
                    print("fast stage\n")
                else:
                    sock.send(b"sloww")
                    fast = 0
                    print("slow stage\n")
            #if line_cnt % 3 == 0:
            #    print(program_cov)
            loc, sign, fn = utils.parse_array(line)
            self.gen_mutate(loc, sign, fn)
    stage_num = fast


def start_fuzz():
    s = socket.socket()
    s.connect((HOST, PORT))
    dry_run("./seeds/", 2)
    while True:
        if not s.recvfrom(5):
            print("received failed\n")
        fuzz_loop("gradient_info", s)
        print("receive\n")


if __name__ == '__main__':

    #os.path.isdir("./crashes/") or os.makedirs("./crashes/")
    #os.path.isdir("./mutations/") or os.makedirs("./mutations/")
    #os.path.isdir("./mutations/0/") or os.makedirs("./mutations/0/")
    (not os.path.exists('gradient_info_p')) or os.remove('gradient_info_p')
    (not os.path.exists('gradient_info')) or os.remove('gradient_info')
    (not os.path.exists("hard_label.h5")) or os.remove("hard_label.h5")
    (not os.path.isdir('./crashes')) or rmtree('./crashes')
    (not os.path.isdir('./mutations')) or rmtree('./mutations')

    os.mkdir('./crashes/')
    os.mkdir('./mutations/')
    os.mkdir('./mutations/0/')

    start_fuzz()

"""
