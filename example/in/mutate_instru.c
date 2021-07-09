#include <stdio.h>
#include <stdbool.h>
#include "D:\fuzzing-tool-14\example\Datagram.h"
#include "D:\fuzzing-tool-14\example\Trajectory.h"
void mutate(Datagram data, char* savePath, int r){
	data.header.dwFrmHead ^= r;
	data.header.SourceSystemID ^= r;
	data.header.ObSystemId ^= r;

	FILE* f;
	f = fopen(savePath, "wb");
	fwrite(&data, sizeof(data), 1, f);
	fclose(f);
}

unsigned int getInstrumentValue(Datagram data){
	return data.trajectory.radonInstr;
}

void resetInstrumentValue(Datagram* data){
    data->trajectory.radonInstr = 0;
}