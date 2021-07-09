#include <iostream>
#include <Windows.h>
#include <fstream>
#include "D:\fuzzing-tool-14\example\Datagram.h"
#include "D:\fuzzing-tool-14\example\Trajectory.h"
using namespace std;

int main(){
	Datagram data;
	data.header.dwFrmHead = 4859;
	data.header.SourceSystemID = 111;
	data.header.ObSystemId = 94;
	data.header.uiNo = 12333.0;
	data.header.conBCDT.wYear = 21.0;
	data.header.conBCDT.wMonth = 11.0;
	data.header.conBCDT.wDay = 18.0;
	data.header.conBCDT.wHour = 15.0;
	data.header.conBCDT.wMinute = 15.0;
	data.header.conBCDT.wSecond = 15.0;
	data.header.conBCDT.wMillisec = 100.0;
	data.header.checksum = 213.0;
	data.trajectory.radarinfo[0].ucRadarID = 155;
	data.trajectory.radarinfo[0].ucRadarType = 164;
	data.trajectory.radarinfo[0].detected[0].bak = 2211137566;
	data.trajectory.radarinfo[0].detected[1].bak = 448288759;
	data.trajectory.radarinfo[1].ucRadarID = 30;
	data.trajectory.radarinfo[1].ucRadarType = 197;
	data.trajectory.radarinfo[1].detected[0].bak = 123.0;
	data.trajectory.radarinfo[1].detected[1].bak = 456.0;
	data.trajectory.radonInstr = 0.0;
	data.trajectory.TestA.ucRadarID = 114;
	data.trajectory.TestA.ucRadarType = 92;
	data.trajectory.TestA.bPatternEnable = 5;
	data.trajectory.TestB.ucRadarID = 232;
	data.trajectory.TestB.ucRadarType = 77;
	data.trajectory.TestB.bPatternEnable = 68;
	data.trajectory.TestD.ucRadarID = 250;
	data.trajectory.TestD.ucRadarType = 228;
	data.trajectory.TestD.bPatternEnable = 83;
	data.trajectory.TestD.TestC.ucRadarID = 44;
	data.trajectory.TestD.TestC.ucRadarType = 112;
	data.trajectory.TestD.TestC.bPatternEnable = 130;

	ofstream f("seed");
	f.write((char*)&data, sizeof(data));
	f.close();
	return 0;
}