#ifndef __LOGGER_H_
#define __LOGGER_H_

class Logger 
{
    private:
    public:
        static void logInit(void);
        static void logInfo(const char* msg);
        static void logWarning(const char* msg);
        static void logError(const char* msg);
};

#endif /* #ifndef __LOGGER_H_ */