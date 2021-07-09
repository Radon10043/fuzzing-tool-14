/*
 * 南京大学徐安孜写的发送UDP的例子
 * 
 * @file: CheckData.cpp
 * @author: Radon
 * @date: 2021年05月15日 11:30:33
 */

#include <stdio.h>
#include <iostream>
#include "Datagram.h"
using namespace std;

void TestA(Trajectory* t);
void TestB(Trajectory* t);
void TestC(Trajectory* t);
void TestD(Trajectory* t);
unsigned int UINO;

extern Datagram* dtg;

bool CheckDate(Datagram* data) {
	if (!(data->header.conBCDT.wMonth >= 1 &&
		data->header.conBCDT.wMonth <= 12))
		return false;
	if (!(data->header.conBCDT.wDay >= 1 &&
		data->header.conBCDT.wDay <= 31))
		return false;
	if (data->header.conBCDT.wHour > 23)
		return false;
	if (data->header.conBCDT.wMinute > 59)
		return false;
	if (data->header.conBCDT.wSecond > 59)
		return false;
	if (data->header.conBCDT.wMillisec > 999999)
		return false;

	printf("Pass Date Check\n");
	return true;
}

bool CheckRadarInfo(RadarInfo* radar) {
	if (!(radar->ucRadarID >= 0 &&
		radar->ucRadarID <= 5))
		return false;
	if (!(radar->ucRadarType >= 0 &&
		radar->ucRadarType <= 2))
		return false;

	printf("Pass RadarInfo Check\n");
	return true;
}

bool CheckUiNo(Datagram* data) {
	printf("CheckUiNo!\n");
	if (data->header.uiNo != UINO + 1)
		return false;
	UINO++;
	printf("Pass UiNo Check\n");
	return true;
}

void TestA(Trajectory* t) {
	printf("TestA\n");
	if (!t->TestA.bPatternEnable)
		return;
	TestB(t);
}

void TestB(Trajectory* t) {
	printf("TestB\n");
	if (t->TestB.bPatternEnable)
		return;
	TestD(t);
}

void TestD(Trajectory* t) {
	printf("TestD\n");
	if (!t->TestD.bPatternEnable)
		return;
	for (int i = 0; i < 3; i++)
		if (t->radarinfo[i].ucRadarID == t->TestD.ucRadarID &&
			t->radarinfo[i].ucRadarType == t->TestD.ucRadarType)
			TestC(t);
}


void TestC(Trajectory* t) {
	printf("TestC\n");
	if (t->TestD.TestC.bPatternEnable)
		return;
	for (int i = 0; i < 3; i++)
		if (t->radarinfo[i].ucRadarID == t->TestD.TestC.ucRadarID &&
			t->radarinfo[i].ucRadarType == t->TestD.TestC.ucRadarType) {
			int k = t->radarinfo[i].ucRadarType;
			int a[2];
			//Bug: Array Index OOB
			if (k == 2) {
				a[1000000]=0;
				printf("hey.\n");
			}
		}
}


void CheckData(Datagram* data) {
	//if (!CheckUiNo(data))
	//	return;

	if (!CheckDate(data))
		return;

	for (int i = 0; i < 3; i++)
		if (!CheckRadarInfo(&data->trajectory.radarinfo[i]))
			return;

	TestA(&data->trajectory);
}

void myFunc(MyStruct* data) {
	cout << "Hi, here is myFunc:" << endl;
	cout << "value1: " << data->value1 << endl;
	cout << "value2: " << data->value2 << endl;
	cout << "value3: " << data->value3 << endl;
	cout << "value4: " << data->value4 << endl;
	cout << "value5: " << data->value5 << endl;
}