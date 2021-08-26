import ctypes
import os
import re
import time
from shutil import copyfile, copy

import numpy as np

import instrument as instr
import nn
import public
import utils

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
program_cov = set()
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


def write_to_testcase(fn, buf, dll):
    fn = bytes(fn, encoding="utf8")
    dll["mutate"].mutate(buf, fn, 0xffffffff)
    # with open(fn, "wb") as f:
    #    f.write(buf)


def fuzz(header_loc_list, ui, uiPrepareFuzz, uiFuzz, fuzzThread):
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
    s = uiPrepareFuzz.senderIPLabel.text()
    r = uiPrepareFuzz.receiverIPLabel.text()
    allCoveredNode = []  # 储存了所有被覆盖到的结点

    allNode = uiPrepareFuzz.allNodes
    utils.allNode = allNode
    print("allNode:", allNode)


    # 待修改
    testcase = open(seed_loc, "rb").read()

    # testcase[0] = [str(data) for data in testcase[0]]
    seeds_dir = os.path.join(now_loc, "AIFuzz", "seeds")
    p2 = os.path.join(now_loc, "AIFuzz", "crossovers")
    p3 = os.path.join(now_loc, "AIFuzz", "mutations")
    p4 = os.path.join(now_loc, "AIFuzz", "bitmaps")
    p5 = os.path.join(now_loc, "AIFuzz", "crashes")
    utils.mkdir(seeds_dir, del_if_exist=False)
    utils.mkdir(p2)
    utils.mkdir(p3)
    utils.mkdir(p4)
    utils.mkdir(p5)
    # uiFuzz.text_browser_nn.append("测试文件夹准备完成...\n")
    if ui.AICfgDialog.randTS.isChecked():
        for f in [os.path.join(seeds_dir, path) for path in os.listdir(seeds_dir)]:
            os.remove(f)
        utils.gen_training_data(os.path.join(now_loc, "AIFuzz"), seed_loc, int(ui.AICfgDialog.randTSSize.text()),
                                dllDict)
        # uiFuzz.text_browser_nn.append("已生成初始训练数据...\n")
        fuzzThread.nnInfoSgn.emit("模型训练信息：\n已经生成初始训练数据，训练集规模：" + ui.AICfgDialog.randTSSize.text() + "\n")
    else:
        dir = ui.AICfgDialog.tsLoc.toPlainText()
        if dir != "":
            for f in [os.path.join(seeds_dir, path) for path in os.listdir(seeds_dir)]:
                os.remove(f)
            files = [os.path.join(dir, path) for path in os.listdir(dir)]
            files = [f for f in files if os.path.isfile(f)]
            print(files)
            for f in files:
                copy(f, seeds_dir)
            fuzzThread.nnInfoSgn.emit("模型训练信息：\n已经拷贝初始训练数据，训练集规模：" + str(len(files)) + '\n')

    # 设置终止条件
    condition = ""
    if ui.stopByCrash.isChecked():
        condition = "self.crash_cnt >= 1"
    elif ui.stopByTime.isChecked():
        fuzzTime = int(ui.fuzzTime.text())
        if ui.timeUnit.currentText() == "分钟":
            fuzzTime *= 60
        else:
            fuzzTime *= 3600
        condition = "time.time() - self.start > " + str(fuzzTime)
    else:
        stopNum = int(ui.stopByTCNum.text()) + 1
        condition = "self.mut_cnt > " + str(stopNum)

    condition += " or self.uiFuzz.stop"
    n = nn.NN(ui, uiFuzz, fuzzThread, len(testcase), allNode, int(ui.AICfgDialog.seedPerRound.text()), program_loc,
              dllDict, now_loc)
    e = FuzzExec(ui, uiFuzz, fuzzThread, program_loc, dllDict, allNode, n, condition,
                 ui.AICfgDialog.mutSize.currentText(), now_loc, s, r)
    n.setExec(e)
    start = time.time()
    e.run()
    end = time.time()
    """
    # Ready to start fuzz!
    while eval(condition):
        if uiFuzz.stop == True:
            break
        # 运行.exe文件并向其中输入，根据插桩的内容获取覆盖信息
"""
    # 生成测试报告
    fuzzThread.execInfoSgn.emit(e.genFuzzInfo() + "\n测试完成！")
    fuzzInfoDict = {"测试时间": str(int(end - start)),
                    "测试对象": now_loc,
                    "循环次数": str(e.round_cnt + 1),
                    "生成速度": 0 if e.mut_cnt == 0 else "{:.2f}".format(e.mut_cnt / e.mut_time),
                    "执行速度": 0 if e.exec_time == 0 else "{:.2f}".format(int(e.exec_cnt / e.exec_time)),
                    "已生成测试用例": str(e.mut_cnt),
                    "已触发缺陷次数": str(e.crash_cnt),
                    "已发现结点数量": str(len(allNode)),
                    "已覆盖结点": str(len(e.program_cov)),
                    "整体覆盖率": "{:.2f}".format(len(e.program_cov) / len(allNode))}
    with open(os.path.join(now_loc, 'AIFuzz', '测试报告.txt'), 'w', encoding='utf-8') as f:
        f.write(str(fuzzInfoDict))
    # generateReport(source_loc[0], fuzzInfoDict)
    uiFuzz.text_browser_exec.append("\n已生成测试报告! 点击<查看结果>按钮以查看")

    print("\n", allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs" % (
        e.round_cnt + 1, len(e.program_cov) / len(allNode), end - start))


class FuzzExec():
    def __init__(self, ui, ui_fuzz, fuzz_thread, program_loc, MAIdll, all_nodes, nn, cond, mut_size, root_loc,s, r):
        self.ui = ui
        self.uiFuzz = ui_fuzz
        self.fuzzThread = fuzz_thread
        self.program_loc = program_loc
        self.MAIdll = MAIdll
        self.dir = os.path.join(root_loc, "AIFuzz")
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
        self.cond = cond
        self.start = time.time()
        self.stop = False
        self.mut_size = mut_size
        self.cov_map = {}
        self.s = s
        self.r = r

    def genFuzzInfo(self):
        info = "轮次：\t\t\t" + str(self.round_cnt + 1) + "\n"
        info += "覆盖节点数：\t\t\t" + str(len(self.program_cov)) + "\n"
        info += "覆盖率：\t\t\t" + "{:.2f}".format(len(self.program_cov) / len(self.all_nodes)) + "\n"
        info += "生成测试用例数：\t\t" + str(self.mut_cnt) + "\n"
        info += "生成测试用例速度\t\t" + (
            "0" if self.mut_time == 0 else "{:.2f}".format(self.mut_cnt / self.mut_time)) + "个/秒\n"
        info += "执行测试用例数：\t\t" + str(self.exec_cnt) + "\n"
        info += "执行测试用例速度\t\t" + (
            "0" if self.exec_time == 0 else "{:.2f}".format(self.exec_cnt / self.exec_time)) + "个/秒\n"
        info += "崩溃次数：\t\t\t" + str(self.crash_cnt) + "\n"
        return info

    def update_program_cov(self, cov):
        cov = set(cov)
        if cov == self.program_cov:
            return 1
        elif cov.issubset(self.program_cov):
            return 0
        else:
            self.program_cov = self.program_cov | cov
            return 2

    def run_testcases(self, dir, stage):
        files = os.listdir(dir)
        start = time.time()
        time_ckpt = start
        for i, f in enumerate(files):
            fn = os.path.join(os.path.abspath(dir), f)
            # crash, timeout = run_target([program_loc, fn])
            print(fn)
            tc = open(fn, "rb").read()
            # self.MAIdll.setValueInRange(tc)
            cur_cov = None
            crash = None
            if stage == 2:
                if fn in self.cov_map.keys():
                    cur_cov, crash = self.cov_map[fn]
                else:
                    _, cur_cov, crash, _ = utils.getCoverage(tc, self.s, self.r, 1, self.MAIdll)
                    self.cov_map[fn] = cur_cov, crash
            else:
                _, cur_cov, crash, _ = utils.getCoverage(tc, self.s, self.r, 1, self.MAIdll)
            if crash:
                crash_fn = os.path.join(self.dir, "crashes", str(self.round_cnt) + "_" + str(self.crash_cnt))
                copyfile(fn, crash_fn)
                self.crash_cnt += 1
            ret = self.update_program_cov(cur_cov)
            if ret != 0 and stage == 1:
                cov_fn = os.path.join(self.dir, "seeds", "id_" + str(self.round_cnt) + "_" + str(self.cov_gain_cnt))
                copyfile(fn, cov_fn)
                self.cov_gain_cnt += 1
            if stage == 1:
                self.exec_cnt += 1
                self.exec_time += (time.time() - time_ckpt)
            if stage != 2:
                time_ckpt = time.time()
                info = self.genFuzzInfo()
                info += "\n正在执行测试用例：\n" + fn + "\n"
                info += "执行速度：" + (
                    "-" if time.time() - start < 1e-4 else "{:.2f}".format((i + 1) / (time.time() - start))) + "个/秒\n"
                self.fuzzThread.execInfoSgn.emit(info)
            else:
                self.fuzzThread.nnInfoSgn.emit("正在执行训练数据：" + fn + "\n")
            if eval(self.cond):
                self.stop = True
                return

    def fuzz_loop(self):
        self.run_testcases(os.path.join(self.dir, "crossovers"), 1)
        dest = os.path.join(self.dir, "gradient_info")
        src = os.path.join(self.dir, "gradient_info_p")
        copyfile(src, dest)
        retrian = False
        n = len(self.program_cov)

        with open(dest, "r") as f:
            for line in f:
                loc, sign, fn = utils.parse_array(line)
                self.gen_mutate(loc, sign, fn)
                if self.stop:
                    return

        n1 = len(self.program_cov)

    def gen_mutate(self, loc, sign, seed_fn):
        if self.mut_size == "小":
            N = 10
        elif self.mut_size == "中":
            N = 30
        else:
            N = 255
        out_buf = open(seed_fn, "rb").read()
        save_dir = os.path.join(self.dir, "mutations", str(self.round_cnt), seed_fn.split("\\")[-1])
        utils.mkdir(save_dir)
        start = time.time()
        cnt = 0
        time_ckpt = start
        for iter in range(0, 10):
            out_buf1 = bytearray(out_buf)
            out_buf2 = bytearray(out_buf)
            low_index = num_index[iter]
            up_index = num_index[iter + 1]
            if low_index >= len(sign):
                up_index = low_index - 1
            elif up_index >= len(sign):
                up_index = len(sign)
            up_step = 0
            low_step = 0
            for index in range(low_index, up_index):
                if self.uiFuzz.stop:
                    self.stop = True
                    return
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
            N = N if N <= up_step else up_step
            up_step = [] if up_step == 0 else np.random.choice(up_step, N, replace=False)
            N = N if N <= low_step else low_step
            low_step = [] if low_step == 0 else np.random.choice(low_step, N, replace=False)

            # for step in range(0, up_step):
            for step in up_step:
                if self.uiFuzz.stop:
                    self.stop = True
                    return
                if step == 0:
                    continue
                for index in range(low_index, up_index):
                    mut_val = int(out_buf1[loc[index]]) + sign[index] * step
                    if mut_val < 0:
                        out_buf1[loc[index]] = 0
                    elif mut_val > 255:
                        out_buf1[loc[index]] = 255
                    else:
                        out_buf1[loc[index]] = mut_val

                # fn = os.path.join(self.dir, 'mutations', str(self.round_cnt),
                #                  "input_{:d}_{:06d}".format(iter, self.mut_cnt))
                fn = save_dir + "\\" + str(self.mut_cnt)
                tmp = bytes(out_buf1)
                # self.MAIdll.setValueInRange(tmp)
                write_to_testcase(fn, tmp, self.MAIdll)
                self.mut_cnt += 1
                self.mut_time += (time.time() - time_ckpt)
                time_ckpt = time.time()
                cnt += 1
                info = self.genFuzzInfo()
                info += "\n正在变异种子文件：\n" + seed_fn + "\n"
                info += "变异速度：" + (
                    "-" if time.time() - start < 1e-4 else "{:.2f}".format(cnt / (time.time() - start))) + "个/秒\n"
                self.fuzzThread.execInfoSgn.emit(info)

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

            # for step in range(0, low_step):
            for step in low_step:
                if self.uiFuzz.stop:
                    self.stop = True
                    return
                if step == 0:
                    continue
                for index in range(low_index, up_index):
                    mut_val = int(out_buf2[loc[index]]) - sign[index] * step
                    if mut_val < 0:
                        out_buf2[loc[index]] = 0
                    elif mut_val > 255:
                        out_buf2[loc[index]] = 255
                    else:
                        out_buf2[loc[index]] = mut_val

                # fn = os.path.join(self.dir, 'mutations', str(self.round_cnt),
                #                  "input_{:d}_{:06d}".format(iter, self.mut_cnt))
                fn = save_dir + "\\" + str(self.mut_cnt)
                tmp = bytes(out_buf2)
                # self.MAIdll.setValueInRange(tmp)
                write_to_testcase(fn, tmp, self.MAIdll)
                self.mut_cnt += 1
                self.mut_time += (time.time() - time_ckpt)
                time_ckpt = time.time()
                cnt += 1
                info = self.genFuzzInfo()
                info += "\n正在变异种子文件：\n" + seed_fn + "\n"
                info += "变异速度：" + (
                    "-" if time.time() - start < 1e-4 else "{:.2f}".format(cnt / (time.time() - start))) + "个/秒\n"
                self.fuzzThread.execInfoSgn.emit(info)

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

        self.run_testcases(save_dir, 1)

    def run(self):
        step = 0
        # s = socket.socket()
        # s.connect((HOST, PORT))
        self.start = time.time()
        seeds_dir = os.path.join(self.dir, "seeds")
        utils.mkdir(os.path.join(self.dir, "mutations", "0"))
        self.run_testcases(seeds_dir, 2)
        self.nn.gen_grad(b'train')
        while True:
            old_cov = self.program_cov
            self.fuzz_loop()
            if self.stop:
                return
            new_cov = self.program_cov
            self.round_cnt += 1
            utils.mkdir(os.path.join(self.dir, 'mutations', str(self.round_cnt)))
            if len(new_cov) > len(old_cov) or self.fast == 0:
                self.nn.gen_grad(b"train")
                self.fast = 1
            else:
                self.nn.gen_grad(b"sloww")
                self.fast = 0


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
