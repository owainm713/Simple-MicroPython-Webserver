# Simple-MicroPython-Webserver
MicroPython module to aid in setting up a simple webserver. Testing was done on
a Raspberry Pi Pico W.

This module allows the use of separate HTML, JavaScript and CSS files. This module
also provides for a means to embed variables into the separate files in format of
{someVariable}.  Currently only GET and POST requests are supported.

For sample usage see the the example files. To run the example files, load the
following files onto your microcontroller; SimpleWebserver.py, exampleJS.js,
exampleCSS.css, errorTemplate.html. Also save as main.py the exampleWebserver.py file,
you will need to change the SSID and passwd fields to connect to your wifi.
For the example, also connect 2 LEDs (with current limiting resistors) to your microcontroller,
I used pins 19 and 20 on my Pi Pico W.

Created Apr 21, 2024
Modified Apr 21, 2024
