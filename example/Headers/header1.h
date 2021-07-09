typedef struct TagDpHead{
	unsigned short dwFrmHead;          //报文头
	unsigned short SourceSystemID:8;   //源分系统ID；
	unsigned short ObSystemId:8;       //目的分系统
	struct{
		unsigned short wYear     :8; //年
		unsigned short wMonth    :8; //月
		unsigned short wDay      :8; //日
		unsigned short wHour     :8; //时
		unsigned short wMinite   :8; //分
		unsigned short wSecond   :8; //秒
		unsigned short wMilisec    ; //秒一下
	}conBCDT;
}DpHead;