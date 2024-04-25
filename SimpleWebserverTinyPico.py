"""SimpleWebserver, micropython module to aid in setting up simple a
webserver

created Apr 21, 2024
modified Apr 21, 2024
modified Apr 24, 2024 - mods for ESP32 Tiny Pico specific implementation"""

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

import asyncio
import re

class WebServer:

    def __init__(self, varSubstitution = True, debug = False):
        
        self.routeList = {}
        self.varSubstitution = varSubstitution
        self.debug = debug
        self.connectedIPs = []
        
        return
    
    def print_message(self, message):
        """print_message, function to print the past message
        if self.debug = True"""
        
        if self.debug == True:
            print(message)
            
        return

    async def serve_client(self, reader, writer):
        """serve_client, function to process http requests and
        redirect responses to the appropriate functions"""                
        
        # reading in client request data
        clientInfo = reader.get_extra_info("peername")        
        callingIP = clientInfo[0] + ":" + str(clientInfo[1])
        self.connectedIPs.append(callingIP)
        self.print_message(clientInfo)
        self.print_message(" Receiving client data")
        data = b''
        while True:
            line = await reader.readline()
            self.print_message(line)
            data = data + line
            if line == b"\r\n" or line == b"":
                break
    
        # Find http method (GET or POST) and current path to 
        # determine how to process request
        m = re.search("([A-Z]+) (/[A-Za-z0-9\.]*) HTTP", data.decode())    
        # Note using ([A-Z]+) /.* HTTP caused a maximum recursion error
        
        if m != None:
            # use httpMethod and current path to determine how to process data
            httpMethod = m.group(1)
            currentPath = m.group(2)
            self.print_message(f"{httpMethod},{currentPath}")
            
            # check the list (self.routeList) of valid paths
            # ex '/myhomepage' and extract callback functions etc
            currentPathDetails = self.routeList.get(currentPath)        
            if currentPathDetails != None:            
                funct = currentPathDetails.get('callback')
                functArgs = currentPathDetails.get('functArgs')
                if httpMethod == 'POST':
                    # read in additional POST data
                    data = await reader.read(2048)
                    if functArgs != {}:
                        funct(reader, writer, data, **functArgs)
                    else:
                        funct(reader, writer, data)                
                elif httpMethod == 'GET':            
                    if functArgs != {}:
                        funct(reader, writer, **functArgs)
                    else:
                        funct(reader, writer)
            else:
                # send 404 page not found
                currentPathDetails = self.routeList.get("ERROR")
                if currentPathDetails != None:
                    funct = currentPathDetails.get('callback')
                    functArgs = currentPathDetails.get('functArgs')
                    functArgs['errorPath'] = currentPath                    
                    funct(reader, writer, **functArgs)                    
                
        else:
            # send 404 page not found
            currentPathDetails = self.routeList.get("ERROR")
            if currentPathDetails != None:
                funct = currentPathDetails.get('callback')
                functArgs = currentPathDetails.get('functArgs')
                functArgs['errorPath'] = 'Unknown'                    
                funct(reader, writer, **functArgs)
            
        await writer.drain()
        await writer.wait_closed()
        self.connectedIPs.remove(callingIP)
        self.print_message("client disconnected")
        
        return
    
    def route(self, httpMethod, route = '/', callback = None, **kwargs):
        """route, function to put user defined webpage paths, ex '/myhomepage'
        and associated callback functions into a single list of route details. This
        list is used by the serve_client function to determine how to process http requests""" 
        
        self.routeList[route] = {'httpMethod':httpMethod, 'route':route, 'callback':callback, 'functArgs':kwargs}
        
        return
    
    def variable_substitution(self, html, **substituteVars):
        """variable_substitution, function to look for imbedded
        python variables in the HTML data enclosed by {} ex {someVariableName}
        and replace with the values of the those python variables"""
                
        startIndex = 0
        while True:
            m = re.search("{(\w*)}", html[startIndex:]) # \w matches word characters equivalent to [A-Za-z0-9_]
            if m != None:                
                v = m.group(1)
                # check for v in variables collected in substituteVars
                if v in substituteVars:
                    startIndex = startIndex + html[startIndex:].find(m.group(0)) + len(m.group(0))
                    html = html.replace("{" + v + "}", substituteVars.get(v, ''))
                else:
                    # check for v in global variables 
                    if v not in globals():
                        # v not found
                        self.print_message(f"Variable {v} not found")
                    startIndex = startIndex + html[startIndex:].find(m.group(0)) + len(m.group(0))
                    html = html.replace("{" + v + "}", globals().get(v, "{" + v + "}"))                               
            else:
                break
                         
        return html   

    def load_file(self, reader, writer, file = None, response = None, **substituteVars):
        """load_file, function to send the contents of a file (html, js, css) back to 
        the client of the calling http request"""
        
        if response == None:    
            response = "HTTP/1.0 200 OK\r\nServer: uPython on Pi Pico W\r\n\content-Type: text/html\r\n\r\n"              
       
        self.print_message(f"Sending {file} data")              
        # open file (file must be saved on microcontroller)
        with open(file, 'r') as fin:
            fileData = fin.read()
        
        # condition file data via variable_substition 
        if self.varSubstitution == True:
            fileData = self.variable_substitution(fileData, **substituteVars)  
        
        # add filedata to the writer output stream
        writer.write(response)
        writer.write(fileData)        
        # no need to do the writer.drain()/writer.wait_closed() function calls as these
        # are done in the serve_client function        
            
        return
    
