import binascii
import os

import crcmod.predefined


class CheckCode:
    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
        self.header_file_path = base_path + "/util/checkCodeLibDir/checkCodeLib/CheckCodeLib.c"
        self.algorithmName = ""
        self.option = ""
        self.code = ""

    def init4str(self, method_str):
        if "PARITY" in method_str:
            self.algorithmName = "parity"
            if "ODD" in method_str:
                self.option = "odd"
                self.code = "getParity(checkList, sizeof(checkList) / sizeof(unsigned int), false);"
            else:
                self.option = "even"
                self.code = "getParity(checkList, sizeof(checkList) / sizeof(unsigned int), false);"
        if "CRC" in method_str:
            self.algorithmName = "crc"
            if "8" in method_str:
                self.option = "crc_8"
                self.code = "crc_8(checkList, sizeof(checkList) / sizeof(unsigned int));"
            elif "16" in method_str:
                self.option = "crc_16"
                self.code = "crc_16(checkList, sizeof(checkList) / sizeof(unsigned int));"
            elif "32" in method_str:
                self.option = "crc_32"
                self.code = "crc_32(checkList, sizeof(checkList) / sizeof(unsigned int));"


def get_support_methods():
    methods = ["PARITY_ODD", "PARITY_EVEN",
               "CRC_8", "CRC_16", "CRC_32"
               # "BCC_NONE"
               ]
    # for crc_table in crcmod.predefined._crc_definitions_table:
    #     methods.append("CRC_" + crc_table[0].upper())
    return methods


def calculate_check_code_from_dec(dec_data_list, method, algorithm):
    """
    10进制转16进制后，再调用hex方法
    @param dec_data_list:
    @param method:
    @param algorithm:
    @return:
    """
    hex_data_list = []
    for dec in dec_data_list:
        hex_data = hex(dec).replace("0x", "")
        if len(hex_data) == 1:
            hex_data = "0" + hex_data
        hex_data_list.append(hex_data)
    return calculate_check_code_from_hex(hex_data_list=hex_data_list, method=method, algorithm=algorithm)


def calculate_check_code_from_hex(hex_data_list, method, algorithm):
    """
    循环冗余校验 crc
    奇偶校验 parity
    异或校验 bcc
    @param method:校验方法
    @param hex_data_list: 16进制数据的列表
    @param algorithm:如果方法需要指定的算法，在这里指定
    @return:校验位的16进制的值，当输出的参数不正确，校验会失败，返回值为-1
    """
    if method == "CRC":
        return calculate_check_code_crc(hex_data_list=hex_data_list, algorithm=algorithm)
    elif method == "PARITY":
        return calculate_check_code_parity(hex_data_list=hex_data_list, algorithm=algorithm)
    elif method == "BCC":
        return calculate_check_code_bcc(hex_data_list=hex_data_list, algorithm=algorithm)


def calculate_check_code_crc(hex_data_list, algorithm):
    """
    循环冗余校验
    @param hex_data_list:
    @param algorithm: 支持的算法，具体可以看 # crcmod.predefined #
    @return:
    """
    try:
        crc = crcmod.predefined.Crc(algorithm)  # 设定算法
    except:
        print("错误的算法")
        return -1
    hex_data = "".join(hex_data_list).replace("0x", "")
    hex_data = binascii.unhexlify(hex_data)
    crc.update(hex_data)
    return hex(crc.crcValue)


def calculate_check_code_parity(hex_data_list, algorithm):
    """
    奇偶校验
    @param algorithm: odd 奇校验 even 偶校验
    @param hex_data_list:
    @return:
    """
    num_of_one = 0
    for hex_data in hex_data_list:
        x = bin(int(hex_data.replace(r"\x", ""), 16))[2:]  # 转二进制
        for ch in x:
            if ch == '1':  # 计算1的个数
                num_of_one += 1
    if algorithm == "ODD":  # 奇数校验，奇数个1的话，不用补1，偶数的1则补1，使1的数量为奇数
        if num_of_one % 2 == 1:
            return hex(0)
        else:
            return hex(1)
    elif algorithm == "EVEN":
        if num_of_one % 2 == 0:
            return hex(0)
        else:
            return hex(1)
    return -1


def calculate_check_code_bcc(hex_data_list, algorithm):
    check_code = 0
    for hex_value in hex_data_list:
        check_code ^= int(hex_value, 16)
    return hex(check_code)
