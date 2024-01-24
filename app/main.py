from fastapi import FastAPI,  Body, Request, Header
import httpx
import uvicorn
from pprint import pprint
from os import environ
from enum import Enum
from datetime import datetime
from app.parse_message import OrderMesssage
from jwt import decode
from app.BybitFutures import NBybitFuture
from app.BinanceFutures import NBinanceFuture
from enum import Enum
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

TEST_BINANCE_API_KEY = environ.get("BINANCE_API_KEY", None)
TEST_BINANCE_API_SECRET = environ.get("BINANCE_API_SECRET", None)
TEST_BYBIT_API_KEY = environ.get("TEST_BYBIT_API_KEY", None)
TEST_BYBIT_API_SECRET = environ.get("TEST_BYBIT_API_SECRET", None)

MAIN_BYBIT_API_KEY = environ.get("MAIN_BYBIT_API_KEY", None)
MAIN_BYBIT_API_SECRET = environ.get("MAIN_BYBIT_API_SECRET", None)


PROXY_API_KEY = environ.get("PROXY_API_KEY", None)
PROXY_API_SECRET = environ.get("PROXY_API_SECRET", None)

TESTNET = bool(environ.get("TESTNET", 0))
LEVERAGE = float(environ.get("LEVERAGE", 1))

um_futures_client = NBinanceFuture(api_key=TEST_BINANCE_API_KEY, 
                                   secret=TEST_BINANCE_API_SECRET, 
                                   url="https://testnet.binance.vision/api")

bybit_client_mainnet = NBybitFuture(
    api_key=MAIN_BYBIT_API_KEY,
    secret=MAIN_BYBIT_API_SECRET,
    testnet=False
)

bybit_client_testnet = NBybitFuture(
    api_key=TEST_BYBIT_API_KEY,
    secret=TEST_BYBIT_API_SECRET,
    testnet=True
)


TESTNET_DOMAIN = environ.get("TESTNET_DOMAIN", "localhost")
MAINNET_DOMAIN = environ.get("MAINNET_DOMAIN", "localhost")

TESTNET_PROTOCAL = environ.get("TESTNET_PROTOCAL", "http")
MAINNET_PROTOCAL = environ.get("MAINNET_PROTOCAL", "http")

TV_API_SECRET = environ.get("TV_API_SECRET", "")
TV_API_KEY = environ.get("TV_API_KEY", "")


class Exchange(Enum):
    Bybit = "BYBIT"
    Binance = "BINANCE"


class Action(Enum):
    OpenShort = "OS"
    OpenLong = "OL"
    CloseShort = "CS"
    CloseLong = "CL"
    CloseShortOpenLong = "CSOL"
    CloseLongOpenShort = "CLOS"
    
    UpdateTPSL = "UPTPSL"
    UpdateTP = "UPTP"
    UpdateSL = "UPSL"
    
    def __str__(self) -> str:
        return self.value
    

class Side(Enum):
  Sell = "SELL"
  Buy = "BUY"
  
  def __str__(self) -> str:
    return self.value
    

class WebhookURL(Enum):
  Testnet = f'{TESTNET_PROTOCAL}://{TESTNET_DOMAIN}/alert-hook'
  Mainnet = f'{MAINNET_PROTOCAL}://{MAINNET_DOMAIN}/alert-hook'
  
  def __str__(self) -> str:
    return self.value
  
class Network(Enum):
  Testnet = "TESTNET"
  Mainnet = "MAINNET"
  Both = "BOTH"
  
  def __str__(self) -> str:
    return self.value

HEADERS = {
  "Content-Type": "text/plain; charset=UTF-8",
  "jwt": "VVS"
}

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


########################

def verify_jwt(jwt_str, secret, api_key):
  try:
      print("JWT :: ", jwt_str)
      result = decode(jwt_str, secret, algorithms=["HS256"])
      print("Decode ::", result)
      return api_key == result.get("apiKey", None)
  except Exception as e:
      return False

def send_message(body, order, url, network="TESTNET"):
  try:
    pprint(order.json)
    r = httpx.post(url, headers=HEADERS, data=body)
  except Exception as e:
    result = {"status": 500, "message": f"{e}"}
  else:
    result = r.json()
  finally:
    url = WebhookURL.testnet.value  if network == "TESTNET" else WebhookURL.mainnet.value
    print(f"[INFO  ] [ {network} : {url} ] RESULT : {result}")
    print("---"*10, datetime.now())
    print()
    return result

async def make_orderbook(order : OrderMesssage):
  client = None 
  if order.exchange == Exchange.Binance.value:
      client = um_futures_client
  elif order.exchange == Exchange.Bybit.value:
      client = bybit_client_mainnet if order.network == Network.Mainnet.value else bybit_client_testnet
  
  print()
  pprint(order.json)
  print()
  
  if not client:
    return {"status": 403, "message" : "Network Not Found"}
    
  try:
    if order.message == f"{Action.CloseShortOpenLong}":
      print("--------- CLOSE SHORT -->  OPEN LONG ---------")
      client.close_short(symbol=order.symbol)
      if order.balance:
        client.open_long(symbol=order.symbol, order_size=order.balance, sl=order.lower_bound, rr=order.rr)
      else:
        client.open_long(symbol=order.symbol, percent=LEVERAGE)
        
    elif order.message == f"{Action.CloseLongOpenShort}":
      print("--------- CLOSE LONG -->  OPEN SHORT ---------")
      client.close_long(symbol=order.symbol)
      if order.balance:
        client.open_short(symbol=order.symbol, order_size=order.balance, sl=order.upper_bound, rr=order.rr)  
      else:
        client.open_short(symbol=order.symbol, percent=LEVERAGE)  
        
    elif order.message == f"{Action.CloseShort}":
      print("--------- CLOSE SHORT ---------")
      client.close_short(symbol=order.symbol)
    
    elif order.message == f"{Action.CloseLong}":
      print("--------- CLOSE LONG ---------")
      client.close_long(symbol=order.symbol)
        
    elif order.message == f"{Action.OpenShort}":
      if order.side == Side.Sell.value:
        print("--------- OPEN SHORT ---------")
        if order.balance:
          client.open_short(symbol=order.symbol, order_size=order.balance, sl=order.upper_bound, rr=order.rr)
        else:
          client.open_short(symbol=order.symbol, percent=LEVERAGE) 
            
    elif order.message == f"{Action.OpenLong}":
      print("--------- OPEN LONG ---------")
      if order.balance:
        client.open_long(symbol=order.symbol, order_size=order.balance, sl=order.lower_bound, rr=order.rr)
      else:
        client.open_long(symbol=order.symbol, percent=LEVERAGE) 
    elif order.message == f"{Action.UpdateTPSL}":
      print("--------- UPDATE TP SL ---------")
      sl_price = order.sl_price
      tp_price = order.tp_price
      
      if not (sl_price and tp_price):
        return {"status": 500, "message" : "sl price or tp price is missing"}
      
      client.update_tpsl(symbol=order.symbol, sl_price=sl_price, tp_price=tp_price)
    
    elif order.message == f"{Action.UpdateTP}":
      print("--------- UPDATE TP ---------")
      
      if not order.tp_price :
        return {"status": 500, "message" : "tp price is missing"}
      
      client.update_tpsl(symbol=order.symbol, tp_price=order.tp_price)
      
    elif order.message == f"{Action.UpdateSL}":
      print("--------- UPDATE SL ---------")
      
      if not order.sl_price :
        return {"status": 500, "message" : "sl price is missing"}
      
      client.update_tpsl(symbol=order.symbol, sl_price=order.sl_price)
    
    else:
        return {"status": 500, "message" : f"Incorrect Action !"}
            
  except Exception as e:
      print(e)
      print("---"*10)
      print()
      return {"status": 500, "message" : f"{e}"}
  
  print("---"*10)
  print()
  
  return {"status": 200, "message" : f"No Action"}
######################

@app.get("/")
async def main(request: Request):
  user_ip = request.headers.get('CF-Connecting-IP', request.client.host)
  country = request.headers.get('CF-IPCountry', "nowhere")
  return {"message": f"Hello {user_ip} from {country}:: {datetime.now()}"}

@app.head("/")
async def head():
  return {"message": f"Still Alive :: {datetime.now()}"}

@app.get("/health")
async def health():
  return {"message": f"Still Alive :: {datetime.now()}"}

@app.post("/alert-hook")
async def alert_hook(body: str = Body(..., media_type='text/plain')):
    order = OrderMesssage(body)
    print()
    print("--------- ", order.message, " ---------")
    if not verify_jwt(order.jwt, TV_API_SECRET, TV_API_KEY):
      print("Authentication Error")
      print("--------- ", "Error", " ---------")
      return {"status": 403, "message" : "Authentication Error"} 
    
    network = order.network if order.network else Network.Testnet.value
    
    # if network == Network.Both.value:
    #   send_message(body, order, url=f"{WebhookURL.Mainnet}", network=f"{Network.Mainnet}")
    #   return send_message(body, order, url=f"{WebhookURL.Testnet}")
    # elif network == Network.mainnet.value:
    #   return send_message(body, order, url=f"{WebhookURL.Mainnet}", network=f"{Network.Mainnet}")
    # else:
    #   return send_message(body, order, url=f"{WebhookURL.Testnet}")
    
    action_result = None
    if network == Network.Mainnet.value:
      action_result = await make_orderbook(order)      
    elif network == Network.Testnet.value:
      action_result = await make_orderbook(order)
    else:
      return {"status": 500, "message" : "Network Option Incorrect"} 
    
    return action_result

if __name__ == "__main__":
  uvicorn.run(app, port=int(environ.get("PORT", 8080)), host="0.0.0.0")