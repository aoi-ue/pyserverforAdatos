from bottle import run, get, post, request

animals = [{'name' : 'Ellie', 'type' : 'Elephant'},
			{'name' : 'Python', 'type' : 'Snake'},
			{'name' : 'Zed', 'type' : 'Zebra'}]

@get('/animal')
def getAll():
	return {'animals' : animals}

@get('/animal/<name>')
def getOne(name):
	the_animal = [animal for animal in animals if animal['name'] == name]
	return {'animal' : the_animal[0]}

@post('/animal')
def addOne():
	new_animal = {'name' : request.json.get('name'), 'type' : request.json.get('type')}
	animals.append(new_animal)
	return {'animals' : animals}



run(host='localhost', port=8000, reloader=True, debug=True)