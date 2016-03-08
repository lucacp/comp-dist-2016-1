from bottle import run, get, post, view, request, redirect, response
import thread
import threading
import time
import json

servers = ["localhost:8080"]

messages = [("ADMIN", "Hello guys! feel free to talk about anything! XD")]

@get('/')
@view('index')
def index():
    nick = request.query('nick')
    if nick:
        return {'messages': messages,'nick': nick}
    else:
	return {'messages': messages,'nick': ''}

@post('/send')
def sendMessage():
    m = request.forms.get('message')
    n = request.query('nick')
    if not n:
        n = request.forms.get('nick')
		response.query('nick',n)
    messages.append([n, m])
    redirect('/')

@get('/peers')
def getPeers():
	global servers
	redirect('/')
	
	
threading.Thread(target=run,kwargs=dict(host='localhost', port=8080)).start()
