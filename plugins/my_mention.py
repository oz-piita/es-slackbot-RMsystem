from slackbot.bot import respond_to

import my_input as ip
import my_calc as cl

@respond_to('d1')
def d1respond(message):
    text = solver('d1')
    message.send(text)

@respond_to('d2')
def d2respond(message):
    text = solver('d2')
    message.send(text)

@respond_to('d3')
def d3respond(message):
    text = solver('d3')
    message.send(text)

@respond_to('d4')
def d4respond(message):
    text = solver('d4')
    message.send(text)

@respond_to('d5')
def d5respond(message):
    text = solver('d5')
    message.send(text)

@respond_to('d6')
def d6respond(message):
    text = solver('d6')
    message.send(text)

@respond_to('d7')
def d7respond(message):
    text = solver('d7')
    message.send(text)

def solver(id):
    k = cl.Param(*ip.readsheet(id)) # *はタプルを展開する演算子オーバーロード.Pythonでの多値返却はタプルで返ってくる.
    message = k.Calc()
    return message
