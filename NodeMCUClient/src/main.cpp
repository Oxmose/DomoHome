#include "CJMCU75.h"
#include "UDPInterface.h"
#include "Connection.h"
#include "Logger.h"

void sendTemperature(char* packet, uint8_t unit)
{
  float temp;
  if(unit == REQ_TEMPERATURE_UNIT_C)
    temp = CJMCU75_getDegTemperature();
  else
    temp = CJMCU75_getFarTemperature();
  char msg[32];
  char str[6];
  strncpy(msg, "REQ Temp: \0", 11);
  sprintf(str, "%f", temp);
  strncat(msg, str, 6);
  msg[16] = 0;
  logInfo(msg);

  ((temperature_packet_t*)packet)->temperature = temp;
  ((temperature_packet_t*)packet)->packetType = TEMPERATURE_PACKET_TYPE;
}

void toggleGPIO(const uint8_t gpio, const uint8_t value)
{
  char msg[32] = {0};
  char str[3];
  strncpy(msg, "REQ Toggle: \0", 13);
  sprintf(str, "%u", gpio);
  strncat(msg, str, 3);
  sprintf(str, "%u", value);
  strncat(msg, " to \0", 5);
  strncat(msg, str, 3);
  msg[24] = 0;
  logInfo(msg);

  pinMode(gpio, OUTPUT);
  
  if(value)
  {
    digitalWrite(gpio, HIGH);
    
  }
  else 
  {
    digitalWrite(gpio, LOW);
  }
}

void setPwm(const uint8_t gpio, const uint8_t value)
{
  char msg[32] = {0};
  char str[3];
  strncpy(msg, "REQ PWM: \0", 10);
  sprintf(str, "%u", gpio);
  strncat(msg, str, 3);
  sprintf(str, "%u", value);
  strncat(msg, " to \0", 5);
  strncat(msg, str, 3);
  msg[21] = 0;
  logInfo(msg);
  
  pinMode(gpio, OUTPUT);
  analogWrite(gpio, value);
}

void setup() {
  analogWriteFreq(500);
  analogWriteRange(255);

  logInit(); 
  CJMCU75_init(false, false, false);

  wifiConnect();
  
  delay(1000);
}

void loop() {
  char  packet[PACKET_SIZE];
  
  uint32_t packetType;
  uint16_t i;
  char ip[16] = {0};
  uint32_t port;
  
  bool  packeted = false;

  receivePacket(ip, &port, packet, PACKET_SIZE);

  logInfo("RECEIVED PACKET");

  packetType = ((info_packet_t*)packet)->packetType;
  if(packetType == REQ_TEMPERATURE_TYPE)
  {
    logInfo("REQ TEMP");
    sendTemperature(packet, ((info_packet_t*)packet)->data[0]);
    packeted = true;
  }
  else if(packetType == REQ_TOGGLE_TYPE)
  {
    logInfo("REQ TOGGLE");
    toggleGPIO(((toggle_packet_t*)packet)->gpio, ((toggle_packet_t*)packet)->state != 0);
  }
  else if(packetType == REQ_SET_PWM_TYPE)
  {
    logInfo("REQ PWM");
    setPwm(((pwm_packet_t*)packet)->gpio, ((pwm_packet_t*)packet)->value);
  }
  else
  {
    logWarning("Unknown packet");
  }

#if 1
  for(i = 0; i < PACKET_SIZE; ++i)
  {
    Serial.print((int)packet[i]);
  }
  Serial.println("");
#endif

  if(packeted)
  {
    sendPacket(ip, port, packet, PACKET_SIZE);
    logInfo("SENT PACKET");
  }
}
