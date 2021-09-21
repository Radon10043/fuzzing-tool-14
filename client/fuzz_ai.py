import ctypes
import json
import os
import re
import random
import time
import glob
from shutil import copyfile, copy
import numpy as np

import nn
import numpy as np
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
    # dll['instrument'].setInstrValueToZero(buf)
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

    input_json_loc = now_loc + "in/input.json"

    # 加载所需的DLL文件，并将CDLL存入一个字典，以便调用
    mutateDll = ctypes.cdll.LoadLibrary(now_loc + "in/mutate.dll")
    instrumentDll = ctypes.cdll.LoadLibrary(now_loc + "in/insFunc.dll")
    dllDict = {"mutate": mutateDll, "instrument": instrumentDll}

    # 设置地址
    s = uiPrepareFuzz.senderIPLabel.text()
    r = uiPrepareFuzz.receiverIPLabel.text()
    s = "127.0.0.1:9999"
    r = "127.0.0.1:8888"

    allCoveredNode = []  # 储存了所有被覆盖到的结点

    allNode = uiPrepareFuzz.allNodes
    utils.allNode = allNode
    print("allNode:", allNode)

    with open(input_json_loc, "r") as fp:
        structDict = json.load(fp)
    in_struct = {}
    for key in structDict.keys():
        struct = key
    for key, value in structDict[struct].items():
        dataName = key.split(" ")[-1].split(":")[0]
        dataType = key.replace(dataName, "").strip()
        in_struct[dataName] = value
        if dataType == "bool":
            in_struct[dataName]["enum"] = [0, 1]
        else:
            in_struct[dataName]["enum"] = []
    # 待修改
    # testcase = open(seed_loc, "rb").read()

    # testcase[0] = [str(data) for data in testcase[0]]

    dirs = [os.path.join(now_loc, "ProtocolFuzz", "input_json", "seeds"),
            os.path.join(now_loc, "ProtocolFuzz", "input_json", "crossovers"),
            os.path.join(now_loc, "ProtocolFuzz", "input_json", "mutations"),
            os.path.join(now_loc, "ProtocolFuzz", "input_json", "bitmaps"),
            os.path.join(now_loc, "ProtocolFuzz", "input_json", "crashes"),
            os.path.join(now_loc, "ProtocolFuzz", "input_bin", "seeds"),
            os.path.join(now_loc, "ProtocolFuzz", "input_bin", "crossovers"),
            os.path.join(now_loc, "ProtocolFuzz", "input_bin", "mutations"),
            os.path.join(now_loc, "ProtocolFuzz", "input_bin", "crashes")]
    for d in dirs:
        utils.mkdir(d)

    # uiFuzz.text_browser_nn.append("测试文件夹准备完成...\n")
    if not ui.ProtocolFuzzCfgDialog.aiEnableCheckBox.isChecked():
        utils.gen_training_data(os.path.join(now_loc, "ProtocolFuzz", "input_json", "seeds"),
                                in_struct, int(ui.ProtocolFuzzCfgDialog.seedPerRound.text()))
        fuzzThread.nnInfoSgn.emit("无模型训练信息：\n采用随机测试用例生成策略\n")
    elif ui.ProtocolFuzzCfgDialog.randTS.isChecked():
        utils.gen_training_data(os.path.join(now_loc, "ProtocolFuzz", "input_json", "seeds"),
                                in_struct, int(ui.ProtocolFuzzCfgDialog.randTSSize.text()))
        # uiFuzz.text_browser_nn.append("已生成初始训练数据...\n")
        fuzzThread.nnInfoSgn.emit("模型训练信息：\n已经生成初始训练数据，训练集规模：" + ui.ProtocolFuzzCfgDialog.randTSSize.text() + "\n")

    else:
        dir = ui.ProtocolFuzzCfgDialog.tsLoc.toPlainText()
        files = [os.path.join(dir, path) for path in os.listdir(dir)]
        files = [f for f in files if os.path.isfile(f)]
        i = 0
        for f in files:
            dst = os.path.join(dirs[0], str(i)+".json")
            i += 1
            dllDict['mutate'].bytes2json(open(f,'rb').read(), bytes(dst, encoding='utf8'))
        fuzzThread.nnInfoSgn.emit("模型训练信息：\n已经拷贝初始训练数据，训练集规模：" + str(len(files)) + '\n')


    # 设置终止条件
    condition = ""
    if ui.stopByCrash.isChecked():
        condition = "self.crash_cnt > 0"
    elif ui.stopByTime.isChecked():
        fuzzTime = int(ui.fuzzTime.text())
        if ui.timeUnit.currentText() == "分钟":
            fuzzTime *= 60
        else:
            fuzzTime *= 3600
        condition = "time.time() - self.start > " + str(fuzzTime)
    else:
        stopNum = int(ui.TCNumsLineEdit.text())
        condition = "self.exec_cnt >= " + str(stopNum)

    condition += " or self.uiFuzz.stop"
    n = nn.NN(ui, uiFuzz, fuzzThread, in_struct, allNode, program_loc, dllDict, now_loc)
    e = FuzzExec(ui, uiFuzz, fuzzThread, program_loc, dllDict, allNode, n, condition, now_loc, s, r, in_struct)
    n.setExec(e)
    start = time.time()
    e.run()
    end = time.time()
    """
    # Ready to start fuzz!
    while eval(condition):
        if uiFuzz.stop == True:
            break
        # 运行.exe文件并向其中输入，根据插装的内容获取覆盖信息
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

    with open(os.path.join(now_loc, 'ProtocolFuzz', '测试报告.txt'), 'w', encoding='utf-8') as f:
        f.write("测试时间：\t" + str(int(end - start)) + "秒\n")
        f.write("测试对象: \t\t" + now_loc + "\n")
        f.write("循环次数: \t\t" + str(e.round_cnt + 1) + "\n")
        f.write("测试用例生成速度: \t" + ("0" if e.mut_cnt == 0 else "{:.2f}".format(e.mut_cnt / e.mut_time) + "个/秒\n"))
        f.write("测试用例执行速度: \t" + ("0" if e.exec_time == 0 else "{:.2f}".format(int(e.exec_cnt / e.exec_time)) + "个/秒\n"))
        f.write("已生成测试用例数: \t" + str(e.mut_cnt) + "\n")
        f.write("已执行测试用例数: \t" + str(e.exec_cnt) + "\n")
        f.write("已触发缺陷次数: \t" + str(e.crash_cnt) + "\n")
        f.write("已发现结点数: \t" + str(len(allNode)) + "\n")
        f.write("已覆盖结点数: \t" + str(len(e.program_cov)) + "\n")
        f.write("整体覆盖率: \t" + "{:.2f}".format(len(e.program_cov) / len(allNode)) + "\n")
        f.write("\n\n==========节点覆盖数分布==========\n")
        f.write("覆盖节点数\t测试用例数\n")
        for i in sorted(e.total_cov_map):
            f.write(str(i) + "\t\t" + str(e.total_cov_map[i]) + "\n")

    # generateReport(source_loc[0], fuzzInfoDict)
    uiFuzz.text_browser_exec.append("\n已生成测试报告! 点击<查看结果>按钮以查看")

    print("\n", allCoveredNode)
    print("\nfuzz over! cycle = %d, coverage = %.2f, time = %.2fs" % (
        e.round_cnt + 1, len(e.program_cov) / len(allNode), end - start))


class FuzzExec():
    def __init__(self, ui, ui_fuzz, fuzz_thread, program_loc, MAIdll, all_nodes, nn, cond, root_loc, s, r,
                 struct):
        self.ui = ui
        self.uiFuzz = ui_fuzz
        self.fuzzThread = fuzz_thread
        self.program_loc = program_loc
        self.MAIdll = MAIdll
        self.dir = os.path.join(root_loc, "ProtocolFuzz")
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

        if ui.ProtocolFuzzCfgDialog.mutSize.currentText() == "小":
            self.mut_size = 50
        elif ui.ProtocolFuzzCfgDialog.mutSize.currentText() == "中":
            self.mut_size = 100
        else:
            self.mut_size = 200

        self.seed_cov_map = {}
        self.total_cov_map = {}
        self.node_cnt = {}
        for node in all_nodes:
            self.node_cnt[node] = 0
        self.s = s
        self.r = r
        self.struct = struct
        self.idx_name = []
        self.name_idx = {}
        for key, value in struct.items():
            if value["mutation"]:
                self.idx_name.append(key)
                self.name_idx[key] = len(self.idx_name) - 1

    def genFuzzInfo(self):
        info = "轮次：\t\t\t" + str(self.round_cnt + 1) + "\n"
        info += "覆盖节点数：\t\t\t" + str(len(self.program_cov)) + "\n"
        info += "覆盖率：\t\t\t" + "{:.2f}".format(len(self.program_cov) / len(self.all_nodes)) + "\n"
        info += "生成测试用例数：\t\t" + str(self.mut_cnt) + "\n"
        info += "生成测试用例速度：\t\t" + (
            "0" if self.mut_time == 0 else "{:.2f}".format(self.mut_cnt / self.mut_time)) + "个/秒\n"
        info += "执行测试用例数：\t\t" + str(self.exec_cnt) + "\n"
        info += "执行测试用例速度：\t\t" + (
            "0" if self.exec_time == 0 else "{:.2f}".format(self.exec_cnt / self.exec_time)) + "个/秒\n"
        info += "崩溃次数：\t\t\t" + str(self.crash_cnt) + "\n"
        return info

    def update_program_cov(self, cov):
        """
        cov = set(cov)
        cnt = (0 if len(cov) not in self.total_cov_map.keys() else self.total_cov_map[len(cov)])
        avg = (0 if len(self.total_cov_map.keys()) == 0 else self.exec_cnt / len(self.total_cov_map.keys()))
        flag = avg == 0 or cnt < avg
        self.program_cov = self.program_cov | cov
        if flag:
            return True
        return False

        """
        cov = set(cov)
        for c in cov:
            self.node_cnt[c] += 1
            if self.node_cnt[c] < self.exec_cnt / len(self.all_nodes):
                return 2

        if cov == self.program_cov:
            return 1
        elif cov.issubset(self.program_cov):
            return 0
        else:
            self.program_cov = self.program_cov | cov
            return 2

    # stage = 1: Normal fuzzing process
    # stage = 2: Running training input
    def run_testcases(self, dir, stage):
        files = os.listdir(dir)
        start = time.time()
        time_ckpt = start
        for i, f in enumerate(files):
            fn_json = os.path.join(os.path.abspath(dir), f)
            tmp_fn_bin = os.path.join(self.dir, "tmp")
            _, cur_cov, crash, data = utils.getCoverage(fn_json, tmp_fn_bin, self.s, self.r, 1, self.MAIdll)
            if stage != 2:
                if len(set(cur_cov)) in self.total_cov_map.keys():
                    self.total_cov_map[len(set(cur_cov))] += 1
                else:
                    self.total_cov_map[len(set(cur_cov))] = 1
                copyfile(tmp_fn_bin, fn_json.replace("input_json", "input_bin").replace(".json", ""))
            if crash:
                crash_fn_json = os.path.join(self.dir, "input_json", "crashes",
                                             str(self.round_cnt))
                crash_fn_bin = os.path.join(self.dir, "input_bin", "crashes",
                                             str(self.round_cnt) + "_" + str(self.crash_cnt))
                open(crash_fn_bin, "wb").write(data)
                self.MAIdll['mutate'].testcaseVisualization(data, bytes(crash_fn_json+".txt", encoding='utf8'))
                self.crash_cnt += 1
            ret = self.update_program_cov(cur_cov)
            if ret == 2 and stage == 1:
                cov_fn_json = os.path.join(self.dir, "input_json", "seeds",
                                           "id_" + str(self.round_cnt) + "_" + str(self.cov_gain_cnt)+".json")
                cov_fn_bin = os.path.join(self.dir, "input_bin", "seeds",
                                          "id_" + str(self.round_cnt) + "_" + str(self.cov_gain_cnt))
                self.seed_cov_map[cov_fn_json] = cur_cov, crash
                copyfile(fn_json, cov_fn_json)
                copyfile(tmp_fn_bin, cov_fn_bin)
                self.cov_gain_cnt += 1
            if stage == 1:
                self.exec_cnt += 1
                self.exec_time += (time.time() - time_ckpt)
            if stage != 2:
                time_ckpt = time.time()
                info = self.genFuzzInfo()
                info += "\n正在执行测试用例：\n" + fn_json + "\n"
                info += "执行速度：" + (
                    "-" if time.time() - start < 1e-4 else "{:.2f}".format((i + 1) / (time.time() - start))) + "个/秒\n"
                self.fuzzThread.execInfoSgn.emit(info)
            # else:
            #     self.fuzzThread.nnInfoSgn.emit("正在执行训练数据：" + fn + "\n")
            if eval(self.cond):
                self.stop = True
                return

    def fuzz_loop(self):
        self.run_testcases(os.path.join(self.dir, "input_json", "crossovers"), 1)
        dest = os.path.join(self.dir, "gradient_info")
        src = os.path.join(self.dir, "gradient_info_p")
        copyfile(src, dest)
        with open(dest, "r") as f:
            for line in f:
                loc, sign, fn = utils.parse_array(line)
                self.gen_mutate(loc, sign, fn)
                if self.stop:
                    return

    def gen_mutate(self, loc, sign, seed_fn):
        N = self.mut_size
        L = int(len(loc)/2)

        with open(seed_fn, "r") as fp:
            seed = json.load(fp)

        save_dir1 = os.path.join(self.dir, "input_json", "mutations", str(self.round_cnt),
                                 seed_fn.split("\\")[-1].split(".")[0])
        save_dir2 = os.path.join(self.dir, "input_bin", "mutations", str(self.round_cnt),
                                 seed_fn.split("\\")[-1].split(".")[0])
        utils.mkdir(save_dir1)
        utils.mkdir(save_dir2)
        start = time.time()
        cnt = 0
        time_ckpt = start

        """
                for num in range(N):
                    if eval(self.cond):
                        self.stop = True
                        return
                    for i, idx in enumerate(loc):
                        name = self.idx_name[idx]
                        enum = len(self.struct[name]["enum"])
                        if enum == 0:
                            upper = float(self.struct[name]["upper"])
                            lower = float(self.struct[name]["lower"])
                            seed[name] = random.uniform(lower, upper)
                        else:
                            seed[name] = self.struct[name]["enum"][random.randint(0, enum-1)]

                    fn = save_dir1 + "\\" + str(self.mut_cnt) + ".json"
                    with open(fn, "w") as fp:
                        json.dump(seed, fp)
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

        seed_up = seed
        loc_up = loc
        sign_up = sign
        seed_down = seed
        loc_down = loc
        sign_down = sign
        for step in range(1, self.mut_size):
            if eval(self.cond):
                self.stop = True
                return
            for i, idx in enumerate(loc):
                name = self.idx_name[idx]
                enum = len(self.struct[name]["enum"])
                if enum == 0:
                    upper = float(self.struct[name]["upper"])
                    lower = float(self.struct[name]["lower"])
                    if lower <= seed_up[name] + sign[i] <= upper:
                        seed_up[name] = float(seed_up[name] + sign[i])
                else:
                    seed_up[name] = self.struct[name]["enum"][random.randint(0, enum - 1)]

            fn = save_dir1 + "\\" + str(self.mut_cnt) + ".json"
            with open(fn, "w") as fp:
                json.dump(seed_up, fp)
            self.mut_cnt += 1
            self.mut_time += (time.time() - time_ckpt)
            time_ckpt = time.time()
            cnt += 1
            info = self.genFuzzInfo()
            info += "\n正在变异种子文件：\n" + seed_fn + "\n"
            info += "变异速度：" + (
                "-" if time.time() - start < 1e-4 else "{:.2f}".format(cnt / (time.time() - start))) + "个/秒\n"
            self.fuzzThread.execInfoSgn.emit(info)


        for step in range(1, self.mut_size):
            if eval(self.cond):
                self.stop = True
                return
            for i, idx in enumerate(loc):
                name = self.idx_name[idx]
                enum = len(self.struct[name]["enum"])
                if enum == 0:
                    upper = float(self.struct[name]["upper"])
                    lower = float(self.struct[name]["lower"])
                    if lower <= seed_down[name] - sign[i] <= upper:
                        seed_down[name] = float(seed_down[name] - sign[i])
                else:
                    seed_down[name] = self.struct[name]["enum"][random.randint(0, enum - 1)]

            fn = save_dir1 + "\\" + str(self.mut_cnt) + ".json"
            with open(fn, "w") as fp:
                json.dump(seed_down, fp)
            self.mut_cnt += 1
            self.mut_time += (time.time() - time_ckpt)
            time_ckpt = time.time()
            cnt += 1
            info = self.genFuzzInfo()
            info += "\n正在变异种子文件：\n" + seed_fn + "\n"
            info += "变异速度：" + (
                "-" if time.time() - start < 1e-4 else "{:.2f}".format(cnt / (time.time() - start))) + "个/秒\n"
            self.fuzzThread.execInfoSgn.emit(info)

        self.run_testcases(save_dir1, 1)

    def run(self):
        if self.ui.ProtocolFuzzCfgDialog.aiEnableCheckBox.isChecked():
            self.ai_fuzz()
        else:
            self.random_fuzz()

    def ai_fuzz(self):
        self.start = time.time()
        seeds_dir = os.path.join(self.dir, "input_json", "seeds")
        utils.mkdir(os.path.join(self.dir, "input_json", "mutations", "0"))
        self.run_testcases(seeds_dir, 2)
        self.nn.gen_grad(b'train')
        while True:
            self.fuzz_loop()
            if self.stop:
                return
            self.round_cnt += 1
            utils.mkdir(os.path.join(self.dir, "input_json", 'mutations', str(self.round_cnt)))
            utils.mkdir(os.path.join(self.dir, "input_bin", 'mutations', str(self.round_cnt)))
            self.nn.gen_grad(b'train')



    def random_fuzz(self):
        self.start = time.time()
        seeds_dir = os.path.join(self.dir, "input_json", "seeds")
        utils.mkdir(os.path.join(self.dir, "input_json", "mutations", "0"))
        self.run_testcases(seeds_dir, 1)
        while True:
            n = int(self.ui.ProtocolFuzzCfgDialog.seedPerRound.text())
            seeds = [os.path.join(seeds_dir, i) for i in glob.glob(os.path.join(seeds_dir, "*"))]
            seeds = np.random.choice(seeds, n, replace=False)
            for seed in seeds:
                loc = list(self.name_idx.values())
                sign = list(np.random.choice([1,-1], len(loc)))
                self.gen_mutate(loc, sign, seed)
                if self.stop:
                    return
            self.round_cnt += 1
            utils.mkdir(os.path.join(self.dir, "input_json", 'mutations', str(self.round_cnt)))
            utils.mkdir(os.path.join(self.dir, "input_bin", 'mutations', str(self.round_cnt)))

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

6		1105
7		439
8		424
9		32


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
