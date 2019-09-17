/**
 * CJMCU75 I2C temperature sensor driver for Arduino.
 * 
 * Developped for the DomoHome projet.
 * 
 * Copyright Alexy Torres Aurora Dugo
 */

#ifndef __CJMCU75_H__
#define __CJMCU75_H__

#include "Arduino.h"

class CJMCU75
{
  private:
    uint32_t address;
    
    uint16_t getRawTemperature(void) const;
    
  public:
    CJMCU75(const bool A0, const bool A1, const bool A2);
    ~CJMCU75(void);

    float getDegTemperature(void) const;
    float getFarTemperature(void) const;
};

#endif /* #ifndef __CJMCU75_H__ */
