/**
 * CJMCU75 I2C temperature sensor driver for Arduino.
 * 
 * Developped for the DomoHome projet.
 * 
 * Copyright Alexy Torres Aurora Dugo
 */

#ifndef __CJMCU75_H__
#define __CJMCU75_H__

#include <stdint.h>

void CJMCU75_init(const uint8_t A0, const uint8_t A1, const uint8_t A2);
uint16_t CJMCU75_getRawTemperature(void);
float CJMCU75_getDegTemperature(void);
float CJMCU75_getFarTemperature(void);

#endif /* #ifndef __CJMCU75_H__ */
