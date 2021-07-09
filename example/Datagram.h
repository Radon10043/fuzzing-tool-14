/*
 * 南京大学徐安孜写的发送UDP的例子
 * 
 * @file: Datagram.h
 * @author: Radon
 * @date: 2021年05月15日 11:31:14
 */

#ifndef DATAGRAM_H
#define DATAGRAM_H
#include "Trajectory.h"
#include <stdbool.h>


typedef struct TagDpHead {
	unsigned short dwFrmHead;          //报文头，unsigned short是16位
	unsigned short SourceSystemID : 8;   //源分系统ID；
	unsigned short ObSystemId : 8;       //目的分系统
	unsigned int uiNo;			   //包序号
	struct {
		unsigned short wYear : 8; //年
		unsigned short wMonth : 8; //月，  取值范围[1,12]
		unsigned short wDay : 8; //日，  取值范围[1,31]
		unsigned short wHour : 8; //时，  取值范围[0,23]
		unsigned short wMinute : 8; //分，	 取值范围[0,59]
		unsigned short wSecond : 8; //秒，  取值范围[0,59]
		unsigned short wMillisec;     //微秒，取值范围[0,999999]
	}conBCDT;
	unsigned int checksum;			//unsigned int 是32位
}DpHead;

typedef struct Datagram {
	DpHead header;
	Trajectory trajectory;
}Datagram;

//自己写的一个简单的结构体
typedef struct RadonStruct {
	unsigned short value1 : 8;
	unsigned short value2 : 8;
	unsigned int value3 : 8;
	unsigned int value4 : 8;
	unsigned int value5 : 8;
}MyStruct;

void CheckData(Datagram* data);

void myFunc(MyStruct* data);

#endif