import asyncio
from enum import Enum
from pprint import pprint
from binance.um_futures import UMFutures
from binance.error import ClientError
from time import sleep

class Side(Enum):
    Sell = "SELL"
    Buy = "BUY"

class Type(Enum):
    Market = "MARKET"
    Limit = "LIMIT"




class NBinanceFuture:
    
    def __init__(self, api_key, secret, url) -> None:
        self.client = UMFutures(key=api_key, secret=secret, base_url=url)

    
    def c_pprint(self, dictionary, filter_keys=[]):
        if filter_keys:
            new_dict = { k : v for k, v in dictionary.items() if k in filter_keys}
            pprint(new_dict)
            return 
        
        pprint(dictionary)
        


    def open_long(self, symbol='BTCUSDT'):
        um_futures_acc = self.client.account()
        my_acc_pos = [ pos for pos in um_futures_acc["positions"] if pos["symbol"] in [symbol]][0]
        my_acc_balance = [ el for el in self.client.balance() if el["asset"] in ["USDT"]][0]
        
        my_usdt = round(float(my_acc_balance["availableBalance"])*0.5) * int(my_acc_pos["leverage"])
        price = float(self.client.ticker_price(symbol)["price"])
        qty = round(my_usdt/price, 3)
        # Post a new order
        params = {
            'symbol': symbol,
            'side': Side.Buy.value,
            'type': Type.Market.value,
            'quantity': qty,
        }
        try:
            response = self.client.new_order(**params)
            print("[INFO ] Open long order successful ! ")
            self.c_pprint(response, filter_keys=["symbol", "side", "orderId", "closePosition"])
            print("=="*50)
            return response["orderId"]
        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
        
    def close_long(self, symbol="BTCUSDT"):
        um_futures_acc = self.client.account()
        my_acc_pos = [ pos for pos in um_futures_acc["positions"] if pos["symbol"] in ["BTCUSDT"]][0]
        # my_acc_balance = [ el for el in self.client.balance() if el["asset"] in ["USDT"]][0]
        qty = float(my_acc_pos["positionAmt"])
        if qty <= 0:
            return False
        
        params = {
            'symbol': symbol,
            'side': Side.Sell.value,
            'type': Type.Market.value,
            'quantity': qty,
        }
        try:
            response = self.client.new_order(**params)
            print("[INFO ] Close long order successful ! ")
            self.c_pprint(response, filter_keys=["symbol", "side", "orderId", "closePosition"])
            print("=="*50)
            return response["orderId"]
        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
        
    def open_short(self, symbol='BTCUSDT'):
        um_futures_acc = self.client.account()
        my_acc_pos = [ pos for pos in um_futures_acc["positions"] if pos["symbol"] in [symbol]][0]
        my_acc_balance = [ el for el in self.client.balance() if el["asset"] in ["USDT"]][0]
        
        my_usdt = round(float(my_acc_balance["availableBalance"])*0.5) * int(my_acc_pos["leverage"])
        price = float(self.client.ticker_price(symbol)["price"])
        qty = round(my_usdt/price, 3)

        # Post a new order
        params = {
            'symbol': symbol,
            'side': Side.Sell.value,
            'type': Type.Market.value,
            'quantity': qty,
        }
        try:
            response = self.client.new_order(**params)
            print("[INFO ] Open short order successful ! ")
            self.c_pprint(response, filter_keys=["symbol", "side", "orderId", "closePosition"])
            print("=="*50)
            return response["orderId"]
        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
            

    def close_short(self, symbol='BTCUSDT'):
        um_futures_acc = self.client.account()
        my_acc_pos = [ pos for pos in um_futures_acc["positions"] if pos["symbol"] in [symbol]][0]
        # my_acc_balance = [ el for el in self.client.balance() if el["asset"] in ["USDT"]][0]
        
        qty = float(my_acc_pos["positionAmt"])
        if qty >= 0: 
            return False
        # Post a new order
        params = {
            'symbol': symbol,
            'side': Side.Buy.value,
            'type': Type.Market.value,
            'quantity': abs(qty),
        }
        try:
            response = self.client.new_order(**params)
            print("[INFO ] Close short order successful ! ")
            self.c_pprint(response, filter_keys=["symbol", "side", "orderId", "closePosition"])
            print("=="*50)
            return response["orderId"]
        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

    def check_balance(self, symbol="BTCUSDT"):
        print("-- Position --")
        um_futures_acc = self.client.account()
        my_acc_pos = [ pos for pos in um_futures_acc["positions"] if pos["symbol"] in [symbol]][0]
        pprint(my_acc_pos)
        print("=="*50)
        return my_acc_pos

async def main():
    SYMBOL = "BTCUSDT"
    from os import environ
    n_binance_client = NBinanceFuture(api_key=environ["BINANCE_API_KEY"], secret=environ["BINANCE_API_SECRET"], url="https://testnet.binancefuture.com")
    # n_binance_client.open_short_order(symbol=SYMBOL)
    
    n_binance_client.check_balance(symbol=SYMBOL)
    
    # await asyncio.sleep(60)
    
    # n_binance_client.close_short_order(symbol=SYMBOL)
    
    # n_binance_client.check_balance(symbol=SYMBOL)
    
    
    

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())