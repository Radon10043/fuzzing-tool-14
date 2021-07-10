'''
Author: your name
Date: 2021-05-08 10:29:12
LastEditTime: 2021-07-10 19:11:13
Description: file content
'''
import socket               # 导入 socket 模块

monitorSocket = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM)  # 创建 socket 对象
host = socket.gethostname()  # 获取本地主机名
port = 9999  # 设置端口
monitorSocket.bind(("127.0.0.1", port))        # 绑定端口
# monitorSocket.listen(5)                 # 等待客户端连接
#while True:
data, client_addr = monitorSocket.recvfrom(1024)
#print(data,client_addr)
print(bytes(data))

    #data = conn.recv(1024)
    #print(data)
    # n = []
    # for i in data[:]:
    #     n.append(i)
    # print(n)
monitorSocket.close()                # 关闭连接