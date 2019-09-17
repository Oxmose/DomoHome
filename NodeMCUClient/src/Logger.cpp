#include <Arduino.h>

#include "Logger.h"

void Logger::logInit(void) 
{
    Serial.begin(9600);
    while(!Serial);
}
void Logger::logInfo(const char* msg) 
{
    Serial.print("[");
    Serial.print(millis());
    Serial.print("]");
    Serial.print("[INFO]");

    Serial.println(msg);
    Serial.flush();
}
void Logger::logWarning(const char* msg) 
{
    Serial.print("[");
    Serial.print(millis());
    Serial.print("]");
    Serial.print("[WARNING]");

    Serial.println(msg);
    Serial.flush();
}
void Logger::logError(const char* msg) 
{
    Serial.print("[");
    Serial.print(millis());
    Serial.print("]");
    Serial.print("[ERROR]");

    Serial.println(msg);
    Serial.flush();
}