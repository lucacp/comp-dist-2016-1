from bottle import run, get, post, view, request, redirect
import thread
import threading
import time
import json

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
	return servers

@post('/peers/add')
def addPeer():
	s = request.forms.get('servers')
	servers.append(s)
	redirect('/?nick='+request.query.nick)
	

threading.Thread(target=run,kwargs=dict(host='localhost', port=8080)).start()
