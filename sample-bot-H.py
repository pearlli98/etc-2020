#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="ALMONDPUDDING"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

market_vals = {"BOND":{"highbuy":0, "lowsell":0, "market":0},
            "VALBZ":{"highbuy":0, "lowsell":0, "market":0},
            "VALE":{"highbuy":0, "lowsell":0, "market":0},
            "GS":{"highbuy":0, "lowsell":0, "market":0},
            "MS":{"highbuy":0, "lowsell":0, "market":0},
            "WFC":{"highbuy":0, "lowsell":0, "market":0},
            "XLF":{"highbuy":0, "lowsell":0, "market":0}}

def log_vals(marketobj):
    mtype = marketobj["symbol"] # the market type
    #mprice = marketobj["price"] # price

    # Check for buys and sells
    if "buy" in marketobj:
        border=marketobj["buy"]
        for item in border:
            price = item[0]
            if price > market_vals[mtype]["highbuy"]:
                market_vals[mtype]["highbuy"] = price
                market_vals[mtype]["market"] = (market_vals[mtype]["highbuy"] + market_vals[mtype]["lowsell"]) / 2

    if "sell" in marketobj:
        sorder=marketobj["sell"]
        for item in sorder:
            price = item[0]
            if price < market_vals[mtype]["lowsell"]:
                market_vals[mtype]["lowsell"] = price
                market_vals[mtype]["market"] = (market_vals[mtype]["highbuy"] + market_vals[mtype]["lowsell"]) / 2 
    
# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    #sell_bond={"type":"add", "order_id":0, "symbol":"BOND", "dir":"SELL", "price":1001,"size":1}
    #write_to_exchange(exchange, sell_bond)
    #hello_from_exchange = read_from_exchange(exchange)
    log = read_from_exchange(exchange)
    while log: 
        # A common mistake people make is to call write_to_exchange() > 1
        # time for every read_from_exchange() response.
        # Since many write messages generate marketdata, this will cause an
        # exponential explosion in pending messages. Please, don't do that!
        print("The exchange replied:", log, file=sys.stderr)
        if log["type"] == "book":
            log_vals(log)
            print('The current market value for ' + log["symbol"] + ' is ' + str(market_vals[log["symbol"]]["market"]))

        #log_vals(log)
        print("-------------ONE LOOP COMPLETED-----------------")
        log = read_from_exchange(exchange)
        #print('The current market value for ' + log["symbol"] + ' is ' + market_vals[log["symbol"]]["market"])

        


# need one function to determine the fair price, fair value 
# need to calculate a fair value for each security
# calculate and holds the fair value for each security


# need to keep track of the best bid
# need to keep track of the best offer

if __name__ == "__main__":
    main()


