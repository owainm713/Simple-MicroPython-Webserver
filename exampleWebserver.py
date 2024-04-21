"""exampleWebserver, program to demonstrate the use of the SimpleWebserver
micropython module

created Apr 21, 2024
modified Apr 21, 2024"""

"""
Copyright 2024 Owain Martin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import machine
import network
import asyncio
import utime as time
import re
import json
import SimpleWebserver

def setup_wifi(ssid, passwd = None):
    
    global wlan
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        if passwd == None:
            passwd = input('Enter password: ')
        wlan.connect(ssid, passwd)

        # wait for connect
        print('Connecting.', end = '')
        maxWait = 10
        while maxWait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            maxWait -= 1
            print('.', end = '')
            time.sleep(1)
        
    if wlan.status() != 3:
        raise RuntimeError('network conection failed')
    else:
        onboard_led.value(1)
        print('connected')
        status = wlan.ifconfig()        
        print('ip = ' + status[0])
        
    return status[0]

def disconnect_wifi():
    
    wlan.disconnect()
    while wlan.status() == 3:
        time.sleep(0.5)
    onboard_led.value(0)
    print('Disconnected ' + str(wlan.status()))
    
    return
    
def home_page(reader, writer, file):
    """home_page, function to load the home page"""
        
    print("Sending homepage data")
    
    # setting blink status variables
    if blinkStatus == 'ON':
        blinkCheckedOn = 'checked="checked"'
        blinkCheckedOff = ''
    else:            
        blinkCheckedOn = ''
        blinkCheckedOff = 'checked="checked"'
        
    # set up calling IP text
    callingIP = ':'
    if len(webserver.connectedIPs) != 0:
        for ip in webserver.connectedIPs:
            callingIP = callingIP + ', ' + ip
        
    webserver.load_file(reader, writer, file, LEDStatus=LEDStatus, blinkCheckedOn=blinkCheckedOn,
                        blinkCheckedOff=blinkCheckedOff, callingIP = callingIP)
            
    return
    
def error_page(reader, writer, file, errorPath):
    """error_page, function to load the error page"""        
        
    print("Sending  error page data")        
    response = "HTTP/1.0 404 PAGE NOT FOUND\r\nServer: uPython on Pi Pico W\r\n\content-Type: text/html\r\n\r\n"
    errorText = "PAGE NOT FOUND: " + errorPath 
        
    webserver.load_file(reader, writer, file, error="404", errorText=errorText)
            
    return
    
def toggle_led(reader, writer, postData = None):
    """toggle_led, function to toggle led1 when the
    LED toggle button on the webpage is pressed. Button pressed
    processed by javascript code which generates an XML request"""
    
    global LEDStatus         
        
    response = "HTTP/1.0 200 OK\r\nServer: uPython on Pi Pico W\r\n\content-Type: text/html\r\n\r\n"       
        
    data = json.loads(postData) 
    print(f"data['mode']: {data['mode']}")
    print("Toggle LED via toggle_led function")
    led1.toggle()
    if led1.value() == 1:
        LEDStatus = "ON"
    else:
        LEDStatus = "OFF"
    xmlResponse = json.dumps({'buttonUpdate':'true','LEDStatus':LEDStatus}, separators=(',',':'))
    writer.write(response)
    writer.write(xmlResponse)
        
    return
    
def set_blink_LED(reader, writer, postData = None):
    """set_blink_led, function to enable or disable the blinking
    of led2 when the Status LED webpage form is submitted
    """
    
    global blinkStatus      
        
    print(postData)
        
    if postData != None:                
        m = re.search("blinkStatus=([A-Za-z]*)",postData.decode())
        if m != None:
            if m.groups()[0] == "ON":
                blinkStatus = 'ON'                
            else:
                blinkStatus = 'OFF'                
        else:
            print("Blink status not found")
        
    home_page(reader, writer, file='example.html')
    
    return
    
# set up onboard LED
onboard_led = machine.Pin("LED", machine.Pin.OUT) # Pi Pico W
onboard_led.value(0)

# set up Red and Green LEDs
led1 = machine.Pin(20, machine.Pin.OUT)
led1.value(0)

led2 = machine.Pin(19, machine.Pin.OUT)
led2.value(0)    
    
ssid = "YourWifiName" # change to the SSID of the wifi network you want to connect to
passwd = "YourWifiPassword" # change to the wifi password, if None you will be prompted to enter one
LEDStatus = "OFF"
blinkStatus = "ON"   
    
webserver = SimpleWebserver.WebServer(varSubstitution = True, debug = False)
webserver.route(httpMethod = 'GET', route = '/', callback = home_page, file = 'example.html')
webserver.route('GET', '/exampleJS.js', webserver.load_file, file = 'exampleJS.js')
webserver.route('GET', '/exampleCSS.css', webserver.load_file, file = 'exampleCSS.css')
webserver.route('POST', '/ledToggle', toggle_led)
webserver.route('POST', '/StatusLEDControl', set_blink_LED)
webserver.route('ERROR', 'ERROR', error_page, file = 'errorTemplate.html')

async def main():
        
    global ipAddr 
        
    # set up wifi connection
    ipAddr = setup_wifi(ssid, passwd)    
        
    # set up webserver
    print("setting up webserver")
    asyncio.create_task(asyncio.start_server(webserver.serve_client, "0.0.0.0", 80)) # simple webpage
            
    while True:
            
        # area to do other non webserver tasks
        
        if blinkStatus == 'ON': 
            led2.on()
            await asyncio.sleep(0.5)
            led2.off()
            await asyncio.sleep(2)
        else:
            await asyncio.sleep(0.5)
            
    return

try:
    asyncio.run(main())
        
finally:
    print("doing finally statement")
    asyncio.new_event_loop()
    

        

    
    