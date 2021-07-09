/*
 * 14所头文件案例
 * 
 * @file: header.h
 * @author: Radon
 * @date: 2021年05月16日 12:15:30
 */

 /*sdhad
 *sdls
 *dhlsd
 */
 /*sdhad
 sdls
 dhlsd
 */
 //#define TKYJ_UINT_INVALID 0xffffffff	
#include <stdbool.h>		
 /***********************************
 消息名称：
 消息源：
 消息宿：
 消息类型：
 ***********************************/
typedef struct TKYJ_LinkDetect
{
	unsigned int uiJds;  //该真
						 //	TKYJ_LinkDetect()
						 //	{
						 //		uiJDS = 0xFFFFFFF;
						 //	}
}TKYJ_LinkDetect;
typedef struct Public_SamplingPt
{
	short int sFd;
	short int sXw;
}Public_SamplingPt;
typedef struct TagSQFreSet
{
	unsigned int uiCsrq;
	unsigned int uiCssj;
	unsigned int uiLdbh;
	unsigned char ucRwms;
	unsigned int uiMblsh;
	unsigned int uiZlID;
	unsigned int uiTKmbbh;
	unsigned char ucKdcysOto1 : 2;
	unsigned char ucKdcyfs2to3 : 2;
	unsigned char ucKdcyfs4to7 : 4;
	unsigned int uiBlzd;
	unsigned int uiYwxds;
	Public_SamplingPt SamPnt[4096];
	unsigned int uiJsxtsbbh;
	unsigned int uiYlzj;
}TKYJ_RadarHrrp;
typedef struct TagSQFreSet
{
	unsigned short SQNum : 8;	//
	unsigned short FreSet : 4;	//
	unsigned short FreModeSet : 4;	//

	unsigned short FixedFre_1 : 8;	//
	unsigned short FixedFre_2 : 8;	//

	unsigned short ChangeFre_1 : 8;	//
	unsigned short ChangeFre_1 : 8;	//

	unsigned short HighDpifre_1 : 8;	//
	unsigned short HighDpifre_2 : 8;	//

	unsigned short CoverFre_1 : 8;	//
	unsigned short CoverFre_2 : 8;	//
	unsigned short CoverFre_3 : 8;	//
	unsigned short CoverFre_4 : 8;	//
}_SQFreSet;
//part1
typedef struct TagDpHead {
	unsigned short dwFrmHead;          //报文头
	unsigned short SourceSystemID : 8;   //源分系统ID；
	unsigned short ObSystemId : 8;       //目的分系统
	struct {
		unsigned short wYear : 8; //年
		unsigned short wMonth : 8; //月
		unsigned short wDay : 8; //日
		unsigned short wHour : 8; //时
		unsigned short wMinite : 8; //分
		unsigned short wSecond : 8; //秒
		unsigned short wMilisec; //秒一下
	}conBCDT;
}DpHead;
typedef struct TagDpDSPParaSet {
	unsigned short AllCancelSwitch : 1;
	unsigned short AllSnapSwitch : 1;
	unsigned short back_6 : 14;
	unsigned short GroupYar : 8;
	unsigned short AutoEngComp : 8;
}_DpDSPParaSet;
typedef struct TagDpDSPPAraSet {
	unsigned short back_1 : 1;
	unsigned short ZBTConTrol : 1;
	unsigned short AfterNYConTrol : 1;
	unsigned short CFARControl : 1;
	unsigned short MTDConTrol : 1;
	unsigned short MTIConTrol : 1;
	unsigned short ZBoutlineCtr : 1;
	unsigned short QXDecCTr : 1;
	unsigned short FYBCtr : 1;
	unsigned short MYPartCtr : 1;
	unsigned short ZPulseLimitCtr : 1;
	unsigned short FbdxCtl : 1;
	unsigned short STCaddCtr : 1;
	unsigned short wPRTChange : 1;
	unsigned short back_2 : 1;
	unsigned short back_3 : 1;
}_DpDSPPAraSet;
typedef struct PDXP_Header
{
	unsigned char ucVER;      //版本，太空预警与监视系统
	unsigned short usMID;     //任务标识
	unsigned int uiSID;       // 信源
	unsigned int uiDID;       // 信宿
	unsigned int uiBID;       // 信息标志
	unsigned int uiNo;        // 包序号，已发送的数据报文帧数
	unsigned char ucFlag;     // 信息处理标志，暂为0，
	unsigned int uiReserved;  //保留
	unsigned short usDATE;    //发送日期
	unsigned int uiTIME;      //发送时标，当前的绝对时
	unsigned short usLen;     //数据长度
}PDXP_Header;
/*sdhad
sdls
dhlsd
*/
typedef struct EularAngle
{
	char valA : 2; //低位在前
	char valB : 2;
	char valC : 4;
	unsigned short int dRoll;   //滚转角 弧度
	double Pitch;  //偏航角 弧度
	double Yaw;    //俯仰角 弧度
				   //软件版本
				   //#abcfmj
}EularAngle;
//
//#kdsaldnk
typedef struct
{
	int valA : 6; //低位在前
	int valB : 6;
	int valC : 20;
	bool a;
	char A;
	unsigned char B;
	signed char C;
	int D;
	unsigned int E;
	signed int F;
	short int G;
	unsigned short int H;
	signed short int I;
	long int J;
	signed long int K;
	unsigned long int L;
	float M;
	double N;
	long double O;
	long P;
	unsigned long Q;
	long long R;
	short S;
	unsigned short T;
}MyStruct;
typedef struct DETECTED_CFAR_ARRAY
{
	float target_range_f;
	float target_freq_f;
	float target_sigma_amp_f;     /**change to i *******/
	float target_sigma_pha_f;     /***change to q *****/
	float target_sigma_noise_f;   /****SN****/
	float target_delta_ev_amp_f;   /***change to i****/
	float target_delta_ev_pha_f;  /*****change to q*****/
	unsigned int bak;
}DETECTED_CFAR_ARRAY;
typedef struct
{
	unsigned char ucRadarID;
	unsigned char ucRadarType;
	bool bPatternEnable;
	float fBeamWidthFreq;
	float fBeamWidthAzm;
	float fBeamWidthElv;
	float fPt[2][3];
	float fGt[2];
	float fLr;
	float fFn;
	float fDx;
	float fDy;
	unsigned short uslen;
	DETECTED_CFAR_ARRAY detected[2];
}RadarInfo;
typedef struct
{
	int d_Time;        //弹道数据         相对时间
	double fnPosition[4096]; //地心绝对坐标
	double fnVelocity[4]; //地心绝对速度
	//EularAngle sEularAngle[5][1024];
	RadarInfo radarinfo[3];
	DpHead abc[4];
	struct
	{
		unsigned char ucRadarID : 8;
		unsigned char ucRadarType;
		bool bPatternEnable;
	}TestA;
	struct
	{
		unsigned char ucRadarID;
		unsigned char ucRadarType;
		bool bPatternEnable;
		//EularAngle sEularAngle[3][2];
	}TestB;
	struct
	{
		unsigned char ucRadarID;
		unsigned char ucRadarType;
		bool bPatternEnable;
		struct TestC
		{
			unsigned char ucRadarID : 8;
			unsigned char ucRadarType;
			bool bPatternEnable;
		};
	}TestD;
}Trajectory;