from pybit.unified_trading import HTTP
from pprint import pprint
from time import time
from enum import Enum
try:
    from app.utils import RR
except Exception as e:
    from utils import RR

class Category(Enum):
    Linear = "linear"
    Inverse = "inverse"
    
    def __str__(self) -> str:
        return self.value

class AccoutType(Enum):
    unitfied = "UNIFIED"
    
    def __str__(self) -> str:
        return self.value

class TimeInForce(Enum):
    GTC = "GTC" # GoodTillCancel
    IOC = "IOC" # ImmediateOrCancel
    FOK = "FOK" # FillOrKill
    PostOnly = "PostOnly"
    
    def __str__(self) -> str:
        return self.value


class Side(Enum):
    Sell = "Sell"
    Buy = "Buy"
    
    def __str__(self) -> str:
        return self.value

class Type(Enum):
    Market = "Market"
    Limit = "Limit"
    
    def __str__(self) -> str:
        return self.value

class TpSlMode(Enum):
    Full = "Full"
    Partial = "Partial"
    
    def __str__(self) -> str:
        return self.value
    
    
class TriggerBy(Enum):
    LastPrice = "LastPrice"
    IndexPrice = "IndexPrice"
    MarkPrice = "MarkPrice"
    
    def __str__(self) -> str:
        return self.value


class NBybitFuture:
    
    def __init__(self, api_key, secret, testnet=True):
        self.client_ss = HTTP(
        testnet=testnet,
        api_key=api_key,
        api_secret=secret,
    )
        
    def c_pprint(self, dictionary, filter_keys=[], name=""):
        if name:
            print("=="*15, name, "=="*15)
        else:
            print("=="*30)
        
        print()
        if filter_keys:
            new_dict = { k : v for k, v in dictionary.items() if k in filter_keys}
            pprint(new_dict)
            print()
            print("=="*30)
            return new_dict
        
        pprint(dictionary)
        print("=="*30)
        return dictionary
        
        

    def get_balance(self):
        """_summary_

        Returns:
           ============================== Balance ==============================

            {'totalAvailableBalance': '10002.2795', 'totalMarginBalance': '10002.2795'}

            ============================================================
        """
        result = self.client_ss.get_wallet_balance(
            accountType=AccoutType.unitfied.value,
            coin="USDT,USDC",
        )

        if result.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {result.get('retMsg', '')} ")
            return {}

        filter_keys = ["totalAvailableBalance", "totalMarginBalance", "totalPerpUPL", "totalInitialMargin", "totalMaintenanceMargin"]
        return self.c_pprint(result["result"]["list"][0], name="Balance", filter_keys=filter_keys)
         
    
    def get_ticker(self, symbol="ARBUSDT"):
        """_summary_

        Args:
            symbol (str, optional): _description_. Defaults to "ARBUSDT".

        Returns:
            ============================== ARBUSDT ==============================

            {'a': [["16638.64", "0.008479"]],
            'b': [["16638.27", "0.305749"]],
            'ts': '1672765737733',
            'symbol': 'ARBUSDT'}

            ============================================================
        """
        result = self.client_ss.get_orderbook(
            category=f"{Category.Linear}",
            symbol=symbol,
            limit=10
        )
        """
        Response 

        {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "s": "BTCUSDT",
                "a": [
                    [
                        "16638.64",
                        "0.008479"
                    ]
                ],
                "b": [
                    [
                        "16638.27",
                        "0.305749"
                    ]
                ],
                "ts": 1672765737733,
                "u": 5277055
            },
            "retExtInfo": {},
            "time": 1672765737734
        }
        """
        
        if result.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {result.get('retMsg', '')} ")
            return {}

        return self.c_pprint(result["result"], name=symbol, filter_keys=["s", "a", "b", "ts"])
    
    def get_position(self, symbol="ARBUSDT"):
        response = self.client_ss.get_positions(
            category=f"{Category.Linear}",
            symbol=symbol,
        )

        if response.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {response.get('retMsg', '')} ")
            return {}
        
        return self.c_pprint(response["result"]["list"][0], name=symbol, 
                        filter_keys=["symbol", "size", "side", "positionValue", "unrealisedPnl", 
                                     "avgPrice", "stopLoss", "takeProfit", "tpslMode"])
    
    
    def close_long(self, qty=0, percent=1, symbol="ARBUSDT"):
        """_summary_

        Args:
            qty (int, optional): _description_. Defaults to 0.
            percent (int, optional): _description_. Defaults to 1.
            symbol (str, optional): _description_. Defaults to "ARBUSDT".

        Returns:
            {'result': {'orderId': '37a25ec3-e2fe-4d8f-8d0b-b347df20838b',
                        'orderLinkId': ''},
            'retCode': 0,
            'retExtInfo': {},
            'retMsg': 'OK',
            'time': 1686130540125}
        """
        qty = self.get_position(symbol=symbol).get("size", "0").replace(" ", "")
        print("qty :: ", qty)
        if qty in [0, "0"]:
            print(f"[ INFO  ] Bybit : No Open order ")
            return {}
        
        response = self.client_ss.place_order(
            category=f"{Category.Linear}",
            symbol=symbol,
            side=f"{Side.Sell}",
            orderType=f"{Type.Market}",
            qty=qty,
            timeInForce=f"{TimeInForce.IOC}",
            takeProfit="0",
            stopLoss="0",
        ) 
        
        if response.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {response.get('retMsg', '')} ")
            return {}

        return self.c_pprint(response["result"], name=f"[ {symbol} ] OPEN ORDER", filter_keys=[])
    
    
    
    def close_short(self, qty=0, percent=1, symbol="ARBUSDT"):
        """_summary_

        Args:
            qty (int, optional): _description_. Defaults to 0.
            percent (int, optional): _description_. Defaults to 1.
            symbol (str, optional): _description_. Defaults to "ARBUSDT".

        Returns:
            {'result': {'orderId': '37a25ec3-e2fe-4d8f-8d0b-b347df20838b',
                        'orderLinkId': ''},
            'retCode': 0,
            'retExtInfo': {},
            'retMsg': 'OK',
            'time': 1686130540125}
        """
        qty = self.get_position(symbol=symbol).get("size", "0").replace(" ", "")
        if qty in [0, "0"]:
            print(f"[ INFO  ] Bybit : No Open order ")
            return {}
        
        response = self.client_ss.place_order(
            category=f"{Category.Linear}",
            symbol=symbol,
            side=f"{Side.Buy}",
            orderType=f"{Type.Market}",
            qty=qty,
            timeInForce=f"{TimeInForce.IOC}",
            takeProfit="0",
            stopLoss="0",
        ) 
        
        if response.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {response.get('retMsg', '')} ")
            return {}

        return self.c_pprint(response["result"], name=f"[ {symbol} ] OPEN ORDER", filter_keys=[])
    
    
    
    def open_long(self, qty=0, percent=1, symbol="ARBUSDT", max_loss=250, order_size=0, tp=0, sl=0, rr=3):
        """_summary_

        Args:
            qty (int, optional): _description_. Defaults to 0.
            percent (int, optional): _description_. Defaults to 1.
            symbol (str, optional): _description_. Defaults to "ARBUSDT".

        Returns:
            {'result': {'orderId': '37a25ec3-e2fe-4d8f-8d0b-b347df20838b',
                        'orderLinkId': ''},
            'retCode': 0,
            'retExtInfo': {},
            'retMsg': 'OK',
            'time': 1686130540125}
        """
        balance = float(self.get_balance().get("totalAvailableBalance", 0))
        if balance == 0:
            print(f"[INFO  ] Bybit : Balance is 0")
            return {}
        
        price_n_vol = self.get_ticker(symbol=symbol).get("a", [[0, 0]])[0]  # get ask price 
        price = float(price_n_vol[0])
        vol = price_n_vol[1]
        vDigit = vol[::-1].find('.')
        
        if price == 0:
            print(f"[INFO  ] Bybit : cannot get bid1Price of {symbol}")
            return {}
        
        if qty == 0 and order_size == 0:
            qty = round((balance *  percent) / price, vDigit)
        
        elif qty == 0 and order_size > 0:
            qty = round(order_size / price, vDigit)
            
        
        if sl != 0:
            rrr = RR(entry_price=price, qty=qty, side=Side.Buy.value, ratio=rr, sl=sl)
            tp = rrr.get_tp_price()
        
        # Calculate stop loss
        response = self.client_ss.place_order(
            category=f"{Category.Linear}",
            symbol=symbol,
            side=f"{Side.Buy}",
            orderType=f"{Type.Limit}",
            qty=f'{qty}',
            timeInForce=f"{TimeInForce.FOK}", 
            takeProfit=f"{tp}",
            stopLoss=f"{sl}",
            price=f"{price}"
        ) 
        
        if response.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {response.get('retMsg', '')} ")
            return {}

        return self.c_pprint(response["result"], name=f"[ {symbol} ] OPEN ORDER", filter_keys=[])
    
        
    def open_short(self, qty=0, percent=1, symbol="ARBUSDT", max_loss=250, order_size=0, tp=0, sl=0, rr=3):
        balance = float(self.get_balance().get("totalAvailableBalance", 0))
        if balance == 0:
            print(f"[INFO  ] Bybit : Balance is 0")
            return {}
        
        price_n_vol = self.get_ticker(symbol=symbol).get("b", [[0, 0]])[0]  # get bid price 
        price = float(price_n_vol[0])
        vol = price_n_vol[1]
        vDigit = vol[::-1].find('.')
        
        if price == 0:
            print(f"[INFO  ] Bybit : cannot get bid1Price of {symbol}")
            return {}
        
        if qty == 0 and order_size == 0:
            qty = round( (balance *  percent) / price, vDigit)
        
        elif qty == 0 and order_size > 0:
            qty = round( order_size / price, vDigit)
            
        
        if sl != 0:
            rrr = RR(entry_price=price, qty=qty, side=Side.Buy.value, ratio=rr, sl=sl)
            tp = rrr.get_tp_price()

        
        response = self.client_ss.place_order(
            category=f"{Category.Linear}",
            symbol=symbol,
            side=f"{Side.Sell}",
            orderType=f"{Type.Limit}",
            qty=f'{qty}',
            timeInForce=f"{TimeInForce.FOK}",
            takeProfit=f"{tp}",
            stopLoss=f"{sl}",
            price=f"{price}"
        ) 
        
        if response.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {response.get('retMsg', '')} ")
            return {}

        return self.c_pprint(response["result"], name=f"[ {symbol} ] OPEN ORDER", filter_keys=[])
    
    
    
    def update_tpsl(self, symbol="ARBUSDT", sl_price=None, tp_price=None):
        """_summary_

        Args:
            symbol (str, optional): _description_. Defaults to "ARBUSDT".
            sl_price (_type_, optional): _description_. Defaults to None.
            tp_price (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        position_info = self.get_position(symbol=symbol)
        
        try:
            response = self.client_ss.set_trading_stop(
                category=f"{Category.Linear}",
                symbol=symbol,
                tpTriggerBy=f"{TriggerBy.LastPrice}",
                slTriggerBy=f"{TriggerBy.MarkPrice}",
                tpslMode=f"{TpSlMode.Full}",
                takeProfit=f"{tp_price if tp_price else position_info.get('takeProfit', 0)}",
                stopLoss=f"{sl_price if sl_price else position_info.get('stopLoss', 0)}",
                positionIdx=0
            )
            
        except Exception as e: 
            response = {
                'result': {},
                'retCode': 0,
                'retExtInfo': {},
                'retMsg': f'NG - not modified (ErrCode: 34040)',
                'time': time()
            }
       
        if response.get("retMsg", None) != "OK": 
            print(f"[ INFO  ] Bybit : {response.get('retMsg', '')} ")
            return {}

        return self.c_pprint({'retMsg': 'OK'}, name=f"[ {symbol} ] Update TakeProfit & StopLoss", filter_keys=[])
    
    
  
def main():
    from os import environ
    SYMBOL = "SOLUSDT"
    TEST_BYBIT_API_KEY="cC02UEf0uq2qdQmZC7"
    TEST_BYBIT_API_SECRET="eojUkhdpwI5tnFt4Izdnb7WX9riKvQWVud1y"
    n_bybit_client = NBybitFuture(api_key=TEST_BYBIT_API_KEY, secret=TEST_BYBIT_API_SECRET)

    # res = n_bybit_client.open_long(symbol=SYMBOL, sl=82.0, tp=100.0, order_size=10000)
    # pprint(res)
    
    res = n_bybit_client.open_short(symbol=SYMBOL, sl=100.0, tp=82.0, order_size=10000)
    pprint(res)
    
    # res = n_bybit_client.get_ticker(symbol=SYMBOL)
    # pprint(res)
    
    
if __name__ == "__main__":
    main()