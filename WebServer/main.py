#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import hashlib
import uuid
import flask_login
import DataBase

from datetime import datetime
from flask import Flask, request, render_template, jsonify, redirect, url_for


class User(flask_login.UserMixin):
    pass

####################################
# CONSTANTS
####################################

USERS_FILE = "config/users.json"

ERROR_INCORRECT_CRED_CODE = 1
ERROR_UNAUTHORIZED_CODE   = 2

ERROR_INCORRECT_CRED_MSG = "Incorrect password or username not found."
ERROR_UNAUTHORIZED_MSG   = "Unauthorized action."
####################################
# SERVER STATE VARIALBES
####################################

# We have to keep the Flask servAPP as global var
servApp   = Flask(__name__)
servLogin = flask_login.LoginManager()

####################################
# FUNCTIONS
####################################

@servLogin.user_loader
def user_loader(username):
    return DataBase.getUserByUsername(username)

@servLogin.request_loader
def request_loader(request):
    username = request.form.get("username")
    return DataBase.getUserByUsername(username)

####################################
# ROUTES
####################################

@servApp.route('/')
@servApp.route('/login')
def indexId():
    return render_template("index.html")

@servApp.route('/dash')
@flask_login.login_required
def dashboardRoute():
    return render_template("dashboard.html")

@servApp.route('/profile')
@flask_login.login_required
def profileRoute():
    return render_template("profile.html")

@servApp.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for("indexId"))

@servApp.route('/tryLogin')
@flask_login.login_required
def tryLogin():
    return jsonify(error=0)


####################################
# API
####################################
@servApp.route('/doLogin/', methods = ["POST"])
def doLogin():
    if request.method == "POST":
        username = request.form["username"]
        passwd   = request.form["passwd"]

        user = DataBase.getUserByUsername(username)
        if(user == None):
            return jsonify(error=ERROR_INCORRECT_CRED_CODE, message=ERROR_INCORRECT_CRED_MSG)

        # Hash given password
        strToHash = username + passwd + str(user.regtime)
        hash = hashlib.sha256(strToHash.encode("utf-8"))
        if hash.hexdigest() == user.password:
            # Add user to session and redirect to dashboard
            flask_login.login_user(user)
            return jsonify(error=0)
        else:
            return jsonify(error=ERROR_INCORRECT_CRED_CODE, message=ERROR_INCORRECT_CRED_MSG)
    else:
        print("Accessed doLogin with incorrect method.")
        return jsonify(error=ERROR_UNAUTHORIZED_CODE, message=ERROR_UNAUTHORIZED_MSG)


@servLogin.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("indexId"))

####################################
# MAIN
####################################

if __name__ == '__main__':
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    DataBase.loadUsers()

    servApp.secret_key = uuid.uuid4().hex

    servLogin.init_app(servApp)
    servApp.run(debug=True, host='0.0.0.0')