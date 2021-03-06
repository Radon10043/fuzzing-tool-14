"""
Author: Radon
Date: 2021-07-20 02:46:39
LastEditors: Radon
LastEditTime: 2021-07-22 17:28:40
Description: 根据源代码和行数信息，获取注释，添加到struct_dict中
"""
import re
import traceback

from loguru import logger as urulog

singe_comment_patten = '//.*'  # 标准匹配单行注释
multi_comment_patten = '\/\*(?:[^\*]|\*+[^\/\*])*\*+\/'  # 标准匹配多行注释  可匹配跨行注释
bracket_patten = '\\[(.*?)]'  # 提取中括号之间的内容，用于提取数组的编号
singe_comment_re = re.compile(singe_comment_patten)  # 单行注释
multi_comment_re = re.compile(multi_comment_patten)  # 编译正则表达式
bracket_re = re.compile(bracket_patten)  # 编译中括号正则表达式
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
    no_name_count = 0
    struct_dict_with_comment = dict()
    struct_name, code_file_path, code_line_number, code_file_str = None, None, None, None
    loc_set = set()
    for struct_name in struct_dict.keys():
        struct_name = struct_name
        struct_dict_with_comment[struct_name] = dict()
        for var_type_name in struct_dict[struct_name].keys():
            loc_str = struct_dict[struct_name][var_type_name]["loc"]
            if ("noName" in var_type_name) and (loc_str in loc_set):
                continue
            loc_set.add(loc_str)
            loc = loc_str.split("?")
            code_file_path = loc[0]
            code_line_number = loc[1]
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
                comment = match_result[0] \
                    .replace("//", "") \
                    .replace("/*", "") \
                    .replace("*/", "") \
                    .strip("*")
                token_list = var_type_name.split(".")
                if "[" in token_list[-1] and "]" in token_list[-1]:
                    urulog.info("该行是数组变量，注释需要重命名")
                    num_list = bracket_re.findall(token_list[-1])
                    if len(num_list) == 1:
                        comment = comment + str(num_list[0])
                    else:
                        comment = comment + " " + ".".join(num_list)

                struct_dict[struct_name][var_type_name]["comment"] = comment
            pattern = re.compile(r'(\?)(.*)(\?)')
            var_name_without_uuid = pattern.sub(r'', var_type_name)
            if var_name_without_uuid != var_type_name:
                # 说明是无名变量
                no_name_count += 1
                parts = var_name_without_uuid.split(":")
                part_1 = parts[0] + "_" + str(no_name_count) + ":"
                part_2 = parts[1]
                var_name_without_uuid = part_1 + part_2
            struct_dict_with_comment[struct_name][var_name_without_uuid] = struct_dict[struct_name][var_type_name]
    return struct_dict_with_comment
