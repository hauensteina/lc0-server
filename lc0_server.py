#!/usr/bin/env python

# /********************************************************************
# Filename: leela_server.py
# Author: AHN
# Creation Date: Nov, 2019
# **********************************************************************/
#
# A back end API to run leela and the keras scoring network.
#

from pdb import set_trace as BP
import os, sys, re
import numpy as np
from datetime import datetime
import uuid
from io import BytesIO

import flask
from flask import Flask,jsonify,request,Response,send_file

from lc0_bot import LC0Bot

leela_cmd = './lc0/build/release/lc0'
lc0bot = LC0Bot( leela_cmd.split() )
here = os.path.dirname( __file__)
static_path = os.path.join( here, 'static')
app = Flask( 'lc0_server', static_folder=static_path, static_url_path='/static')

@app.route('/send_cmd', methods=['POST'])
# Send command to the bot and return result
#---------------------------------------------
def send_cmd():
    content = request.json
    resp = lc0bot.send_cmd( content)
    lines = resp.split( '\n')
    return jsonify( {'response':lines})

#----------------------------
if __name__ == '__main__':
    app.run( host='127.0.0.1', port=2718, debug=True)
