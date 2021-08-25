
#include <stdbool.h>
#include <stdlib.h>
#include "checksum.h"

static void             init_crcdnp_tab( void );

static bool             crc_tabdnp_init         = false;
static uint16_t         crc_tabdnp[256];

/*
 * uint16_t crc_dnp( const unsigned char* input_str, size_t num_bytes );
 *
 * The function crc_dnp() calculates the DNP CRC checksum of a provided byte
 * string in one pass.
 */

uint16_t crc_dnp( const unsigned char *input_str, size_t num_bytes ) {

	uint16_t crc;
	uint16_t tmp;
	uint16_t short_c;
	uint16_t low_byte;
	uint16_t high_byte;
	const unsigned char *ptr;
	size_t a;

	if ( ! crc_tabdnp_init ) init_crcdnp_tab();

	crc = CRC_START_DNP;
	ptr = input_str;

	if ( ptr != NULL ) for (a=0; a<num_bytes; a++) {

		short_c = 0x00ff & (uint16_t) *ptr;
		tmp     =  crc       ^ short_c;
		crc     = (crc >> 8) ^ crc_tabdnp[ tmp & 0xff ];

		ptr++;
	}

	crc       = ~crc;
	low_byte  = (crc & 0xff00) >> 8;
	high_byte = (crc & 0x00ff) << 8;
	crc       = low_byte | high_byte;

	return crc;

}  /* crc_dnp */

/*
 * uint16_t update_crc_dnp( uint16_t crc, unsigned char c );
 *
 * The function update_crc_dnp() is called for every new byte in a row that
 * must be feeded tot the CRC-DNP routine to calculate the DNP CRC.
 */

uint16_t update_crc_dnp( uint16_t crc, unsigned char c ) {

	uint16_t tmp;
	uint16_t short_c;

	short_c = 0x00ff & (uint16_t) c;

	if ( ! crc_tabdnp_init ) init_crcdnp_tab();

	tmp =  crc       ^ short_c;
	crc = (crc >> 8) ^ crc_tabdnp[ tmp & 0xff ];

	return crc;

}  /* update_crc_dnp */

/*
 * static void init_crcdnp_tab( void );
 *
 * For better performance, the DNP CRC calculation uses a precompiled list with
 * bit patterns that are used in the XOR operation in the main routine. This
 * table is calculated once at the start of the program by the
 * init_crcdnp_tab() routine.
 */

static void init_crcdnp_tab( void ) {

	int i;
	int j;
	uint16_t crc;
	uint16_t c;

	for (i=0; i<256; i++) {

		crc = 0;
		c   = (uint16_t) i;

		for (j=0; j<8; j++) {

			if ( (crc ^ c) & 0x0001 ) crc = ( crc >> 1 ) ^ CRC_POLY_DNP;
			else                      crc =   crc >> 1;

			c = c >> 1;
		}

		crc_tabdnp[i] = crc;
	}

	crc_tabdnp_init = true;

}  /* init_crcdnp_tab */
