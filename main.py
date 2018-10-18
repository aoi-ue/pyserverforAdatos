from bottle import run, get, post, request 
import json

data = json.load(open('json_tasking_input.json', 'r'))

# Get Specific Scripts from S3 Based on the tasking_server's analysis key 
@get('/tasking')
def getAll():
	return {'data': data}


@post('/tasking')
def inputNew(): 
	new_request= {'data' : ''}
	data.append(new_request)
	return {'data' : data}


# Run and Async Josie's Script 

# Run Hafiz's Script 

# Error Handler to end script and notify josie & hafiz 

# Post to AWS Script 

# Post to mapping_server

# python SMTP to client 


run(host='localhost', port=8000, reloader=True, debug=True)