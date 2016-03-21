from bottle import run, get, post, view, request, redirect
import threading
import time
import json
import requests
servers = ["http://localhost:8080"]
messages = [("Nobody", "Hello guys!")]
@get('/')
@view('index')
def index():
    return {'messages': messages,'nick': ''}

@get('/<nick>')
@view('index')
def index(nick):
	return {'messages': messages,'nick': nick}

@post('/send')
def sendMessage():
	m=request.forms.get('message')
	n=request.forms.get('nick')	
	messages.append([n, m])
	redirect('/'+n)

@get('/peers')
def getPeers():
	global servers
	return json.dumps(servers)	
		
@get('/peers/msg')
def getMsg():
	global messages
	return json.dumps(messages)
	
def clientServ():
	while True:
		time.sleep(2)
		print ('ola!')
		global servers
		for i in servers:
			s = requests.get(i+'/peers')
			ns = json.loads(s.content.decode("UTF-8"))
			for j in ns:
				if ns not in servers:
					servers.append(j)

def clientMsg():
	while True:
		global messages
		global servers
		for i in servers:
			time.sleep(5)
			s = requests.get(i+'/peers/msg')
			ns = json.loads(s.content.decode("UTF-8"))
			if ns not in messages:
				messages=ns
				
	
threading.Thread(target=clientServ).start()

threading.Thread(target=clientMsg).start()
	
threading.Thread(target=run,kwargs=dict(host='localhost', port=8080)).start()


