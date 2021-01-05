#ifndef __LOGGER_H_
#define __LOGGER_H_

void logInit(void);
void logInfo(const char* msg);
void logWarning(const char* msg);
void logError(const char* msg);

#endif /* #ifndef __LOGGER_H_ */