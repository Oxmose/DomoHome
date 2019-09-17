#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

from flask     import Flask, request, render_template
from flask_api import status

####################################
# SERVER STATE VARIALBES
####################################

# We have to keep the Flask servAPP as global var
servApp = Flask(__name__)

####################################
# ROUTES
####################################

@servApp.route('/', defaults={'objid': 3})
@servApp.route('/<int:objid>')
def indexId(objid=3):
    return render_template("index.html", objId=objid)


####################################
# MAIN
####################################
if __name__ == '__main__': 
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    servApp.run(debug=True, host='0.0.0.0')