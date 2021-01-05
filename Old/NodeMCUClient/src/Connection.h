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

#define SERVER_PORT 5000

void wifiConnect(void);

void receivePacket(char* ip, uint32_t* port, char* buffer, const uint32_t size);

void sendPacket(const char* ip, const uint32_t port, const char* buffer, const uint32_t size);

#endif /* __CONNECTION_H_ */
