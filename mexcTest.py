
import requests
from mexc_sdk import Spot
from datetime import datetime as dt
spot = Spot(api_key='mx0vglwFI2Jc5NmUTX', api_secret='8ec86fe4c3844502b0b24f6da872cad3')


def getBal(symbol):
    return [x for x in spot.account_info()['balances'] if x['asset'] == symbol][0]['free']



def createOrder( type_order='market', side='buy', order_size = "30", price = '0.35'):
    if len(spot.open_orders(symbol="XRPUSDT")) > 0:
        return
    u_id="WEBd7912d2ede53915e9f0097c9feccbfd5f8991565b1a410cad41f11e9da16b5ce"
    currencyId="a7ceba5c75644a82ad2ccc1069f7a177"
    marketCurrencyId="128f589271cb4951b03e71e6323eb7be"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': 'u_id='+u_id,
        'language': 'en-US',
        'origin': 'https://www.mexc.com',
        'pragma': 'akamai-x-cache-on',
        'priority': 'u=1, i',
        'referer': 'https://www.mexc.com/exchange/XRP_USDT',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    
    json_data={
        "currencyId":currencyId,
        "marketCurrencyId":marketCurrencyId,
        "tradeType":side.upper(),
        "price":price,
        "quantity":order_size,
        "stopPrice": float(price)+0.0001,
    }
    

    if type_order=="market":
        json_data["orderType"]="MARKET_ORDER"
    if type_order=="limit":
        json_data["orderType"]="LIMIT_ORDER"

    response = requests.post('https://www.mexc.com/api/platform/spot/order/place', headers=headers, json=json_data)
    
    
    json_obj = response.json()
    print(json_obj)
    trade = spot.account_trade_list(symbol="XRPUSDT", options={ "limit": 1})[0]
    price = trade['price']
    print(f"{side} at {price} at time {dt.fromtimestamp(float(trade['time'])/1000)}")



if __name__ == "__main__":
    usd = [x for x in spot.account_info()['balances'] if x['asset'] == "USDT"][0]['free']
    createOrder( 'market', 'buy',usd )
    trade = spot.account_trade_list(symbol="XRPUSDT", options={ "limit": 1})[0]
    price = trade['price']
    qty = trade['quoteQty']
    print(f"Bought {qty} at {price}")
    print(trade)
    xrp = [x for x in spot.account_info()['balances'] if x['asset'] == "XRP"][0]['free']
    createOrder( "limit", "sell", xrp, float(price)+0.0001)#
    trade = spot.open_orders("XRPUSDT")[0]
    price = trade['price']
    qty = trade['origQuoteOrderQty']
    print(f"Going to sell {qty} at {price}")
