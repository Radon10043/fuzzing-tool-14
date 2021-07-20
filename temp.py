'''
Author: Radon
Date: 2021-07-12 10:28:52
LastEditors: Radon
LastEditTime: 2021-07-12 12:03:13
Description: temp file
'''
import ctypes

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

data = bytes(
    data_10)
dll = ctypes.cdll.LoadLibrary("C:\\Users\\Administrator\\Desktop\\Tool\\example_21.7.16\\in\\mutate_instru.dll")
# dll.setValueInRange(data)
print(dll.getInstrumentValue(data))

# check_code_methods = get_support_methods()
# for index in range(len(check_code_methods)):
#     check_code = calculate_check_code_from_dec(dec_data_list=data, method=check_code_methods[index].split("_")[0],
#                                                algorithm=check_code_methods[index].split("_")[1])
#     print(check_code)
