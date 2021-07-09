/*
 * @Author: your name
 * @Date: 2021-05-08 10:23:59
 * @LastEditTime: 2021-05-09 14:27:15
 * @Description: file content
 */
#define  _WINSOCK_DEPRECATED_NO_WARNINGS
#include <stdio.h>
#include <WinSock2.h>
#include <Windows.h>
using namespace std;
#pragma comment(lib,"WS2_32.lib")

int sendUDPresult(const char* content){
    printf("- - - start sendUDP - - -\n");
    WORD wVersionRequested;
    WSADATA wsaData;
    int err;

    wVersionRequested = MAKEWORD(1, 1);

    err = WSAStartup(wVersionRequested, &wsaData);
    if (err != 0)
    {
        printf("err");
        return 0;
    }
    SOCKET sockClient = socket(AF_INET, SOCK_DGRAM, 0);
    SOCKADDR_IN addr;
    addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9999);
    const char* sendData = content;
    sendto(sockClient, sendData, strlen(sendData), 0, (sockaddr*)&addr, sizeof(SOCKADDR_IN));
    closesocket(sockClient);
    WSACleanup();
    printf("- - - end sendUDP - - -\n");
}



int main(void)
{
    sendUDPresult("************************hello my first udp *************************\n");
    /*WORD wVersionRequested;
    WSADATA wsaData;
    int err;

    wVersionRequested = MAKEWORD(1, 1);

    err = WSAStartup(wVersionRequested, &wsaData);
    if (err != 0)
    {
        printf("err");
        return 0;
    }
    SOCKET sockClient = socket(AF_INET, SOCK_DGRAM,0);
    SOCKADDR_IN addr;
    addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8888);
    const char* sendData = "hello";
    sendto(sockClient, sendData, strlen(sendData), 0, (sockaddr*)&addr, sizeof(SOCKADDR_IN));
    closesocket(sockClient);
    WSACleanup();*/
    system("pause");
    return 0;
}