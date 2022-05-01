#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import flask_login
import Constants
import Logger

class User(flask_login.UserMixin):
    pass

####################################
# CONSTANTS
####################################

MODULE_NAME = "USER_DB"

####################################
# GLOBAL VARIABLES
####################################

users   = {}
emails  = {}
apiKeys = {}

####################################
# FUNCTIONS
####################################

def loadUsers():
    global emails
    global users
    global apiKeys

    # Open JSON user file and load the JSON dictionary
    try:
        usersRaw = open(Constants.USERS_FILE, "r")
        data  = json.load(usersRaw)
        users  = data["users"]
        emails = data["emails"]

        # Load the API keys
        for username, user in users.items():
            if user["api_key"] in apiKeys:
                Logger.LOG_ERROR(MODULE_NAME, Constants.ERROR_API_KEY_DUPLICATE,
                                 Constants.ERROR_API_KEY_DUPLICATE_CODE, True)
            apiKeys[user["api_key"]] = username

        Logger.LOG_SUCCESS(MODULE_NAME, Constants.INFO_LOADED_USERS)
    except OSError as exc:
        Logger.LOG_ERROR(MODULE_NAME, Constants.ERROR_CANNOT_LOAD_USER_FILE + " " + str(exc),
                            Constants.ERROR_CANNOT_LOAD_USER_FILE_CODE, True)
    except Exception as exc:
        Logger.LOG_ERROR(MODULE_NAME, Constants.ERROR_UNKNOWN + " " + str(exc),
                            Constants.ERROR_UNKNOWN_CODE, False)

def getUserByEmail(email):
    if email in emails:
        if emails[email] not in users:
            raise RuntimeError("Emails and users database do not match.")

        username = emails[email]
        userData = users[username]

        user               = User();
        user.id            = username
        user.email         = email
        user.regtime       = userData["reg_time"]
        user.password      = userData["password"]
        user.level         = userData["level"]
        user.serverApiKey  = userData["api_key"]
        user.weatherApiKey = userData["weather_api_key"]

        return user
    else:
        return None

def getUserByUsername(username):
    if username in users:
        userData = users[username]

        user               = User();
        user.id            = username
        user.email         = userData["email"]
        user.regtime       = userData["reg_time"]
        user.password      = userData["password"]
        user.level         = userData["level"]
        user.serverApiKey  = userData["api_key"]
        user.weatherApiKey = userData["weather_api_key"]

        return user
    else:
        return None

def checkApiKey(apiKey):
    global apiKeys

    return apiKey in apiKeys
################################################################################
# EOF