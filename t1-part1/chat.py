from bottle import run, get, post, view, request, redirect, response
import threading
import time
import json

servers = ["localhost:8080"]

messages = [("ADMIN", "Hello guys! feel free to talk about anything! XD")]

@get('/')
@view('index')
def index():
    nick = request.get_cookie('nick')
    if nick:
        return {'messages': messages,'nick': nick}
    else:
	return {'messages': messages,'nick': ''}

@post('/send')
def sendMessage():
    m = request.forms.get('message')
    n = request.get_cookie('nick')
    if not n:
        n = request.forms.get('nick')
        response.set_cookie('nick',n)
    
    messages.append([n, m])
    redirect('/')



run(host='localhost', port=8080)
