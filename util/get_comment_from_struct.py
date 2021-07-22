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
    for struct_name in struct_dict.keys():
        for var_type_name in struct_dict[struct_name].keys():
            var_path_name = var_type_name.split(" ")[-1]
            var_name = var_path_name.split(".")[-1].split(":")[0]  # 该成员变变量的名字
            try:
                if struct_dict[struct_name][var_type_name]["loc"] is None:
                    raise sa.VariableNoNameError
                code_file_path = struct_dict[struct_name][var_type_name]["loc"].split("?")[0]
                code_line_number = struct_dict[struct_name][var_type_name]["loc"].split("?")[1]
            except sa.VariableNoNameError:
                struct_dict[struct_name][var_type_name]["comment"] = "该成员变量没有名字"
                continue
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
                    "*/", "").strip()
    return struct_dict
