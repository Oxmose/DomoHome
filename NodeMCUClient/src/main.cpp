#include "CJMCU75.h"
#include "UDPInterface.h"
#include "Connection.h"
#include "Logger.h"

CJMCU75 tempSensor(false, false, false);

void sendTemperature(char* packet)
{
  float temp;
  temp = tempSensor.getDegTemperature();
  char msg[32];
  char str[6];
  strncpy(msg, "REQ Temp: \0", 11);
  sprintf(str, "%f", temp);
  strncat(msg, str, 6);
  msg[16] = 0;
  Logger::logInfo(msg);

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
  Logger::logInfo(msg);

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
  Logger::logInfo(msg);
  
  pinMode(gpio, OUTPUT);
  analogWrite(gpio, value);
}

void setup() {
  analogWriteFreq(500);
  analogWriteRange(255);

  Logger::logInit(); 

  wifiConnect();
  
  delay(1000);
}

void loop() {
  char  packet[PACKET_SIZE];
  
  uint32_t packetType;
  uint16_t i;
  
  bool  packeted = false;

  receivePacket(packet, PACKET_SIZE);

  Logger::logInfo("RECEIVED PACKET");

  packetType = ((info_packet_t*)packet)->packetType;
  if(packetType == REQ_TEMPERATURE_TYPE)
  {
    Logger::logInfo("REQ TEMP");
    sendTemperature(packet);
    packeted = true;
  }
  else if(packetType == REQ_TOGGLE_TYPE)
  {
    Logger::logInfo("REQ TOGGLE");
    toggleGPIO(((toggle_packet_t*)packet)->gpio, ((toggle_packet_t*)packet)->state != 0);
  }
  else if(packetType == REQ_SET_PWM_TYPE)
  {
    Logger::logInfo("REQ PWM");
    setPwm(((pwm_packet_t*)packet)->gpio, ((pwm_packet_t*)packet)->value);
  }
  else
  {
    Logger::logWarning("Unknown packet");
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
    sendPacket(packet, PACKET_SIZE);;
    Logger::logInfo("SENT PACKET");
  }
}
