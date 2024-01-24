import httpx
from os import environ
import jwt
from enum import Enum
import secrets
import random
from pybit.unified_trading import HTTP

class Action(Enum):
    OpenShort = "OS"
    OpenLong = "OL"
    CloseShort = "CS"
    CloseLong = "CL"
    CloseShortOpenLong = "CSOL"
    CloseLongOpenShort = "CLOS"
    
    def __str__(self) -> str:
        return self.value

class AccoutType(Enum):
    unitfied = "UNIFIED"
    
    def __str__(self) -> str:
        return self.value


order = {
    "message" : "CLOS - SAR"
}

TEST_BYBIT_API_KEY = environ.get("TEST_BYBIT_API_KEY", None)
TEST_BYBIT_API_SECRET = environ.get("TEST_BYBIT_API_SECRET", None)

def test_bybit():

    session = HTTP(
        testnet=True,
        api_key=TEST_BYBIT_API_KEY,
        api_secret=TEST_BYBIT_API_SECRET
    )

    result = session.get_wallet_balance(
            accountType=f"{AccoutType.unitfied}",
            coin="USDT,USDC",
    )
    
    print(result)


def main_send_request():
    old_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhcGlLZXkiOiJ6aFZITXRrcXc0Uk9EUHdra0RWcWZUZkEifQ.xU3lvNH5XdLOcc0XhR8yTPETxM7g4VxUaLmetOnVCQM"
    old_data = f"symbol = MATICUSDT.P, exchange = BYBIT, side = buy, network = MAINNET, message = CL - BBandSE, size = 10.916, price = 1.2, timestamp = 2023-09-11T16:15:00Z, balance = 1500.00, JWT = {old_jwt}"
    
    new_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhcGlLZXkiOiJvaTRCZHhLeEtsSE9lc09CVzh2eWxkWHgifQ.iEwJ-XdrCQ1pM6lp38_cXvIzEcDyIJeHS7bQIARznrU"
    new_data = f"symbol = GALAUSDT.P, exchange = BYBIT, side = SELL, network = TESTNET, message = OS - BBandSE, size = 10.916, price = 1.2, timestamp = 2023-09-11T16:15:00Z, balance = 3000.00, JWT = {new_jwt}, upper = 0.02475, lower = 0.02, rr = 4.0"
    # base_url = "https://testnet-webhook-ewdxkehvuq-an.a.run.app"
    # base_url = "https://127.0.0.1:5432"
    # base_url = "https://tv-proxy-server-d67wrljpbq-as.a.run.app" # new - main
    # base_url = "https://tv-api-server-d67wrljpbq-as.a.run.app" # new - testnet
    base_url = "http://34.87.73.160" # mainnet

    REQUEST_URL = f"{base_url}/alert-hook"

    with httpx.Client() as client:
        headers = {
            "Content-Type": "text/plain; charset=UTF-8"
        }
        r = client.post(REQUEST_URL, headers=headers, data=new_data)

    print(r.json())

def generate_api_key(n=8):
    index = random.randint(0, n-1)
    return [ secrets.token_urlsafe(18) for _ in range(n) ][index]

def generate_api_scecret(n=8):
    index = random.randint(0, n-1)
    return [ secrets.token_hex(18) for _ in range(n) ][index]

def create_jwt(api_key, api_secret):
    return jwt.encode({"apiKey": api_key}, api_secret, algorithm="HS256")

def verify_jwt(jwt_str, api_key, api_secret):
    return jwt.decode(jwt_str, api_secret, algorithms=["HS256"])


def main_generate_jwt(API_KEY=None, API_SC=None):
    API_KEY = generate_api_key() if not API_KEY else API_KEY
    API_SC = generate_api_scecret() if not API_SC else API_SC
    print(f"API_KEY : {API_KEY}")
    print(f"API_SECRET : {API_SC}")
    jwt_str = create_jwt(API_KEY, API_SC)
    print(f"JWT : {jwt_str}")
    print(verify_jwt(jwt_str, API_KEY, API_SC))
    print("==="*15)


if __name__ == "__main__":
    # main_generate_jwt()
    # main_send_request()
    test_bybit()
