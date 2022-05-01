#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

from colorama import Fore, Back, Style, init

####################################
# CONSTANTS
####################################

# None

####################################
# GLOBAL VARIABLES
####################################

isInit = False

####################################
# FUNCTIONS
####################################

def formatLog(module, message, errorCode, style):
    global isInit

    # Init colorama is needed
    if not isInit:
        init()
        isInit = True

    print(style, end = "")
    if(module is not None and len(module) != 0):
        print("[" + module + "] ", end = "")

    if(message is not None and len(message) != 0):
        print(message, end = "")
    else:
        print("No message provided.", end = "")

    if(errorCode is not None):
        print(" | " + str(errorCode), end = "")

    # Last endline
    print(Fore.RESET + Style.RESET_ALL)


def LOG_ERROR(module, message, errorCode, terminate):
    formatLog(module, message, errorCode, Fore.RED + Style.BRIGHT)

    if terminate:
        exit(errorCode)

def LOG_WARNING(module, message, errorCode):
    formatLog(module, message, errorCode, Fore.YELLOW + Style.BRIGHT)

def LOG_INFO(module, message):
    formatLog(module, message, None, Fore.CYAN + Style.BRIGHT)

def LOG_SUCCESS(module, message):
    formatLog(module, message, None, Fore.GREEN + Style.BRIGHT)

def LOG_DEBUG(module, message, terminate):
    formatLog(module, message, None, Fore.YELLOW + Style.BRIGHT)

    if terminate:
        exit(errorCode)


####################################
# MAIN
####################################

if __name__ == '__main__':
    LOG_ERROR("TEST_MOD", "This is an error test", 12, 0);
    LOG_WARNING("TEST_MOD", "This is a warning test", 12);
    LOG_INFO("TEST_MOD", "This is an info test");
    LOG_SUCCESS("TEST_MOD", "This is a success test");
    LOG_DEBUG("TEST_MOD", "This is a debug test", 0);
    print("This is a test print")

################################################################################
# EOF