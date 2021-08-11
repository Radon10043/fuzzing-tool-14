import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. 绑定一个本地信息
localaddr = ("", 7001)
udp_socket.bind(localaddr)
i = 0
while (i < 100000):
    i += 1
    # 3. 接收数据
    recv_data = udp_socket.recvfrom(1024)
    recv_msg = recv_data[0]
    send_addr = recv_data[1]

    # 4. 打印接收到的信息
    print("%s:%s" % (str(send_addr), str(recv_msg.decode("utf-8"))))

# 5. 关闭套接字
udp_socket.close()
