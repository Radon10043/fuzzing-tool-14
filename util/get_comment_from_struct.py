'''
Author: Radon
Date: 2021-07-20 02:46:39
LastEditors: Radon
LastEditTime: 2021-07-22 17:28:40
Description: Hi, say something
'''
import re
import traceback
import staticAnalysis as sa

singe_comment_patten = '//.*'  # 标准匹配单行注释
multi_comment_patten = '\/\*(?:[^\*]|\*+[^\/\*])*\*+\/'  # 标准匹配多行注释  可匹配跨行注释

singe_comment_re = re.compile(singe_comment_patten)  # 单行注释

multi_comment_re = re.compile(multi_comment_patten)  # 编译正则表达式
remove_keywords = ["char", "double", "enum", "float", "int", "long", "short", "unsigned", "struct", "union", "signed",
                   "void", ";"]


def handle_struct(struct_dict: dict):
    """向结构体的字典中添加注释

    Parameters
    ----------
    struct_dict : dict
        结构体字典

    Returns
    -------
    dict
        返回的dict中新增了comment的key

    Notes
    -----
    [description]
    """
    unknown_var_info = list()
    struct_name = None
    for struct_name in struct_dict.keys():
        struct_name = struct_name
        for var_type_name in struct_dict[struct_name].keys():
            var_path_name = var_type_name.split(" ")[-1]
            var_name = var_path_name.split(".")[-1].split(":")[0]  # 该成员变变量的名字
            try:
                if "*" in struct_dict[struct_name][var_type_name]["loc"]:
                    unknown_var_info.append(var_type_name)
                    continue
                else:
                    code_file_path = struct_dict[struct_name][var_type_name]["loc"].split("?")[0]
                    code_line_number = struct_dict[struct_name][var_type_name]["loc"].split("?")[1]
            except BaseException as e:
                print("\033[1;31m")
                traceback.print_exc()
                print("\033[0m")

            # 获取注释
            try:
                code_file_str = open(code_file_path, encoding="utf", mode="r").readlines()[int(code_line_number) - 1]
            except UnicodeDecodeError:
                code_file_str = open(code_file_path, encoding="gbk", mode="r").readlines()[int(code_line_number) - 1]
            except BaseException as e:
                print("\033[1;31m")
                traceback.print_exc()
                print("\033[0m")

            match_result = singe_comment_re.findall(code_file_str)
            if len(match_result) == 0:
                match_result = multi_comment_re.findall(code_file_str)
            if len(match_result) == 0:
                struct_dict[struct_name][var_type_name]["comment"] = "该成员变量没有注释说明"
            else:
                struct_dict[struct_name][var_type_name]["comment"] = match_result[0].replace("//", "").replace("/*",
                                                                                                               "").replace(
                    "*/", "").strip("*")
    for var_type_name in unknown_var_info:
        var_info = struct_dict[struct_name][var_type_name]
        file_path = var_info["loc"].split("*")[0]
        struct_end_line_number = var_info["loc"].split("*")[1]
        try:
            file_content = open(file_path, mode="r", encoding="gbk").readlines()
        except:
            file_content = open(file_path, mode="r", encoding="utf").readlines()
        # 定位这个结构体的范围
        line_number = int(struct_end_line_number) - 2
        while True:
            handle_line = file_content[line_number].strip()
            if len(handle_line) == 0:
                line_number -= 1
                continue
            handle_line_split = handle_line.split()
            if "typedef" in handle_line_split or "struct" in handle_line_split:
                break
            elif ":" in handle_line:
                handle_line_backup = handle_line
                # 确认是否是无名变量
                # TODO 找到了无名变量和他的备注，但是只反着找到了第一个，需要为无名变量编号
                for remove_keyword in remove_keywords:
                    handle_line = handle_line.replace(remove_keyword, "").strip()
                handle_line.replace(" ", "").strip()
                handle_line_split_contain_empty = handle_line.split(":")
                handle_line_split = list()
                for one in handle_line_split_contain_empty:
                    if len(one) != 0:
                        handle_line_split.append(one)
                if len(handle_line_split) == 1:
                    match_result = singe_comment_re.findall(handle_line_backup)
                    if len(match_result) == 0:
                        match_result = multi_comment_re.findall(code_file_str)
                    if len(match_result) == 0:
                        comment_result = "无名变量没有注释说明"
                    else:
                        comment_result = match_result[0].replace("//", "").replace("/*", "").replace("*/", "").strip(
                            "*")
                    struct_dict[struct_name][var_type_name]["comment"] = comment_result
            line_number -= 1
    return struct_dict
