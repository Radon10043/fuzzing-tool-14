import socket
import os
from shutil import copyfile, rmtree
from subprocess import *
HOST = '127.0.0.1'
PORT = 12012
cur_dir = os.path.abspath(os.path.curdir)
num_index = [0,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192]
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
program_cov = {}
# coverage achieved by current execution
cur_cov = {}
fast = 1
stage_num = 1
cov_gain = 0


def parse_array(text):
    # loc|sign|filename
    loc_sign_fn = text.strip().split("|")
    loc = [int(i) for i in loc_sign_fn[0].split(',')]
    sign = [int(i) for i in loc_sign_fn[1].split(',')]
    fn = loc_sign_fn[2]
    return loc, sign, fn


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


def write_to_testcase(fn, buf):
    with open(fn, "wb") as f:
        f.write(buf)


def gen_mutate(loc, sign, seed_fn):
    tmout_cnt = 0
    global mut_cnt
    global round_cnt
    flag = True
    out_buf = open(seed_fn, "rb").read()
    for iter in range(0, 13):
        out_buf1 = bytearray(out_buf)
        out_buf2 = bytearray(out_buf)
        low_index = num_index[iter]
        up_index = num_index[iter+1]
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

        #print(iter, low_step, up_step)
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

            fn = os.path.join(cur_dir, 'mutations', str(round_cnt),
                              "input_{:d}_{:06d}".format(iter, mut_cnt))
            write_to_testcase(fn, out_buf1)
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

            mut_cnt += 1

        for step in range(0, low_step):
            for index in range(low_index, up_index):
                if index >= len(sign):
                    flag = False
                    break
                mut_val = int(out_buf2[loc[index]])- sign[index]
                if mut_val < 0:
                    out_buf2[loc[index]] = 0
                elif mut_val > 255:
                    out_buf2[loc[index]] = 255
                else:
                    out_buf2[loc[index]] = mut_val

            fn = os.path.join(cur_dir, 'mutations', str(round_cnt),
                              "input_{:d}_{:06d}".format(iter, mut_cnt))
            write_to_testcase(fn, out_buf2)
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

            mut_cnt += 1
            if not flag:
                return


def dry_run(dir, stage):
    global mut_cnt
    files = os.listdir(dir)
    for f in files:
        fn = os.path.join(os.path.abspath(dir), f)
        crash, timeout = run_target([program_loc, fn])
        if crash or timeout:
            print(fn)
            mut_fn = "crashes/crash_{:d}_{:06d}".format(round_cnt, mut_cnt)
            copyfile(fn, mut_fn)
            mut_cnt += 1
        ret = update_program_cov()
        if ret != 0 and stage == 1:
            mut_fn = "seeds/id_{:d}_{:06d}".format(round_cnt,  mut_cnt)
            copyfile(fn, mut_fn)
            mut_cnt += 1


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
            #print(line_cnt)
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
            loc, sign, fn = parse_array(line)
            gen_mutate(loc, sign, fn)
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
