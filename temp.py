'''
Author: Radon
Date: 2021-07-12 10:28:52
LastEditors: Radon
LastEditTime: 2021-07-12 12:03:13
Description: temp file
'''
import ctypes

data = bytes([251, 17, 111, 96, 45, 48, 0, 0, 22, 10, 16, 15, 13, 13, 101, 0, 214, 0, 0, 0, 153, 162, 1, 0, 30, 71, 202, 129, 247, 87, 182, 25, 30, 197, 1, 0, 121, 0, 0, 2, 200, 1, 1, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 2, 0, 7, 4, 62, 0, 114, 91, 1, 232, 78, 0, 248, 228, 1, 44, 112, 1])
dll = ctypes.cdll.LoadLibrary("C:\\Users\\Radon\\Desktop\\fuzztest\\4th\\example_21.7.5\\in\\mutate_instru.dll")
dll.setValueInRange(data)
print(dll.getInstrumentValue(data))