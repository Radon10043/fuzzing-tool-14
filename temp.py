'''
Author: Radon
Date: 2021-07-12 10:28:52
LastEditors: Radon
LastEditTime: 2021-08-09 12:31:32
Description: temp file
'''
import ctypes, os

from util.check_code import calculate_check_code_from_hex, calculate_check_code_from_dec, get_support_methods

data_10 = [
    251,
    17, 111, 96, 45, 48, 0, 0, 22, 10, 16,
    15, 13, 13, 101, 0, 214, 0, 0, 0, 153, 162, 1, 0, 30, 71, 202,
    129,
    247, 87, 182, 25, 30, 197, 1, 0, 121, 0, 0, 2, 200, 1, 1, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 2, 0, 7, 4, 62, 0,
    114,
    91, 1, 232, 78, 0, 248, 228, 1, 44, 112, 1
]

# fb 11 6f 60 2d 30 00 00 16 0a 10 0f 0d 0d 65 00 d6 00 00 00 99 a2 01 00 1e 47 ca 81 f7 57 b6 19 1e c5 01 00 79 00 00 02 c8 01 01 00 00 00 00 00 08 00 00 00 00 00 02 00 07 04 3e 00 72 5b 01 e8 4e 00 f8 e4 01 2c 70 01

# data = bytes(
#     data_10)
# dll = ctypes.cdll.LoadLibrary("C:\\Users\\Administrator\\Desktop\\Tool\\example_21.7.16\\in\\mutate_instru.dll")
# # dll.setValueInRange(data)
# print(dll.getInstrumentValue(data))

# check_code_methods = get_support_methods()
# for index in range(len(check_code_methods)):
#     check_code = calculate_check_code_from_dec(dec_data_list=data, method=check_code_methods[index].split("_")[0],
#                                                algorithm=check_code_methods[index].split("_")[1])
#     print(check_code)

data = bytes([153, 170, 36, 2, 15, 233, 239, 95, 69, 206, 176, 153, 142, 168, 50, 37, 75, 110, 167, 112, 41, 231, 0, 0, 114, 28, 15, 15, 37, 50, 158, 209, 19, 175, 0, 0, 245, 154, 69, 86, 57, 205, 148, 103, 214, 4, 0, 0, 250, 149, 143, 15, 20, 165, 63, 234, 7, 248, 72, 130, 23, 251, 0, 28, 107, 0, 79, 158, 0, 177, 13, 0])
dll = ctypes.cdll.LoadLibrary("C:/Users/Radon/Desktop/fuzztest/4th/example_21.7.16/in/instrument.dll")
instrValue = dll.getInstrumentValue(data)
print("instrument value:", instrValue)