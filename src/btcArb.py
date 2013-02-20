#!/usr/bin/python
import json
import websocket

mtgox = websocket.create_connection("ws://websocket.mtgox.com:80")
ticker_cmd = "{'op':'mtgox.subscribe', 'type':'ticker'}"
mtgox.send(ticker_cmd)
mtgox.recv()
while 1:
    ticker = json.loads(mtgox.recv())["ticker"]
    print "Last: %s Bid: %s Ask: %s" % (ticker['last']['value'], ticker['buy']['value'], ticker['sell']['value']) 
