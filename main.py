import requests 
import http.server 
import socketserver

PORT = 8000 

Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("",PORT),Handler) 

print ("Successfully created at PORT", PORT)

#get http requesting from tasking server in config server tasking url /trigger task
r = requests.get('https://swapi.co/api/people/1')

if r.status_code == 200: 
    print ("GET Request from Tasking Server is connected successfully")
    print (r.status_code)
else: 
    print ("Try again!")
    

# function to run josie's code 

# function for sentinel files to be compiled as images 

# function to run hafiz's code 

# function to store in aws database 


httpd.serve_forever()
