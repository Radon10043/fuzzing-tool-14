







#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <stdio.h>
#include <iostream>
#include <winsock2.h>
#include <string>
#include "Datagram.h"
using namespace std;
#pragma comment(lib, "ws2_32.lib")

Datagram* dtg;

int sendUDPresult(char content[], int contentLen)
{
	dtg->trajectory.radonInstr |= 1024;
	
	string returnContent = "";
	for (int i = 0; i < contentLen; i++)
	{
		returnContent += to_string((unsigned char)content[i]);
		returnContent += ",";
	}
	returnContent += "";
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
	sendto(sockClient, returnContent.data(), returnContent.length(), 0, (sockaddr *)&addr, sizeof(SOCKADDR_IN));
	closesocket(sockClient);
	WSACleanup();
	printf("- - - end sendUDP - - -\n");
}

int sendUDPresult(int content[], int contentLen)
{
	dtg->trajectory.radonInstr |= 1024;
	
	string returnContent = "";
	for (int i = 0; i < contentLen; i++)
	{
		returnContent += to_string(content[i]);
		returnContent += " ";
	}
	returnContent += "";
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
	sendto(sockClient, returnContent.data(), returnContent.length(), 0, (sockaddr *)&addr, sizeof(SOCKADDR_IN));
	closesocket(sockClient);
	WSACleanup();
	printf("- - - end sendUDP - - -\n");
}

int main(int argc, char *argv[])
{
	WORD wVersionRequested;
	WSADATA wsaData;
	int err, iLen;
	wVersionRequested = MAKEWORD(2, 2);
	err = WSAStartup(wVersionRequested, &wsaData);
	if (err != 0)
	{
		printf("Load WinSock Failed!");
		return -1;
	}

	int socket_desc, client_sock, c;
	struct sockaddr_in server, client;
	const int BUF_SIZE = sizeof(Datagram);
	char buf[BUF_SIZE];

	socket_desc = socket(AF_INET, SOCK_STREAM, 0);
	if (socket_desc == -1)
	{
		printf("Could not create socket\n");
	}

	server.sin_family = AF_INET;
	server.sin_addr.s_addr = INADDR_ANY;
	server.sin_port = htons(8888);

	if (bind(socket_desc, (struct sockaddr *)&server, sizeof(server)) < 0)
	{
		printf("error");
		return 1;
	}
	puts("bind done");
	listen(socket_desc, 3);
	puts("Waiting for incoming connections...");

	c = sizeof(struct sockaddr_in);
	client_sock = accept(socket_desc, (struct sockaddr *)&client, &c);
	if (client_sock < 0)
	{
		perror("accept failed");
		return 1;
	}
	puts("Connection accepted");
	extern unsigned int UINO;
	UINO = 0;
	while (1)
	{

		int n = recv(client_sock, buf, BUF_SIZE, 0);
		if (n > 0)
		{
			
			
			dtg = (Datagram*)buf;
			CheckData((Datagram *)buf);
		}
		else
		{
			break;
		}
	}
	
	sendUDPresult(buf, sizeof(buf) / sizeof(buf[0]));
	printf("%u.\n", dtg->trajectory.radonInstr);
	return 0;
}