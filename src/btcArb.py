#!/usr/bin/python
import json
import websocket
import urllib2

def connect_mtgox():
    sock = websocket.create_connection("ws://websocket.mtgox.com:80")
    ticker_cmd = "{'op':'mtgox.subscribe', 'type':'ticker'}"
    sock.send(ticker_cmd)
    sock.recv()
    return sock 
    
def get_mtgoxtick(sock):
    ticker = json.loads(sock.recv())["ticker"]
    print "MTGOX: Last: %s Bid: %s Ask: %s" % (ticker['last']['value'], ticker['buy']['value'], ticker['sell']['value']) 

def get_bitstamp():
    ticker = json.load(urllib2.urlopen("https://www.bitstamp.net/api/ticker/"))
    print "BITSTAMP: Last: %s Bid: %s Ask: %s" % (ticker['last'], ticker['bid'], ticker['ask'])
    
mtgox = connect_mtgox()
while 1:
    get_mtgoxtick(mtgox)
    get_bitstamp()
