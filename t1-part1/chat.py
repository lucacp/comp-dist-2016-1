from bottle import run, get, post, view, request, redirect
import thread
import threading
import time
import json

servers = ["localhost:8080"]
messages = [("Nobody", "Hello guys!")]
nick = ["Nobody"]
@get('/')
@view('index')
def index():
    nick = request.query.nick
    if nick:
        return {'messages': messages,'nick': nick}
    else:
		return {'messages': messages,'nick': ''}
@post('/send')
def sendMessage():
	global nick
	m=request.forms.get('message')
	n=request.forms.get('nick')
	if n is not in nick:
		nick.append(n)
	messages.append([n, m])
	redirect('/?nick='+n)

@get('/peers')
def getPeers():
	return servers

@post('/peers/add')
def addPeer():
	s = request.forms.get('servers')
	servers.append(s)
	redirect('/?nick='+request.query.nick)
	

threading.Thread(target=run,kwargs=dict(host='localhost', port=8080)).start()
