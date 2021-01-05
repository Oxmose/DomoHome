#include <Arduino.h>
#include <WiFiUdp.h>
#include <string.h>

#include "Connection.h"
#include "UDPInterface.h"
#include "Logger.h"

static WiFiUDP udpClient;

void wifiConnect(void)
{
  Serial.print("\n");
  logInfo("Connecting to " NET_SSID);

  IPAddress ip(192, 168, 0, 11);
  IPAddress gateway(192, 168, 0, 254);
  IPAddress subnet(255, 255, 255, 0);

  WiFi.mode(WIFI_STA);
  WiFi.config(ip, gateway, subnet);  
  WiFi.begin(NET_SSID, NET_PASS);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\n");

  logInfo("WiFi connected");
   
  char msg[100];
  char IP[] = "xxx.xxx.xxx.xxx";
  char str[12];
  sprintf(str, "%d", SERVER_PORT);
  WiFi.localIP().toString().toCharArray(IP, 16);
  strncpy(msg, "IP address: \0", 13);
  strncat(msg, IP, 16);
  strncat(msg, ":", 1);
  strncat(msg, str, strlen(str));
  logInfo(msg);

  /* Init pseudo connection */
  udpClient.begin(SERVER_PORT);
  udpClient.flush();
}

void receivePacket(char* ip, uint32_t* port, char* buffer, const uint32_t size)
{
  while(!udpClient.parsePacket())
  {
    delay(100);
  }
  udpClient.read(buffer, size);
  strcpy(ip, udpClient.remoteIP().toString().c_str());
  *port = udpClient.remotePort();
}

void sendPacket(const char* ip, const uint32_t port, const char* buffer, const uint32_t size)
{
    udpClient.beginPacket(ip, port);
    udpClient.write(buffer, size);
    udpClient.endPacket();
}
