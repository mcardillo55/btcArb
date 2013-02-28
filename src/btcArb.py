#!/usr/bin/python
import json
import websocket
import urllib2
import socket
import argparse
import time

MTGOX_SOCKET = "ws://websocket.mtgox.com:80"
MTGOX_SOCKET_BACKUP = "ws://socketio.mtgox.com:80/mtgox"
MTGOX_HTTP = "https://mtgox.com/api/1/BTCUSD/ticker"
BITSTAMP_HTTP = "https://www.bitstamp.net/api/ticker/"
TIMEOUT = 10
DEFAULT_REFRESH = 5
MAX_RETRIES = 5

#Initialize record data
maxgain = 0.0
avggain = 0.0
numgains = 0
retries = 0

def print_verbose(text, text_args):
    global verbose
    
    if verbose:
        print text % text_args

def connect_mtgox():
    try:
        print "Connecting to MtGox websocket..."
        sock = websocket.create_connection(MTGOX_SOCKET, TIMEOUT)
    except socket.timeout:
        print "Connection timed out. Trying backup socket..."
        sock = websocket.create_connection(MTGOX_SOCKET_BACKUP, TIMEOUT)
    except websocket.WebSocketException:
        print "Connection FAILED! Reverting to HTTP API"
        return None
    print "Connected!"
    ticker_cmd = "{'op':'mtgox.subscribe', 'type':'ticker'}"
    sock.send(ticker_cmd)
    sock.recv()
    return sock 
    
def get_mtgoxtick(sock):
    try:
        ticker = json.loads(sock.recv())["ticker"]
    except socket.timeout:
        print "Timed out. Retrying"
        return None
    mtdata = (float(ticker['last']['value']), float(ticker['buy']['value']), float(ticker['sell']['value']))
    
    print_verbose("MTGOX: Last: %f Bid: %f Ask: %f", mtdata)

    return mtdata

def get_mtgoxtick_http():
    ticker = json.load(urllib2.urlopen(MTGOX_HTTP))['return']
    mtdata = (float(ticker['last']['value']), float(ticker['buy']['value']), float(ticker['sell']['value']))
    
    print_verbose("MTGOX: Last: %f Bid: %f Ask: %f", mtdata)

    return mtdata

def get_bitstamptick():
    ticker = json.load(urllib2.urlopen(BITSTAMP_HTTP))
    bsdata = (float(ticker['last']), float(ticker['bid']), float(ticker['ask']))
    
    print_verbose("BITSTAMP: Last: %f Bid: %f Ask: %f", bsdata)
    
    return bsdata

def compare_prices(mtdata, bsdata):
    global maxgain
    global avggain
    global numgains

#compare MtGox BID to BitStamp ASK
    if mtdata[1] > bsdata[2]:
        gain = (mtdata[1]/bsdata[2]) - 1
        direction = '>'
    else:
        gain = (bsdata[2]/mtdata[1]) - 1 
        direction = '<'
        
    gain = gain * 100
    if gain > maxgain:
        maxgain = gain
    
    avggain = ((avggain * numgains) + gain) / (numgains + 1)
    numgains += 1

    print "#%d, mtBID: %f %s bsASK: %f, gain: %f, max: %f, avg: %f" % \
          (numgains, mtdata[1], direction, bsdata[2], gain, maxgain, avggain)

#compare MtGox ASK to Bitstamp BID

    if mtdata[2] > bsdata[1]:
        gain = (mtdata[2]/bsdata[1]) - 1
        direction = '>'
    else:
        gain = (bsdata[1]/mtdata[2]) - 1
        direction = '<'

    gain = gain * 100
    if gain > maxgain:
        maxgain = gain
    
    avggain = ((avggain * numgains) + gain) / (numgains + 1)
    numgains += 1

    print "#%d, mtASK: %f %s bsBID: %f, gain: %f, max: %f, avg: %f" % \
          (numgains, mtdata[2], direction, bsdata[1], gain, maxgain, avggain)

def main():
    parser = argparse.ArgumentParser(description='Identify and capitalize on potential Bitcoin arbitrage situations')
    parser.add_argument('-v', action='store_true', help='Print more info to the terminal')
    parser.add_argument('-i', type=int, help='Specify ticker refresh interval in seconds [default = 5]')
    parser.add_argument('--http', action='store_true', help='Force only HTTP API calls')
    args = parser.parse_args()
    verbose = args.v
    force_http = args.http

    if force_http:
        mtgox = None
    else:
        mtgox = connect_mtgox()
        
    if (args.i is not None):
        refresh_int = args.i
    else:
        refresh_int = DEFAULT_REFRESH
        
#Main program loop
    while True:
        if mtgox is not None:
            mtdata = get_mtgoxtick(mtgox)
        else:
            mtdata = get_mtgoxtick_http()
        bsdata = get_bitstamptick()

#mtdata is None on socket timeout
        if mtdata is not None:
            compare_prices(mtdata, bsdata)
            retries = 0
        else:
            retries += 1
            if retries == MAX_RETRIES:
                print "Maximum socket retries reached. Falling back to HTTP mode."
                mtgox = None
        time.sleep(refresh_int)
        
if __name__ == "__main__":
    main()
