#include <Arduino.h>

#include "Logger.h"

void logInit(void) 
{
    Serial.begin(9600);
    while(!Serial);
}
void logInfo(const char* msg) 
{
    Serial.print("[");
    Serial.print(millis());
    Serial.print("]");
    Serial.print("[INFO]");

    Serial.println(msg);
    Serial.flush();
}
void logWarning(const char* msg) 
{
    Serial.print("[");
    Serial.print(millis());
    Serial.print("]");
    Serial.print("[WARNING]");

    Serial.println(msg);
    Serial.flush();
}
void logError(const char* msg) 
{
    Serial.print("[");
    Serial.print(millis());
    Serial.print("]");
    Serial.print("[ERROR]");

    Serial.println(msg);
    Serial.flush();
}