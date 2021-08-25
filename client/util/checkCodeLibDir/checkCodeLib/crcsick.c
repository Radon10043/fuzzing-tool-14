#include <stdlib.h>
#include "checksum.h"

/*
 * uint16_t crc_sick( const unsigned char *input_str, size_t num_bytes );
 *
 * The function crc_sick() calculates the SICK CRC value of an input string in
 * one pass.
 */

uint16_t crc_sick( const unsigned char *input_str, size_t num_bytes ) {

	uint16_t crc;
	uint16_t low_byte;
	uint16_t high_byte;
	uint16_t short_c;
	uint16_t short_p;
	const unsigned char *ptr;
	size_t a;

	crc     = CRC_START_SICK;
	ptr     = input_str;
	short_p = 0;

	if ( ptr != NULL ) for (a=0; a<num_bytes; a++) {

		short_c = 0x00ff & (uint16_t) *ptr;

		if ( crc & 0x8000 ) crc = ( crc << 1 ) ^ CRC_POLY_SICK;
		else                crc =   crc << 1;

		crc    ^= ( short_c | short_p );
		short_p = short_c << 8;

		ptr++;
	}

	low_byte  = (crc & 0xff00) >> 8;
	high_byte = (crc & 0x00ff) << 8;
	crc       = low_byte | high_byte;

	return crc;

}  /* crc_sick */

/*
 * uint16_t update_crc_sick( uint16_t crc, unsigned char c, unsigned char prev_byte );
 *
 * The function update_crc_sick() calculates a new CRC-SICK value based on the
 * previous value of the CRC and the next byte of the data to be checked.
 */

uint16_t update_crc_sick( uint16_t crc, unsigned char c, unsigned char prev_byte ) {

	uint16_t short_c;
	uint16_t short_p;

	short_c  =   0x00ff & (uint16_t) c;
	short_p  = ( 0x00ff & (uint16_t) prev_byte ) << 8;

	if ( crc & 0x8000 ) crc = ( crc << 1 ) ^ CRC_POLY_SICK;
	else                crc =   crc << 1;

	crc &= 0xffff;
	crc ^= ( short_c | short_p );

	return crc;

}  /* update_crc_sick */
