# aiwaystoabrpgateway
This is a python Gateway to Read Data from the Aiways API and send it to ABRP and / or Homeassistant

# Getting the needed Data out of the Aiways App
- Source: https://community.home-assistant.io/t/read-aiways-u5-state-of-charge/466441/3

Unfortunately there isn’t an easy way.
Here is, what worked for me. But it is not for the faint hearted:
Use PCAPdroid on Android to capture the communication of the Aiways app. This helper app does NOT require root access.
Activate TLS-Decryption in PCAPdroid and follow the wizard to generate a certificate and install it in Android. The guide (https://emanuele-f.github.io/PCAPdroid/tls_decryption) can help you to test the decryption.
Choose HTTP-Server as traffic dump and the Aiways app as the target app.
Start the dump with the play icon.
Open the Aiways app and navigate to the car data.
Back in PCAPdroid stop the dump and check the registered traffic. There should be a bunch of requests. Most of them contain the header data that you are interested in:
- token
- registerid
- deviceid
- vin
- userId

These can possible expire at any time (though they were stable for me for quite some time now. If they expire you have to capture them again for an update.

# Homeassistant
If the Homeassistant URL and Token is set, the Script will send the following Data to HA entitys
- soc to entity_id='sensor.Aiways_U5_SOC'
- drivingRange to entity_id='sensor.Aiways_U5_RANGE'
- speed to entity_id='sensor.Aiways_U5_SPEED'
- chargeSts to entity_id='sensor.Aiways_U5_Charge_Sts'

# A Better Route Planner
If the ABRP Token is set, the Script will send soc, drivingRange, speed and chargeSts to ABRP.

To get a USER TOKEN from ABRP do the following:
Inside the ABRP (web)app, navigate to your car settings and use the "generic" card (last one at the very bottom) to generate your user token. Make a note of that token and keep it to yourself.

# USAGE:
    
Read Aiways Data and send it to ABRP and/or Homeassistant.

options:

  -h, --help            show this help message and exit
  
  -v VIN, --vin VIN     Your car VIN
  
  -t TOKEN, --token TOKEN
                        Your Aiways token
                        
  -d DEVICEID, --deviceid DEVICEID
                        Your deviceid
                        
  -r REGISTERID, --registerid REGISTERID
                        Your registerid
                        
  -u USERID, --userId USERID
                        Your userId
                        
  -a ABRPTOKEN, --abrptoken ABRPTOKEN
                        Optional: Your ABRP Token
                        
  -g HAURL, --haurl HAURL
                        Optional: Your Homeassistent URL
                        
  -f HATOKEN, --hatoken HATOKEN
                        Optional: Your Homeassistent LONG LIVED ACCESS TOKEN
                        
  -l DEBUGLEVEL, --debuglevel DEBUGLEVEL
                        Debuglevel
# Docker:
There exist a Docker Container 
holtiwilan/aiwaystoabrpgateway:latest

To use the container you have to set the following ENV Variables to pass them to the script:
-VIN
-TOKEN
-DEVICEID
-REGISTERID
-USERID
-ABRPTOKEN (Optional, if not set, nothing will be send to ABRP)
-HAURL (Optional, if not set, nothing will be send to Homeassistent)
-HATOKEN (Optional, if not set, nothing will be send to Homeassistent)
-DEBUGLEVEL
