/**
 * UDP Interface difinition, contains UDP packets def
 * 
 * Developped for the DomoHome projet.
 * 
 * Copyright Alexy Torres Aurora Dugo
 */

#ifndef __UDP_INTERFACE_H__
#define __UDP_INTERFACE_H__

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define TEMPERATURE_PACKET_TYPE 0x1

#define REQ_TEMPERATURE_UNIT_C 0x0
#define REQ_TEMPERATURE_UNIT_F 0x1

#define REQ_TEMPERATURE_TYPE    0x2
#define REQ_TOGGLE_TYPE         0x3
#define REQ_SET_PWM_TYPE        0x4

#define PACKET_SIZE 20

typedef struct temperature_packet
{
  uint32_t packetType;
  
  float temperature;

  char pad[12];
} temperature_packet_t;

typedef struct info_packet
{
  uint32_t packetType;

  char data[16];
} info_packet_t;

typedef struct toggle_packet
{
  uint32_t packetType;
 
  uint8_t gpio;
  uint8_t state;

  char pad[14];  
} toggle_packet_t;

typedef struct pwm_packet
{
  uint32_t packetType;
 
  uint8_t gpio;
  uint8_t value;

  char pad[14];  
} pwm_packet_t;

#endif /* #ifndef __UDP_INTERFACE_H__ */
