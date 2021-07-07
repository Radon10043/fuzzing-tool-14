import random
import numpy as np
import pickle
from subprocess import *
from sklearn import model_selection
from sklearn import neural_network
import os
import ctypes
MAX_INPUT_SIZE = 20


TC1 = bytearray([204,204,204,204,204,204,204,204,204,2,1,3,1,4,1,1,204,204,204,204,0,0,204,204,204,204,204,204,204,204,204,204,1,1,204,204,204,204,204,204,204,204,204,204,2,3,204,204,204,204,204,204,204,204,204,204,204,204,1,204,204,0,1,0,1,2,2,1])
TC2 = bytearray([204,204,204,204,204,204,204,204,204,1,5,4,3,1,2,10,204,204,204,204,0,0,204,204,204,204,204,204,204,204,204,204,1,1,204,204,204,204,204,204,204,204,204,204,3,2,204,204,204,204,204,204,204,204,204,204,204,204,1,204,204,0,1,1,3,2,4,0])


def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]


def prepare_data(data):
    res = bytearray(data)
    if len(data) < MAX_INPUT_SIZE:
        res += (MAX_INPUT_SIZE - len(data)) * b'\x00'
    return np.array(res).reshape(1, -1)


def getCoverage(testcase,program_loc,maxTimeout):
    coverNode = []
    p=Popen([program_loc],stdout=PIPE,stdin=PIPE,stderr=STDOUT)
    try:
        out = p.communicate(timeout=maxTimeout)[0]
    except TimeoutExpired:
        p.kill()
        out = b"timeout"
    p.kill()
    output = out.decode().split("\n")
    for j in range(0,len(output)):
        if "execute-" in output[j]:
            coverNode.append(get_str_btw(output[j],"execute-","\r"))
            coverNode = sorted(set(coverNode),key=coverNode.index)
    return len(coverNode)


def mutate(a, add=True, delete=True):
    res = bytearray()
    for i in range(0, len(a)):
        if a[i] == 204:
            res.append(a[i])
            continue
        prob = random.random()
        number = random.randint(0, 255)
        step = random.randint(1,2)
        if prob <= 0.1 and delete:
            continue
        elif prob <= 0.2 and add:
            res.append(number)
            i-=1
        elif prob <= 0.4:
            #down
            if a[i] < step:
                res.append(a[i])
                continue
            res.append(a[i]-step)
        elif prob <= 0.6:
            #up
            res.append(a[i]+step)
        else:
            res.append(a[i])
    return res


def get_coverage(testcase, cmd):
    coverNode = []
    print(cmd)
    p=Popen(cmd,stdout=PIPE,stdin=PIPE,stderr=STDOUT)
    try:
        out = p.communicate(timeout=2)[0]
    except TimeoutExpired:
        p.kill()
        out = b"timeout"
    p.kill()
    output = out.decode().split("\n")
    for j in range(0,len(output)):
        if "execute-" in output[j]:
            coverNode.append(get_str_btw(output[j],"execute-","\r"))
            coverNode = sorted(set(coverNode), key=coverNode.index)
    return coverNode


def gen_training_data(program_loc, num):
    population = [bytearray([1, 2, 3, 4]), bytearray([0, 10, 100, 200])]
    #population = [TC1, TC2]
    i = 0
    if not os.path.exists("./seeds"):
        os.mkdir("./seeds")
    else:
        files = os.listdir("./seeds")
        for file in files:
            os.remove(os.path.join("./seeds", file))

    while len(population) <= num:
        new_population = []
        for tc in population:
            new_population.append(mutate(tc,add=False,delete=False))
            if len(new_population) + len(population) >= num:
                break
        population += new_population
    res = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
    for tc in population:
        #coverage = get_coverage(tc, program_loc)
        input_fn = "./seeds/input_" + str(i).zfill(10)
        #label_fn = "./seed/label_" + str(i).zfill(10) + ".txt"
        #cmd = [program_loc , os.path.abspath(input_fn)]
        with open(input_fn, "wb") as f:
            f.write(tc)
        #coverage = get_coverage(tc, cmd)
        #res[len(coverage)] +=1
        #with open(label_fn, "w") as f:
        #    for cov in coverage:
        #        f.write(cov+'\n')
        i+=1
    print(res)
    return population



if __name__ == "__main__":
    gen_training_data("D:\\fuzzer_new\\example\\main.exe", 2000)
