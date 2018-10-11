import http.server 
import socketserver
import requests 

PORT = 8000 

Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("",PORT),Handler) 

print ("Successfully created at PORT", PORT)

# placeholder for tasking_server in config server tasking url /trigger task
r = requests.get('https://swapi.co/api/people/1')
data = r.json() 

if r.status_code == 200: 
    print ("GET Request from Tasking Server is connected successfully")
else: 
    print ("Try again!")


# pass r.request into function to run josie's code
def josie(): 
    print (data['name'])

josie()

# library built in for sentinel files to be compiled as images 


# function to run hafiz's code 

# function to store in aws database 


httpd.serve_forever()
