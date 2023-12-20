#!/usr/bin/env python

# Script to read data from the Aiways API and send them to ABRP
# Author  : Tim Holzhausen
# Version : 1.2
# Date    : 19.12.2023
# Based on the OpenWB project - https://github.com/snaptec/openWB/blob/master/modules/soc_aiways/aiways_get_soc.py
# Changelog:
# added Homeassistant support
# changed Homeassistant support to publish all data

import requests
import argparse
import json
import logging
import urllib3
import time
import calendar as cal
from datetime import datetime
import os
import sys
from homeassistant_api import Client, State

urllib3.disable_warnings()
CS_URL = "https://coiapp-api-eu.ai-ways.com:10443/"
ABRP_URL = "https://api.iternio.com/1/tlm/send"

ABRP_API_KEY = "8cfc314b-03cd-4efe-ab7d-4431cd8f2e2d"
language = "de"
version = "1.3.0"
platform = "android"
apptimezone = "GMT+02:00"
apptimezoneid = "Europe/Berlin"
#debug = False
debuglevel = 0
vc = ""
waittime= 5 #Time in minutes beween requests


     
#########################################################################
# Send Data to Homeassistent                                            #
#########################################################################
def send_to_homeassistant():
    global vc
    global HA_URL
    global HA_TOKEN

    logger.info("Schreibe nach HA")

    client = Client(HA_URL, HA_TOKEN)
    for (k, v) in vc.items():
        sensorname = "sensor.Aiways_" + vin + "_" + k
        client.set_state(State(state=str(v), entity_id=sensorname))

#########################################################################
# Request "app/vc/getCondition"                                        #
# Get the current Condition of the car                                  #
# The data are located in data/vc                                       #
#########################################################################
def read_from_aiways():    
    global vc
    PATH = "app/vc/getCondition"
    headers = {
        "language": language,
        "registerid": registerid,
        "deviceid": deviceid,
        "version": version,
        "platform": platform,
        "token": token,
        "apptimezone": apptimezone,
        "apptimezoneid": apptimezoneid,
        "content-type": "application/json; charset=utf-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.3.1"
    }

    PAYLOAD = {'userId': userId,'vin': vin}

    resp = requests.post(CS_URL + PATH, headers=headers, data = json.dumps(PAYLOAD),verify=False)
    logger.debug(resp.status_code)
    logger.debug(resp.content)

    data = resp.json()["data"]
    vc = data["vc"]
    logger.info("SoC erfolgreich ermittelt: " + vc["soc"] + "%")

#########################################################################
# Send Data to ABRP                                                    #
#########################################################################
def send_to_abrp():
    global objTLM   
    global vc 
    utc_now = datetime.utcnow()

    objTLM = {
        "utc": cal.timegm(datetime.timetuple(utc_now)),
        "soc": vc["soc"],
        "power": 0,
        "speed": vc["speed"],
        "lat": 0,
        "lon": 0,
        "is_charging": False,
        "est_battery_range": vc["drivingRange"],
        "ext_temp": vc["airconoutsidetemp"]
    }

    if vc["chargeSts"] == 1:
        objTLM["is_charging"] = 1
    else:
        objTLM["is_charging"] = 0

    url = ABRP_URL+"?token=" + ABRP_TOKEN
    headers = {"Authorization": "APIKEY " + ABRP_API_KEY}
    body = {"tlm": objTLM}
    abrp_response = requests.post(url, headers=headers, json=body)

    logger.debug(abrp_response.status_code)
    logger.debug(abrp_response.content)


class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if (
                envvar in os.environ
                and os.environ[envvar]
        ):
            default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Read Aiways Data and send it to ABRP and/or Homeassistant.')
    parser.add_argument('-v', '--vin', help='Your car VIN', required=True, action=EnvDefault, envvar='VIN')
    parser.add_argument('-t', '--token', help='Your Aiways token', required=True, action=EnvDefault, envvar='TOKEN')
    parser.add_argument('-d', '--deviceid', help='Your deviceid', required=True, action=EnvDefault, envvar='DEVICEID')
    parser.add_argument('-r', '--registerid', help='Your registerid', required=True, action=EnvDefault, envvar='REGISTERID')
    parser.add_argument('-u', '--userId', help='Your userId', required=True, action=EnvDefault, envvar='USERID')
    parser.add_argument('-a', '--abrptoken', help='Optional: Your ABRP Token', required=False, action=EnvDefault, envvar='ABRPTOKEN')
    parser.add_argument('-g', '--haurl', help='Optional: Your Homeassistent URL', required=False, action=EnvDefault, envvar='HAURL')
    parser.add_argument('-f', '--hatoken', help='Optional: Your Homeassistent LONG LIVED ACCESS TOKEN', required=False, action=EnvDefault, envvar='HATOKEN')
    parser.add_argument('-l', '--debuglevel', help='Debuglevel', type = int, required=True, action=EnvDefault, envvar='DEBUGLEVEL')
    args = parser.parse_args()
    vin = args.vin
    token = args.token
    deviceid = args.deviceid
    registerid = args.registerid
    userId = args.userId
    debuglevel = args.debuglevel
    HA_URL = args.haurl
    HA_TOKEN = args.hatoken
    ABRP_TOKEN = args.abrptoken
    if debuglevel < 0: logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s', level=logging.DEBUG)
    if debuglevel > 0: logging.basicConfig(filename='aiwaystoabrpgateway.log', format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s', level=logging.DEBUG)
    else: logging.basicConfig(filename='aiwaystoabrpgateway.log', format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s', level=logging.ERROR)
    logger = logging.getLogger("aiways_to_abrp.py")
    
    logger.info("ha url: " + HA_URL)

    while(True):
        read_from_aiways()
        if args.abrptoken is not None:
            send_to_abrp()
        if args.haurl is not None and args.hatoken is not None:
            send_to_homeassistant()            
        time.sleep(waittime * 60)  # Makes Python wait in each iteration