from bottle import run, get, post, view, request, redirect
import thread
import threading
import time
import json
nserver = 0
servers = ["localhost:8080"]
messages = [("Nobody", "Hello guys!")]
nick = 'Nobody'
@get('/')
@view('index')
def index():
    return {'messages': messages,'nick': nick}

@get('/<nick>')
@view('index')
def index(nick):
    return {'messages': messages,'nick': nick}

@post('/send')
def sendMessage():
	global nick
	m=request.forms.get('message')
	n=request.forms.get('nick')
	if n is not in nick:
		nick.append(n)
	messages.append([n, m])
	redirect('/'+n)

@get('/peers')
def getPeers():
	global servers
	return servers

@post('/peers/add')
def addPeer():
	global nserver
	global servers
	for i range (0,nserver)
		s = request.(servers[i]+'/peers')
		if s not in servers
			servers.insert(s)
	redirect('/')
	

threading.Thread(target=run,kwargs=dict(host='localhost', port=8080)).start()
