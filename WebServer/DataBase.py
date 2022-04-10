#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import flask_login


class User(flask_login.UserMixin):
    pass

####################################
# CONSTANTS
####################################

DB_FILE = "config/users.json"

####################################
# DATABASE STATE VARIALBES
####################################

users  = {}
emails = {}

####################################
# FUNCTIONS
####################################

def loadUsers():
    global users
    # Open JSON user file and load the JSON disctionary
    with open(DB_FILE) as usersRaw:
        data  = json.load(usersRaw)
        users  = data["users"]
        emails = data["emails"]

def getUserByEmail(email):
    if email in emails:
        if emails[email] not in users:
            raise RuntimeError("Emails and users database do not match.")

        username = emails[email]
        userData = users[username]

        user          = User();
        user.id       = username
        user.email    = email
        user.regtime  = userData["reg_time"]
        user.password = userData["password"]
        user.level    = userData["level"]

        return user
    else:
        return None

def getUserByUsername(username):
    if username in users:
        userData = users[username]

        user          = User();
        user.id       = username
        user.email    = userData["email"]
        user.regtime  = userData["reg_time"]
        user.password = userData["password"]
        user.level    = userData["level"]

        return user
    else:
        return None