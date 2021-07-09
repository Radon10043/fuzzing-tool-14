







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
	dtg->trajectory.radonInstr |= 2;
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
	dtg->trajectory.radonInstr |= 4;
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
	dtg->trajectory.radonInstr |= 8;
	printf("CheckUiNo!\n");
	if (data->header.uiNo != UINO + 1)
		return false;
	UINO++;
	printf("Pass UiNo Check\n");
	return true;
}

void TestA(Trajectory* t) {
	dtg->trajectory.radonInstr |= 16;
	printf("TestA\n");
	if (!t->TestA.bPatternEnable)
		return;
	TestB(t);
}

void TestB(Trajectory* t) {
	dtg->trajectory.radonInstr |= 32;
	printf("TestB\n");
	if (t->TestB.bPatternEnable)
		return;
	TestD(t);
}

void TestD(Trajectory* t) {
	dtg->trajectory.radonInstr |= 128;
	printf("TestD\n");
	if (!t->TestD.bPatternEnable)
		return;
	for (int i = 0; i < 3; i++)
		if (t->radarinfo[i].ucRadarID == t->TestD.ucRadarID &&
			t->radarinfo[i].ucRadarType == t->TestD.ucRadarType)
			TestC(t);
}


void TestC(Trajectory* t) {
	dtg->trajectory.radonInstr |= 64;
	printf("TestC\n");
	if (t->TestD.TestC.bPatternEnable)
		return;
	for (int i = 0; i < 3; i++)
		if (t->radarinfo[i].ucRadarID == t->TestD.TestC.ucRadarID &&
			t->radarinfo[i].ucRadarType == t->TestD.TestC.ucRadarType) {
			int k = t->radarinfo[i].ucRadarType;
			int a[2];
			
			if (k == 2) {
				a[1000000]=0;
				printf("hey.\n");
			}
		}
}


void CheckData(Datagram* data) {
	dtg->trajectory.radonInstr |= 1;
	
	

	if (!CheckDate(data))
		return;

	for (int i = 0; i < 3; i++)
		if (!CheckRadarInfo(&data->trajectory.radarinfo[i]))
			return;

	TestA(&data->trajectory);
}

void myFunc(MyStruct* data) {
	dtg->trajectory.radonInstr |= 512;
	cout << "Hi, here is myFunc:" << endl;
	cout << "value1: " << data->value1 << endl;
	cout << "value2: " << data->value2 << endl;
	cout << "value3: " << data->value3 << endl;
	cout << "value4: " << data->value4 << endl;
	cout << "value5: " << data->value5 << endl;
}