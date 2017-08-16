#!/usr/bin/env python
__author__ = 'chase.ufkes'

import time
import json
from modules import bittrex
from modules import orderUtil
from modules import buyUtil
from modules import sellUtil

with open("config/botConfig.json", "r") as fin:
    config = json.load(fin)

apiKey = str(config['apiKey'])
apiSecret = str(config['apiSecret'])
trade = config['trade']
currency = config['currency']
sellValuePercent = config.get('sellValuePercent', 0)
sellVolumePercent = config.get('sellVolumePercent', 0)
buyValuePercent = config.get('buyValuePercent', 0)
buyVolumePercent = config.get('buyVolumePercent', 0)
extCoinBalance = config['extCoinBalance']
checkInterval = config['checkInterval']


if (sellValuePercent == 0) or (sellVolumePercent == 0):
    blockSell = 'true'
else:
    blockSell = 'false'

if (buyValuePercent == 0) or (buyVolumePercent == 0):
    blockBuy = 'true'
else:
    blockBuy = 'false'

api = bittrex.bittrex(apiKey, apiSecret)
market = '{0}-{1}'.format(trade, currency)

def control_sell_orders(orderInventory):
    orders = sellUtil.sellNumber(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        sellUtil.cancelOrder(orderInventory, orders, apiKey, apiSecret)
    else:
        return 0

def control_buy_orders(orderInventory):
    orders = buyUtil.buyNumber(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        buyUtil.cancelOrder(orderInventory, orders, apiKey, apiSecret)
    else:
        return 0

def set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, currentValue):
    newBuyValue = buyUtil.defBuyValue(currentValue, buyValuePercent)
    newBuyVolume = buyUtil.defBuyVolume(orderVolume, buyVolumePercent)
    result = api.buylimit(market, newBuyVolume, newBuyValue)
    print result

def set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, currentValue):
    newSellValue = sellUtil.defSellValue(currentValue, sellValuePercent)
    newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent)
    result = api.selllimit(market, newSellVolume, newSellValue)
    print result


#setting buy / sells during startup to avoid crap selling
currentValue = orderUtil.initialMarketValue(market, apiKey, apiSecret)
orderInventory = orderUtil.orders(market, apiKey, apiSecret) #prepare to reset orders
orderUtil.resetOrders(orderInventory, apiKey, apiSecret)
orderVolume = api.getbalance(currency)['Available'] + extCoinBalance
if blockBuy == 'false':
    set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, currentValue)
if blockSell == 'false':
    set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, currentValue)
time.sleep(2)

while True:
    orderInventory = orderUtil.orders(market, apiKey, apiSecret)
    orderUtil.recentTransaction(market, orderInventory, apiKey, apiSecret, checkInterval)
    orderInventory = orderUtil.orders(market, apiKey, apiSecret)
    if blockSell == 'false':
        sellControl = control_sell_orders(orderInventory)
        if (sellControl == 0):
            newSellValue = sellUtil.defSellValue(orderValueHistory, sellValuePercent)
            newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent)
            print "Currency: " + currency
            print "Sell Value: " + str(newSellValue)
            print "Sell volume: " + str(newSellVolume)
            result = api.selllimit(market, newSellVolume, newSellValue)
            print result

    orderValueHistory = orderUtil.lastOrderValue(market, apiKey, apiSecret)
    orderVolume = api.getbalance(currency)['Available'] + extCoinBalance


    if blockBuy == 'false':
        buyControl = control_buy_orders(orderInventory)
        if (buyControl == 0):
            newBuyValue = buyUtil.defBuyValue(orderValueHistory, buyValuePercent)
            newBuyVolume = buyUtil.defBuyVolume(orderVolume, buyVolumePercent)
            print "Currency: " + currency
            print "Buy Value: " + str(newBuyValue)
            print "Buy Volume: " + str(newBuyVolume)
            result = api.buylimit(market, newBuyVolume, newBuyValue)
            print result
    time.sleep(checkInterval)