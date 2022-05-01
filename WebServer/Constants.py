#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

# None.

####################################
# CONSTANTS
####################################

MODULE_NAME = "EnvMonitor"

USERS_FILE  = "config/users.json"
ENV_FILE    = "config/env_save.db"

ERROR_INCORRECT_CRED_CODE        = 1
ERROR_UNAUTHORIZED_CODE          = 2
ERROR_CANNOT_LOAD_ENV_FILE_CODE  = 3
ERROR_CANNOT_SAVE_ENV_FILE_CODE  = 4
ERROR_CANNOT_LOAD_USER_FILE_CODE = 5
ERROR_API_KEY_DUPLICATE          = 6
ERROR_INVALID_API_KEY_CODE       = 7

ERROR_UNKNOWN_CODE               = 255

ERROR_INCORRECT_CRED_MSG    = "Incorrect password or username not found."
ERROR_UNAUTHORIZED_MSG      = "Unauthorized action."
ERROR_CANNOT_LOAD_ENV_FILE  = "Could not open environment save file."
ERROR_CANNOT_SAVE_ENV_FILE  = "Could not save environment save file."
ERROR_CANNOT_LOAD_USER_FILE = "Could not open users files."
ERROR_API_KEY_DUPLICATE     = "Duplicate users API key."
ERROR_INVALID_API_KEY       = "Invalid API key."

ERROR_UNKNOWN               = "Unknown error."

WARNING_NOT_INIT                = "Not initialized."
WARNING_STOP_NONEXISTANT_THREAD = "Tried to stop a non-existant thread."
WARNING_SAMPLE_COUNT_MISSMATCH  = "Sample count missmatch."

INFO_CREATED_ENV_FILE   = "Created environment file."
INFO_LOADED_ENV_FILE    = "Loaded environment file."
INFO_SAVED_ENV_FILE     = "Saved environment file."
INFO_WAITING_FOR_THREAD = "Waiting for environment thread to terminate."
INFO_REQUESTING_NODE    = "Requesting data from environment node."
INFO_REQUESTING_NODE_OK = "Request accepted."
INFO_LOADED_USERS       = "Loaded users."

####################################
# GLOBAL VARIABLES
####################################

# None.

####################################
# FUNCTIONS
####################################

# None.

####################################
# MAIN
####################################

# None.

################################################################################
# EOF