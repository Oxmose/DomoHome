#include "CJMCU75.h"
#include <Wire.h>
#include <stdint.h>

#define CJMCU75_BASE_ADDR 0x48
#define CJMCU75_REG_TEMP  0x00
#define CJMCU75_DEG_RED   0.125f
#define CJMCU75_SIGN_BIT  0x0400
#define CJMCU75_MASK      0xF800

static uint32_t address;

void CJMCU75_init(const uint8_t A0, const uint8_t A1, const uint8_t A2)
{
  address = CJMCU75_BASE_ADDR;
  if(A0)
  {
    address += 1;
  }
  if(A1)
  {
    address += 2;
  }
  if(A2)
  {
    address += 4;
  }

  Wire.begin(14, 12);
}

uint16_t CJMCU75_getRawTemperature(void) 
{
  uint16_t rawTemp;
  uint16_t readValue;
  uint8_t* readValueBuffer;
  uint8_t  buffer;
  
  
  rawTemp = UINT32_MAX;
  readValueBuffer = (uint8_t*)&readValue;
  
  Wire.beginTransmission((int)address);
  Wire.write(CJMCU75_REG_TEMP);

  if(Wire.endTransmission())
  {
    return rawTemp;
  }
  if(!Wire.requestFrom((int)address, sizeof(uint16_t)))
  {
    return rawTemp;
  }
  
  Wire.readBytes(readValueBuffer, sizeof(uint16_t));
  buffer = readValueBuffer[0];
  readValueBuffer[0] = readValueBuffer[1];
  readValueBuffer[1] = buffer;

  rawTemp = readValue >> 5;
	return rawTemp;
}

float CJMCU75_getDegTemperature(void)
{
  float degData;
  uint16_t rawData;
  
  rawData = CJMCU75_getRawTemperature();

  if(rawData & CJMCU75_SIGN_BIT)
  {
    rawData |= CJMCU75_MASK;
    rawData = ~rawData + 1;
    degData = rawData * -CJMCU75_DEG_RED;
  }
  else 
  {
    degData = rawData * CJMCU75_DEG_RED;
  }

  return degData;
}

float CJMCU75_getFarTemperature(void)
{
  float degData;
  uint16_t rawData;
  
  rawData = CJMCU75_getRawTemperature();

  if(rawData & CJMCU75_SIGN_BIT)
  {
    rawData |= CJMCU75_MASK;
    rawData = ~rawData + 1;
    degData = rawData * -CJMCU75_DEG_RED;
  }
  else 
  {
    degData = rawData * CJMCU75_DEG_RED;
  }

  return (degData * 1.8 + 32);
}
