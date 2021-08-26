#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import math
import os
import random
import socket
import sys
import time
from collections import Counter
from subprocess import *

import keras
import keras.backend as K
import numpy as np
import tensorflow as tf
from keras.layers import Dense, Activation
from keras.models import Sequential
from keras.models import load_model

import utils

HOST = '127.0.0.1'
PORT = 12012
seed = 12
np.random.seed(seed)
random.seed(seed)
tf.random.set_seed(seed)
argvv = sys.argv[1:]
PROGRAM_LOC = "D:\\fuzzer_new\\example\\main.exe"


def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]


def get_coverage(cmd):
    coverNode = []
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    try:
        out = p.communicate(timeout=2)[0]
    except TimeoutExpired:
        p.kill()
        out = b"timeout"
    p.kill()
    output = out.decode().split("\n")
    for j in range(0, len(output)):
        if "execute-" in output[j]:
            coverNode.append(get_str_btw(output[j], "execute-", "\r"))
            coverNode = sorted(set(coverNode), key=coverNode.index)
    return coverNode


# learning rate decay
def step_decay(epoch):
    initial_lrate = 0.001
    drop = 0.7
    epochs_drop = 10.0
    lrate = initial_lrate * math.pow(drop, math.floor((1 + epoch) / epochs_drop))
    return lrate


class LossHistory(keras.callbacks.Callback):

    def on_train_begin(self, logs={}):
        self.losses = []
        self.lr = []

    def on_epoch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))
        self.lr.append(step_decay(len(self.losses)))
        print(step_decay(len(self.losses)))


class NN():
    def __init__(self, ui, ui_fuzz, fuzz_thread, input_dim, all_node, grads_cnt, program_loc, MAIdll, root_loc):
        tf.compat.v1.disable_eager_execution()
        # threading.Thread.__init__(self)
        self.ui = ui
        self.uiFuzz = ui_fuzz
        self.fuzzThread = fuzz_thread
        self.input_dim = input_dim
        self.output_dim = len(all_node)
        self.grads_cnt = grads_cnt
        self.dir = os.path.join(root_loc, "AIFuzz")
        self.program_loc = program_loc
        self.MAIdll = MAIdll
        self.nodes_map = {}
        self.seed_list = []
        self.new_seeds = []
        self.SPLIT_RATIO = 0
        self.round_cnt = 0
        self.all_node = all_node

        for idx, node in enumerate(all_node):
            self.nodes_map[node] = idx

    def setExec(self, exec_module):
        self.exec_module = exec_module

    def crossover(self, fl1, fl2, idxx):
        tmp1 = open(fl1, 'rb').read()
        ret = 1
        randd = fl2
        while ret == 1:
            tmp2 = open(randd, 'rb').read()
            if len(tmp1) >= len(tmp2):
                lenn = len(tmp2)
                head = tmp2
                tail = tmp1
            else:
                lenn = len(tmp1)
                head = tmp1
                tail = tmp2
            f_diff = 0
            l_diff = 0
            for i in range(lenn):
                if tmp1[i] != tmp2[i]:
                    f_diff = i
                    break
            for i in reversed(range(lenn)):
                if tmp1[i] != tmp2[i]:
                    l_diff = i
                    break
            if f_diff >= 0 and l_diff > 0 and (l_diff - f_diff) >= 2:
                splice_at = f_diff + random.randint(1, l_diff - f_diff - 1)
                head = list(head)
                tail = list(tail)
                tail[:splice_at] = head[:splice_at]
                tail = bytes(tail)
                fn = os.path.join(self.dir, 'crossovers', 'tmp_' + str(idxx))
                self.MAIdll["mutate"].setValueInRange(tail)
                fn = bytes(fn, encoding="utf8")
                self.MAIdll["mutate"].mutate(tail, fn, 0xffffffff)
                ret = 0
            print(f_diff, l_diff)
            randd = random.choice(self.seed_list)

    def process_data(self):
        # obtain raw bitmaps
        raw_bitmap = {}
        tmp_cnt = []
        cov = set()
        crash_cnt = 0
        for i, f in enumerate(self.seed_list):
            tmp_list = []
            out = None
            crash = None
            if f in self.exec_module.cov_map.keys():
                out, crash = self.exec_module.cov_map[f]
            else:
                _, out, crash, _ = utils.getCoverage(open(f, "rb").read(), self.exec_module.s, self.exec_module.r,1, self.MAIdll)
            cov = cov.union(set(out))
            if crash:
                crash_cnt += 1
            for edge in out:
                tmp_cnt.append(edge)
                tmp_list.append(edge)
            raw_bitmap[f] = tmp_list
        info = "训练集信息：\n"
        info += "训练集数量：\t\t" + str(len(self.seed_list)) + "\n"
        info += "覆盖节点数：\t\t" + str(len(cov)) + "\n"
        info += "崩溃次数：\t\t" + str(crash_cnt) + "\n"
        self.fuzzThread.nnInfoSgn.emit(info)
        counter = Counter(tmp_cnt).most_common()

        # save bitmaps to individual numpy label
        label = [self.nodes_map[f[0]] for f in counter]
        bitmap = np.zeros((len(self.seed_list), len(label)))
        for idx, i in enumerate(self.seed_list):
            tmp = raw_bitmap[i]
            for j in tmp:
                if self.nodes_map[j] in label:
                    bitmap[idx][label.index((self.nodes_map[j]))] = 1

        # label dimension reduction
        fit_bitmap = np.unique(bitmap, axis=1)
        print("data dimension" + str(fit_bitmap.shape))
        # save training data
        self.output_dim = fit_bitmap.shape[1]
        for idx, i in enumerate(self.seed_list):
            file_name = os.path.join(self.dir, "bitmaps", i.split('\\')[-1])
            np.save(file_name, fit_bitmap[idx])

    # compute jaccard accuracy for multiple label
    def accur_1(self, y_true, y_pred):
        y_true = tf.round(y_true)
        pred = tf.round(y_pred)
        summ = tf.constant(self.output_dim, dtype=tf.float32)
        wrong_num = tf.subtract(summ, tf.reduce_sum(tf.cast(tf.equal(y_true, pred), tf.float32), axis=-1))
        right_1_num = tf.reduce_sum(
            tf.cast(tf.logical_and(tf.cast(y_true, tf.bool), tf.cast(pred, tf.bool)), tf.float32),
            axis=-1)
        return K.mean(tf.divide(right_1_num, tf.add(right_1_num, wrong_num)))

    # get vector representation of input
    def vectorize_file(self, fl):
        seed = np.zeros((1, self.input_dim))
        tmp = open(fl, 'rb').read()
        ln = len(tmp)
        if ln < self.input_dim:
            tmp = tmp + (self.input_dim - ln) * b'\x00'
        seed[0] = [j for j in bytearray(tmp)]
        seed = seed.astype('float32') / 255
        return seed

    # training data generator
    def generate_training_data(self, lb, ub):
        seed = np.zeros((ub - lb, self.input_dim))
        bitmap = np.zeros((ub - lb, self.output_dim))
        for i in range(lb, ub):
            tmp = open(self.seed_list[i], 'rb').read()
            ln = len(tmp)
            if ln < self.input_dim:
                tmp = tmp + (self.input_dim - ln) * b'\x00'
            seed[i - lb] = [j for j in bytearray(tmp)]

        for i in range(lb, ub):
            file_name = os.path.join(self.dir, "bitmaps", self.seed_list[i].split('\\')[-1] + ".npy")
            bitmap[i - lb] = np.load(file_name)
        return seed, bitmap

    def train_generate(self, batch_size):
        while 1:
            np.random.shuffle(self.seed_list)
            # load a batch of training data
            for i in range(0, self.SPLIT_RATIO, batch_size):
                # load full batch
                if (i + batch_size) > self.SPLIT_RATIO:
                    x, y = self.generate_training_data(i, self.SPLIT_RATIO)
                    x = x.astype('float32') / 255
                # load remaining data for last batch
                else:
                    x, y = self.generate_training_data(i, i + batch_size)
                    x = x.astype('float32') / 255
                yield (x, y)

    # compute gradient for given input
    def gen_adv2(self, f, fl, model, layer_list, idxx, splice):
        adv_list = []
        loss = layer_list[-2][1].output[:, f]
        grads = K.gradients(loss, model.input)[0]
        iterate = K.function([model.input], [loss, grads])
        ll = 2
        while fl[0] == fl[1]:
            fl[1] = random.choice(self.seed_list)

        for index in range(ll):
            x = self.vectorize_file(fl[index])
            loss_value, grads_value = iterate([x])
            idx = np.flip(np.argsort(np.absolute(grads_value), axis=1)[:, -self.input_dim:].reshape((self.input_dim,)),
                          0)
            val = np.sign(grads_value[0][idx])
            adv_list.append((idx, val, fl[index]))

        # do not generate spliced seed for the first round
        if splice == 1 and self.round_cnt != 0:
            if self.round_cnt % 2 == 0:
                splice_fn = os.path.join(self.dir, 'crossovers', 'tmp_' + str(idxx))
                self.crossover(fl[0], fl[1], idxx)
                x = self.vectorize_file(splice_fn)
                loss_value, grads_value = iterate([x])
                idx = np.flip(
                    np.argsort(np.absolute(grads_value), axis=1)[:, -self.input_dim:].reshape((self.input_dim,)), 0)
                val = np.sign(grads_value[0][idx])
                adv_list.append((idx, val, splice_fn))
            else:
                self.crossover(fl[0], fl[1], idxx + self.grads_cnt)
                splice_fn = os.path.join(self.dir, 'crossovers', 'tmp_' + str(idxx + self.grads_cnt))
                x = self.vectorize_file(splice_fn)
                loss_value, grads_value = iterate([x])
                idx = np.flip(
                    np.argsort(np.absolute(grads_value), axis=1)[:, -self.input_dim:].reshape((self.input_dim,)), 0)
                val = np.sign(grads_value[0][idx])
                adv_list.append((idx, val, splice_fn))

        return adv_list

    # compute gradient for given input without sign
    def gen_adv3(self, f, fl, model, layer_list, idxx, splice):
        adv_list = []
        loss = layer_list[-2][1].output[:, f]
        grads = K.gradients(loss, model.input)[0]
        iterate = K.function([model.input], [loss, grads])
        ll = 2
        while fl[0] == fl[1]:
            fl[1] = random.choice(self.seed_list)

        for index in range(ll):
            x = self.vectorize_file(fl[index])
            loss_value, grads_value = iterate([x])
            idx = np.flip(np.argsort(np.absolute(grads_value), axis=1)[:, -self.input_dim:].reshape((self.input_dim,)),
                          0)
            # val = np.sign(grads_value[0][idx])
            val = np.random.choice([1, -1], self.input_dim, replace=True)
            adv_list.append((idx, val, fl[index]))

        # do not generate spliced seed for the first round
        if splice == 1 and self.round_cnt != 0:
            self.crossover(fl[0], fl[1], idxx)
            splice_fn = os.path.join(self.dir, "crossovers", "tmp_" + str(idxx))
            x = self.vectorize_file(splice_fn)
            loss_value, grads_value = iterate([x])
            idx = np.flip(np.argsort(np.absolute(grads_value), axis=1)[:, -self.input_dim:].reshape((self.input_dim,)),
                          0)
            # val = np.sign(grads_value[0][idx])
            val = np.random.choice([1, -1], self.input_dim, replace=True)
            adv_list.append((idx, val, splice_fn))

        return adv_list

    def gen_mutate2(self, model, edge_num, sign):
        tmp_list = []
        # select seeds
        start = time.time()
        if self.round_cnt == 0 or len(self.new_seeds) == 0:
            new_seed_list = self.seed_list
        else:
            new_seed_list = self.new_seeds

        if len(new_seed_list) < edge_num:
            rand_seed1 = [os.path.abspath(new_seed_list[i]) for i in
                          np.random.choice(len(new_seed_list), edge_num, replace=True)]
        else:
            rand_seed1 = [os.path.abspath(new_seed_list[i]) for i in
                          np.random.choice(len(new_seed_list), edge_num, replace=False)]
        if len(new_seed_list) < edge_num:
            rand_seed2 = [os.path.abspath(self.seed_list[i]) for i in
                          np.random.choice(len(self.seed_list), edge_num, replace=True)]
        else:
            rand_seed2 = [os.path.abspath(self.seed_list[i]) for i in
                          np.random.choice(len(self.seed_list), edge_num, replace=False)]

        # function pointer for gradient computation
        fn = self.gen_adv2 if sign else self.gen_adv3

        # select output neurons to compute gradient
        interested_indice = np.random.choice(self.output_dim, edge_num)
        layer_list = [(layer.name, layer) for layer in model.layers]

        grad_fn = os.path.join(self.dir, 'gradient_info_p')
        with open(grad_fn, 'w') as f:
            for idxx in range(len(interested_indice[:])):
                # kears's would stall after multiple gradient compuation. Release memory and reload model to fix it.
                if idxx % 100 == 0:
                    del model
                    K.clear_session()
                    # model = build_model()
                    # model.load_weights('hard_label.h5')
                    model = load_model(os.path.join(self.dir, 'hard_label.h5'),
                                       custom_objects={"accur_1": self.accur_1})
                    layer_list = [(layer.name, layer) for layer in model.layers]

                print("number of feature " + str(idxx))
                index = int(interested_indice[idxx])
                fl = [rand_seed1[idxx], rand_seed2[idxx]]
                adv_list = fn(index, fl, model, layer_list, idxx, 1)
                tmp_list.append(adv_list)
                for ele in adv_list:
                    ele0 = [str(el) for el in ele[0]]
                    ele1 = [str(int(el)) for el in ele[1]]
                    ele2 = ele[2]
                    f.write(",".join(ele0) + '|' + ",".join(ele1) + '|' + ele2 + "\n")
        end = time.time()
        info = "已生成梯度信息！\n"
        info += "轮次：\t\t\t" + str(self.round_cnt + 1) + "\n"
        info += "生成梯度信息的种子数：\t\t" + str(edge_num) + "\n"
        info += "梯度类型：\t\t\t" + ("有符号" if sign else "无符号(随机)") + "\n"
        info += "时间：\t\t\t" + "{:.2f}".format(end - start) + "秒\n"
        info += "梯度文件保存路径：\n" + grad_fn + "\n"
        info += "可以开始测试...\n"
        self.uiFuzz.text_browser_nn.append(info)

    def train(self, model):
        start = time.time()
        loss_history = LossHistory()
        lrate = keras.callbacks.LearningRateScheduler(step_decay)
        callbacks_list = [loss_history, lrate]
        model.fit_generator(self.train_generate(16),
                            steps_per_epoch=(self.SPLIT_RATIO / 16 + 1),
                            epochs=10,
                            verbose=1, callbacks=callbacks_list)
        end = time.time()
        save_loc = os.path.join(self.dir, "hard_label.h5")
        model.save(save_loc)
        info = "模型训练完成！\n"
        info += "轮次：\t\t\t" + str(self.round_cnt + 1) + "\n"
        info += "输入维数：\t\t\t" + str(self.input_dim) + "\n"
        info += "输出维数：\t\t\t" + str(self.output_dim) + "\n"
        info += "训练时间：\t\t\t" + "{:.2f}".format(end - start) + "秒\n"
        info += "保存路径：\n" + save_loc + "\n"
        self.uiFuzz.text_browser_nn.append(info)

    def build_model(self):
        batch_size = 32
        num_classes = self.output_dim
        epochs = 50
        model = Sequential()
        model.add(Dense(2048, input_dim=self.input_dim))
        model.add(Activation('relu'))
        model.add(Dense(num_classes))
        model.add(Activation('sigmoid'))
        # opt = keras.optimizers.adam(lr=0.0001)
        opt = keras.optimizers.Adam(learning_rate=0.0001)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=[self.accur_1])
        model.summary()
        return model

    def gen_grad(self, data):
        seeds_dir = os.path.join(self.dir, "seeds")
        self.seed_list = [os.path.join(seeds_dir, i) for i in glob.glob(os.path.join(seeds_dir, "*"))]
        self.new_seeds = [os.path.join(seeds_dir, i) for i in glob.glob(os.path.join(seeds_dir, "id*"))]
        self.SPLIT_RATIO = len(self.seed_list)
        t0 = time.time()
        self.process_data()
        model = self.build_model()
        self.train(model)
        # model.load_weights('hard_label.h5')
        self.gen_mutate2(model, self.grads_cnt, data[:5] == b"train")
        self.round_cnt += 1
        print(time.time() - t0)

    def run(self):
        tf.compat.v1.disable_eager_execution()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen(1)
        conn, addr = sock.accept()
        print('connected by execution module ' + str(addr))
        self.gen_grad(b"train")
        conn.sendall(b"start")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            else:
                self.gen_grad(data)
                conn.sendall(b"start")
        conn.close()
