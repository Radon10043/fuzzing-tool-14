typedef struct Public_SamplingPt
{
	short int sFd;
	short int sXw;
}Public_SamplingPt;
typedef struct TKYJ_RadarHrrp
{
  unsigned int uiCsrq;
  unsigned int uiCssj;
  unsigned int uiLdbh;
  unsigned char ucRwms;
  unsigned int uiMblsh;
  unsigned int uiZlID;
  unsigned int uiTKmbbh;
  unsigned char ucKdcysOto1:2;
  unsigned char ucKdcyfs2to3:2;
  unsigned char ucKdcyfs4to7:4;
  unsigned int uiBlzd;
  unsigned int uiYwxds;
  Public_SamplingPt SamPnt[4096];
  unsigned int uiJsxtsbbh;
  unsigned int uiYlzj;
} TKYJ_RadarHrrp;