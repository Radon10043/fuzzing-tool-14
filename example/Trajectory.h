#ifndef TRAJECTORY_H
#define TRAJECTORY_H

#include <stdbool.h>

typedef struct EularAngle {
	char valA : 2; //低位在前
	char valB : 2;
	char valC : 4;
	unsigned short int dRoll;   //滚转角 弧度
	double Pitch;  //偏航角 弧度
	double Yaw;    //俯仰角 弧度
	//软件版本
}EularAngle;

typedef struct DETECTED_CFAR_ARRAY {
	//float target_range_f;
	//float target_freq_f;
	//float target_sigma_amp_f;     /**change to i *******/
	//float target_sigma_pha_f;     /***change to q *****/
	//float target_sigma_noise_f;   /****SN****/
	//float target_delta_ev_amp_f;   /***change to i****/
	//float target_delta_ev_pha_f;  /*****change to q*****/
	unsigned int bak;
}DETECTED_CFAR_ARRAY;

typedef struct RadarInfo {
	unsigned char ucRadarID;	//取值范围[0,5]
	unsigned char ucRadarType;	//取值范围[0,2]
	//bool bPatternEnable;
	DETECTED_CFAR_ARRAY detected[2];
}RadarInfo;

typedef struct {
	//int d_Time;        //弹道数据         相对时间
	//double fnPosition[4096]; //地心绝对坐标
	//double fnVelocity[4]; //地心绝对速度
	//EularAngle sEularAngle[2][2];
	RadarInfo radarinfo[3];
	unsigned int radonInstr:20;
	struct {
		unsigned char ucRadarID;
		unsigned char ucRadarType;
		bool bPatternEnable;
	}TestA;
	struct {
		unsigned char ucRadarID;
		unsigned char ucRadarType;
		bool bPatternEnable;
	}TestB;
	struct {
		unsigned char ucRadarID;
		unsigned char ucRadarType;
		bool bPatternEnable;
		struct {
			unsigned char ucRadarID;
			unsigned char ucRadarType;
			bool bPatternEnable;
		}TestC;
	}TestD;
}Trajectory;
#endif // TRAJECTORY_H
