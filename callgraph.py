'''
Author: Radon
Date: 2020-09-28 13:18:56
LastEditors: Radon
LastEditTime: 2021-06-17 15:51:49
Description: Hi, say something
'''
import re
import public

def get_str_btw(s, f, b):
    par = s.partition(f)
    return (par[2].partition(b))[0][:]

'''
@description: 创建函数调用图
@param {*} source_loc 列表, 其中存储了所有源文件的位置
@param {*} graph_loc 调用图保存的路径
@return {*}
'''
def createCallGraph(source_loc, graph_loc):
    f_graph = open(graph_loc,mode="w+")
    graph = []
    customize = []      #这个列表用于存储自定义的函数

    for source in source_loc:
        brace = 0
        try:
            f_source = open(source,encoding="utf8")
            lines = f_source.readlines()
        except:
            f_source = open(source)
            lines = f_source.readlines()
        lines = public.deleteNote(lines)

        start = "empty"
        for line in lines:
            # 如果行内有#define #pragma 和 #include的话, 为了防止分析结果错误, 跳过这一行
            if "#define" in line or "#pragma" in line or "#include" in line:
                continue
            # 如果行内有左括号且brace == 0, 证明这一行定义了某个函数
            if "(" in line and brace == 0:
                start = line.split("(")[0].split(" ")[-1]
                start = re.sub("[^A-Za-z1-9_]","",start)
                if not start in customize:
                    customize.append(start)
            # 如果行内有左括号且brace != 0, 证明这一行调用了某个函数
            elif "(" in line and brace != 0:
                words = re.sub("[^A-Za-z1-9_(]"," ",line).split("(")
                for end in words:
                    end = end.split(" ")[-1]
                    if end in customize:
                        path = start+","+end
                        #先把路径信息存到一个list中，下面是在write前检测一下是否已存在这个路径（这是针对调用多次同一函数的情况）
                        found = False
                        for i in range(0,len(graph)):
                            if path in graph[i]:
                                print("I found it!\n")
                                found = True
                                break
                        if found == False :
                            graph.append(path+",1")
                        else:
                            path = graph.pop(i).split(",")
                            weight = int(path[2])+1
                            graph.append(path[0]+","+path[1]+","+str(weight))
            if "{" in line:
                brace += 1
            if "}" in line:
                brace -= 1

    print("graph:",graph)
    for i in range(0,len(graph)):
        f_graph.write(graph[i]+"\n")
    f_graph.close()
    f_source.close()

if __name__ == '__main__':
    source_loc = ["C:\\Users\\Radon\\Desktop\\fuzztest\\4th\\example\\main.cpp","C:\\Users\\Radon\\Desktop\\fuzztest\\4th\\example\\CheckData.cpp"]
    graph_loc = "C:\\Users\\Radon\\Desktop\\fuzztest\\4th\\example\\graph_cg.txt"
    createCallGraph(source_loc,graph_loc)