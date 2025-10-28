import asyncio
import json
import websockets
from google.protobuf.json_format import MessageToDict
import PushDataV3ApiWrapper_pb2
from datetime import datetime
from collections import defaultdict
from tvDatafeed import TvDatafeed, Interval
tv = TvDatafeed()
import os
import ta 
import pandas as pd 

from mexcTest import createOrder
from mexc_sdk import Spot
spot = Spot(api_key='mx0vglwFI2Jc5NmUTX', api_secret='8ec86fe4c3844502b0b24f6da872cad3')


bars = tv.get_hist("XRPUSDT", "MEXC", Interval.in_1_minute, 100) 
bars.reset_index(drop=False, inplace=True)
shortEmaLength = 150
longEmaLength = 300
stochLength = 14
stochSmoothK = 3
stochSmoothD = 3

buying = False
xrp = 0
closePrice = 0 
def process_kline(decoded):
    global bars, buying, closePrice, xrp
    start = int(decoded["windowStart"])
    bar = {
        "datetime": datetime.fromtimestamp(start),
        "symbol": "MEXC:XRPUSDT",
        "open": float(decoded["openingPrice"]),
        "high": float(decoded["highestPrice"]),
        "low": float(decoded["lowestPrice"]),
        "close": float(decoded["closingPrice"]),
        "volume": float(decoded["volume"]),
    }
    if not bars.empty and bars.iloc[-1]["datetime"] == bar["datetime"]:
        bars.iloc[-1] = bar
    else:
        bars = pd.concat([bars, pd.DataFrame([bar])], ignore_index=True)

    bars['stoch_rsi_k'] = ta.momentum.StochRSIIndicator(bars['close'], stochLength, stochSmoothK, stochSmoothD, fillna=True).stochrsi_k()
    bars['shortEMA'] = ta.trend.ema_indicator(bars['close'], shortEmaLength, fillna=True)
    bars['longEMA'] = ta.trend.ema_indicator(bars['close'], longEmaLength, fillna=True)
    row = bars.iloc[-1]
    #print(bars.iloc[-2]['stoch_rsi_k'], row['stoch_rsi_k'])
    if not buying and bars.iloc[-2]['stoch_rsi_k'] < 0.2 and row['stoch_rsi_k'] > 0.2:
        buying = True
        closePrice = row['close']
        createOrder('market', 'buy', '30')
        trade = spot.account_trade_list(symbol="XRPUSDT", options={ "limit": 1})[0]
        price = trade['price']
        qty = trade['qty']
        createOrder( "limit", "sell", qty, float(price)+0.0001)
    elif buying and (row['close'] >= float(closePrice)+0.0002):
        #createOrder('market', 'sell' ,xrp)
        buying = False



async def handle_message(msg):
    if isinstance(msg, bytes):
        data = PushDataV3ApiWrapper_pb2.PushDataV3ApiWrapper()
        data.ParseFromString(msg)
        payload = MessageToDict(data, preserving_proto_field_name=True)
        if "publicSpotKline" in payload:
            decoded = payload["publicSpotKline"]
            process_kline(decoded)
    else:
        print("TEXT MESSAGE:", msg)


async def start_ws(subscriptions):
    uri = "wss://wbs-api.mexc.com/ws"
    while True:
        try:
            print("Connecting to WebSocket:", uri)
            async with websockets.connect(uri, ping_interval=30, ping_timeout=10) as ws:
                for channel in subscriptions:
                    subscribe_msg = {"method": "SUBSCRIPTION", "params": [channel]}
                    await ws.send(json.dumps(subscribe_msg))
                    print("Subscribed to channel:", channel)

                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=20)
                        await handle_message(msg)
                    except asyncio.TimeoutError:
                        await ws.send(json.dumps({"method": "PING"}))
                        print("Sent ping to keep connection alive.")

        except Exception as e:
            print("WebSocket error:", e)
            print("Retrying connection in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    subscriptions = [
        "spot@public.kline.v3.api.pb@XRPUSDT@Min1",
    ]
    asyncio.run(start_ws(subscriptions))
