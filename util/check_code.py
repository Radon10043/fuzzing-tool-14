import binascii
import crcmod.predefined


def calculate_check_code(hex_data_list, method, algorithm):
    """
    循环冗余校验 crc
    奇偶校验 parity
    异或校验 bcc
    @param method:校验方法
    @param hex_data_list: 16进制数据的列表
    @param algorithm:如果方法需要指定的算法，在这里指定
    @return:校验位的16进制的值，当输出的参数不正确，校验会失败，返回值为-1
    """
    if method == "crc":
        return calculate_check_code_crc(hex_data_list=hex_data_list, algorithm=algorithm)
    elif method == "parity":
        return calculate_check_code_parity(hex_data_list=hex_data_list, algorithm=algorithm)
    elif method == "bcc":
        pass


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
    hex_data = "".join(hex_data_list).replace(r"\x", "")
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
    if algorithm == "odd":  # 奇数校验，奇数个1的话，不用补1，偶数的1则补1，使1的数量为奇数
        if num_of_one % 2 == 1:
            return hex(0)
        else:
            return hex(1)
    elif algorithm == "even":
        if num_of_one % 2 == 0:
            return hex(0)
        else:
            return hex(1)
    return -1


def calculate_check_code_bcc(hex_data):
    pass


if __name__ == '__main__':
    hex_data_list = [hex(1), hex(12), hex(57)]
    hex_data_list_handle = []
    for one_hex in hex_data_list:
        one_hex = one_hex.replace("0x", "")
        if len(one_hex) == 1:
            one_hex = "0" + one_hex
        one_hex = r'\x' + one_hex
        hex_data_list_handle.append(one_hex)
    print("origin list is:" + str(hex_data_list_handle))
    result = calculate_check_code(hex_data_list=hex_data_list_handle, method="crc", algorithm="crc-8")
    print(result)
    result = calculate_check_code(hex_data_list=hex_data_list_handle, method="parity", algorithm="even")
    print(result)
