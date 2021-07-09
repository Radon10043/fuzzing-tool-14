import socket               # 导入 socket 模块

monitorSocket = socket.socket()  # 创建 socket 对象
host = socket.gethostname()  # 获取本地主机名
port = 8889  # 设置端口
monitorSocket.bind((host, port))        # 绑定端口
monitorSocket.listen(5)                 # 等待客户端连接
print("start")
while True:
    conn, addr = monitorSocket.accept()     # 建立客户端连接。
    print(conn, addr)
    # while True:
    # try:
    data = conn.recv(1024)
    n = []
    for i in data[:]:
        n.append(i)
    print(n)
    # except Exception as e:
    #     print(e)
    # print(monitorSocket.recv(1024))
    # print('连接地址：', addr)
    # c.send(b'hello python socket')
    conn.close()                # 关闭连接
