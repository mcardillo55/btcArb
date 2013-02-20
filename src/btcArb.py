#!/usr/bin/python
import json
import websocket

def connect_mtgox():
    sock = websocket.create_connection("ws://websocket.mtgox.com:80")
    ticker_cmd = "{'op':'mtgox.subscribe', 'type':'ticker'}"
    sock.send(ticker_cmd)
    sock.recv()
    return sock 
    
def get_mtgoxtick(sock):
    ticker = json.loads(sock.recv())["ticker"]
    print "Last: %s Bid: %s Ask: %s" % (ticker['last']['value'], ticker['buy']['value'], ticker['sell']['value']) 
    
mtgox = connect_mtgox()
while 1:
    get_mtgoxtick(mtgox)
