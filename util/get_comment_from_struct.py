import re

singe_comment_patten = '//.*'  # 标准匹配单行注释
multi_comment_patten = '\/\*(?:[^\*]|\*+[^\/\*])*\*+\/'  # 标准匹配多行注释  可匹配跨行注释

singe_comment_re = re.compile(singe_comment_patten)  # 单行注释

multi_comment_re = re.compile(multi_comment_patten)  # 编译正则表达式


def get_code_str_list(header_path_list):
    header_content_list = []
    for path in header_path_list:
        try:
            file = open(path, mode="r", encoding="utf")
        except Exception as e:
            file = open(path, mode="r", encoding="gbk")
        for line in file:
            header_content_list.append(line.strip())
    return header_content_list


def handle_struct(struct_dict: dict):
    header_path_list = []
    header_path_list.append(r"C:\Users\Administrator\Desktop\Tool\example_21.7.16\Trajectory.h")
    header_path_list.append(r"C:\Users\Administrator\Desktop\Tool\example_21.7.16\Datagram.h")
    code_str_list = get_code_str_list(header_path_list=header_path_list)
    last_struct_name = ""
    struct_dict_from_header = {}
    temp_list = []

    for code_str in code_str_list:
        if code_str.startswith("typedef") or code_str.startswith("struct"):
            struct_dict_from_header[last_struct_name] = temp_list
            temp_list = []
            last_struct_name = code_str.replace("typedef", "").replace("struct", "").replace("}", "").strip()
        else:
            temp_list.append(code_str.strip())
    struct_dict_from_header.pop("")
    for struct_name in struct_dict.keys():
        for var_type_name in struct_dict[struct_name].keys():
            var_path_name = var_type_name.split(" ")[-1]
            var_name = var_path_name.split(".")[-1].split(":")[0]  # 该成员变变量的名字
            var_path_list = var_path_name.replace("." + var_name, "").split(".")  # 用.组成的地址
            code_file_path = struct_dict[struct_name][var_type_name]["loc"].split("?")[0]
            code_line_number = struct_dict[struct_name][var_type_name]["loc"].split("?")[1]
            try:
                code_file_str = open(code_file_path, encoding="utf", mode="r").readlines()[int(code_line_number) - 1]
            except:
                code_file_str = open(code_file_path, encoding="gbk", mode="r").readlines()[int(code_line_number) - 1]
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
