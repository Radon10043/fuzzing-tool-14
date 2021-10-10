#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import math
import os
import random
import socket

import time
from collections import Counter
from subprocess import *
import sys
import keras
import keras.backend as K
import numpy as np
import tensorflow as tf
from keras.layers import Dense, Activation
from keras.models import Sequential
from keras.models import load_model

import utils
import json

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
    def __init__(self, ui, ui_fuzz, fuzz_thread, struct, all_node, program_loc, MAIdll, root_loc,instrVarSetTuple):
        tf.compat.v1.disable_eager_execution()
        # threading.Thread.__init__(self)
        self.ui = ui
        self.uiFuzz = ui_fuzz
        self.fuzzThread = fuzz_thread
        self.struct = struct
        self.input_dim = 0
        self.output_dim = len(all_node)
        self.grads_cnt = int(ui.ProtocolFuzzCfgDialog.seedPerRound.text())
        self.dir = os.path.join(root_loc, "ProtocolFuzz")
        self.program_loc = program_loc
        self.MAIdll = MAIdll
        self.nodes_map = {}
        self.seed_list = []
        self.new_seeds = []
        self.SPLIT_RATIO = 0
        self.round_cnt = 0
        self.all_node = all_node
        self.crash = False
        for idx, node in enumerate(all_node):
            self.nodes_map[node] = idx

        self.idx_name = []
        self.name_idx = {}
        for key, value in struct.items():
            if value["mutation"]:
                self.idx_name.append(key)
                self.name_idx[key] = len(self.idx_name) - 1
                self.input_dim += 1

        self.instrVarSetTuple = instrVarSetTuple

    def setExec(self, exec_module):
        self.exec_module = exec_module

    def crossover(self, fl1, fl2, idxx):
        with open(fl1, "r") as fp1:
            struct1 = json.load(fp1)
        with open(fl2, "r") as fp2:
            struct2 = json.load(fp2)
        fn = os.path.join(self.dir, "input_json", 'crossovers', 'tmp_' + str(idxx) + ".json")
        for key, value in struct2.items():
            p = random.random()
            if p > 0.5 and self.struct[key]["mutation"]:
                struct1[key] = struct2[key]
        with open(fn, "w") as fp:
            json.dump(struct1, fp)


    def process_data(self):
        # obtain raw bitmaps
        raw_bitmap = {}
        tmp_cnt = []
        cov = set()
        crash_cnt = 0

        training_set = np.zeros((len(self.seed_list), self.input_dim), dtype="float64")
        for i, f in enumerate(self.seed_list):
            with open(f, "r") as fp:
                struct = json.load(fp)
            for idx, name in enumerate(self.idx_name):
                training_set[i][idx] = float(struct[name])
        self.max_ = np.max(training_set, axis=0)
        self.min_ = np.min(training_set, axis=0)

        for i, f in enumerate(self.seed_list):
            tmp_list = []
            out = None
            crash = None
            self.fuzzThread.nnInfoSgn.emit("正在执行训练数据：" + f + "\n")
            _, out, crash, _ = utils.getCoverage(f, os.path.join(self.dir, "tmp"), self.exec_module.s, self.exec_module.r, 1,
                                                     self.MAIdll, self.instrVarSetTuple)
            cov = cov.union(set(out))
            if crash:
                self.crash = True
                return
            for edge in out:
                tmp_cnt.append(edge)
                tmp_list.append(edge)
            raw_bitmap[f] = tmp_list
        info = "训练集信息：\n"
        info += "训练集数量：\t\t" + str(len(self.seed_list)) + "\n"
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
            file_name = os.path.join(self.dir, "input_json", "bitmaps", i.split('\\')[-1])
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
        vec = np.zeros((1, self.input_dim), dtype="float64")
        with open(fl, 'r') as fp:
            struct = json.load(fp)
        for idx, name in enumerate(self.idx_name):
            vec[0][idx] = float(struct[name])
        vec = np.nan_to_num((vec - self.min_) / (self.max_ - self.min_))
        return vec

    # training data generator
    def generate_training_data(self, lb, ub):
        seed = np.zeros((ub - lb, self.input_dim), dtype="float64")
        bitmap = np.zeros((ub - lb, self.output_dim))
        for i in range(lb, ub):
            vec = np.zeros((1, self.input_dim), dtype="float64")
            with open(self.seed_list[i], 'r') as fp:
                struct = json.load(fp)
            for idx, name in enumerate(self.idx_name):
                vec[0][idx] = float(struct[name])
            vec = np.nan_to_num((vec - self.min_) / (self.max_ - self.min_))
            seed[i - lb] = vec

        for i in range(lb, ub):
            file_name = os.path.join(self.dir, "input_json","bitmaps", self.seed_list[i].split('\\')[-1] + ".npy")
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
                # load remaining data for last batch
                else:
                    x, y = self.generate_training_data(i, i + batch_size)
                yield x, y

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
                splice_fn = os.path.join(self.dir, "input_json", 'crossovers', 'tmp_' + str(idxx)+".json")
                self.crossover(fl[0], fl[1], idxx)
                x = self.vectorize_file(splice_fn)
                loss_value, grads_value = iterate([x])
                idx = np.flip(
                    np.argsort(np.absolute(grads_value), axis=1)[:, -self.input_dim:].reshape((self.input_dim,)), 0)
                val = np.sign(grads_value[0][idx])
                adv_list.append((idx, val, splice_fn))
            else:
                self.crossover(fl[0], fl[1], idxx + self.grads_cnt)
                splice_fn = os.path.join(self.dir, "input_json",'crossovers', 'tmp_' + str(idxx + self.grads_cnt)+".json")
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
            splice_fn = os.path.join(self.dir, "input_json","crossovers", "tmp_" + str(idxx)+".json")
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
                adv_list = fn(index, fl, model, layer_list, idxx, 0)
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
        seeds_dir = os.path.join(self.dir, "input_json", "seeds")
        self.seed_list = [os.path.join(seeds_dir, i) for i in glob.glob(os.path.join(seeds_dir, "*"))]
        self.new_seeds = [os.path.join(seeds_dir, i) for i in glob.glob(os.path.join(seeds_dir, "id_*"))]
        self.SPLIT_RATIO = len(self.seed_list)
        t0 = time.time()
        self.process_data()
        if self.crash:
            return
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
