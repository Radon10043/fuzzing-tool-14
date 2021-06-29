import argparse
import collections
import functools
import networkx as nx

def loadData(fileName):
    file = open(fileName,'r')#read file
    weightedEdges = []
    elementList = []
    for line in file:
        data = line.split(',')
        elementList.append(data[0])
        elementList.append(data[1])
        elementList.append(int(data[2]))
        elementTuple = tuple(elementList)
        elementList.clear()
        weightedEdges.append(elementTuple)
    return weightedEdges

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-d', '--dot', type=str, required=True, help="Path to dot-file representing the graph.")
    args = parser.parse_args ()

    print ("\nParsing %s .." % args.dot)
    G = nx.DiGraph(nx.drawing.nx_pydot.read_dot(args.dot))#读取dot文件，并把它转化为nx图
    print (G.edges.data('weight'))
    
    weightedEdges = []    #新的list，用于存储图的权重、边等信息，这里需要把权重变成int型再重新存储。
    for tupleOrigin in G.edges.data('weight'):
        temp = list(tupleOrigin)    #tuple内的数据无法更改，只能先变成list再改信息
        temp[2] = int(temp[2])
        print(temp)
        weightedEdges.append(tuple(temp))
    P=nx.DiGraph()
    P.add_weighted_edges_from(weightedEdges)
    print ("shortest path = ", nx.dijkstra_path(P,'A','D'))
    print ("shortest path length = ", nx.dijkstra_path_length(P,'A','D'))

    # G = nx.DiGraph()
    # weightedEdges = [('A','B',1),('B','C',1),('C','D',1),('B','D',1),('D','A',1)]
    # #weightedEdges = loadData('weightedEdges.txt')
    # #print(weightedEdges)
    # G.add_weighted_edges_from(weightedEdges)
    # #print (G.edges.data('weight'))
    # print ("shortest path = ", nx.dijkstra_path(G,'A','D'))
    # print ("shortest path length = ", nx.dijkstra_path_length(G,'A','D'))