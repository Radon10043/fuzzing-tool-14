#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string>
#include "Datagram.h"

extern Datagram* dtg;

void GenErrInput() {
	Datagram data;
	data.header.conBCDT.wMonth = 1;
	data.header.conBCDT.wDay = 1;
	data.header.conBCDT.wHour = 1;
	data.header.conBCDT.wMinute = 1;
	data.header.conBCDT.wSecond = 1;
	data.header.conBCDT.wMillisec = 1;

	//	unsigned char ucRadarID;	//取值范围[0,5]
	//  unsigned char ucRadarType;	//取值范围[0,2]
	Trajectory t;
	for (int i = 0; i < 3; i++) {
		t.radarinfo[i].ucRadarID = i;
		t.radarinfo[i].ucRadarType = i;
	}
	t.TestA.bPatternEnable = true;
	t.TestB.bPatternEnable = false;
	t.TestD.bPatternEnable = true;
	t.TestD.ucRadarID = 1;
	t.TestD.ucRadarType = 1;
	t.TestD.TestC.ucRadarID = 2;
	t.TestD.TestC.ucRadarType = 2;
	t.TestD.TestC.bPatternEnable = false;
	data.trajectory = t;

	unsigned char* p_char = (unsigned char*)&data;
	FILE* f = fopen("GenErrInput.py", "w");
	printf("%d\n", sizeof(data));

	std::string cmd = "import socket\n";
	cmd += "s = socket.socket()\n";
	cmd += "host = socket.gethostname()\n";
	cmd += "port = 8888\n";
	cmd += "s.connect((host, port))\n";
	cmd += "data = bytes([";
	fprintf(f, cmd.c_str());
	// (unsigned char *) &p + sizeof(p) 为 结构体p的首地址 加上 p的字节大小
	for (; p_char < (unsigned char*)&data + sizeof(data); p_char++) {
		fprintf(f,"%d", *p_char);
		if (p_char != (unsigned char*)&data + sizeof(data)-1)
			fprintf(f, ",");
	}
	fprintf(f, "])\ns.send(data)\ns.close()\n");
	fclose(f);

}