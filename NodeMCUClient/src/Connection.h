/**
 * UDP Connection manager.
 * 
 * Developped for the DomoHome projet.
 * 
 * Copyright Alexy Torres Aurora Dugo
 */
#ifndef __CONNECTION_H_
#define __CONNECTION_H_

#define NET_SSID "DomoDev"
#define NET_PASS "DomohomeDev"

#define SERVER_IP   "192.168.0.106"
#define SERVER_PORT 62276

void wifiConnect(void);

void receivePacket(char* buffer, const uint32_t size);

void sendPacket(const char* buffer, const uint32_t size);
#endif /* __CONNECTION_H_ */
