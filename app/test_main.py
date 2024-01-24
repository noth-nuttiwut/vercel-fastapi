from fastapi import FastAPI, Request
import uvicorn
from pprint import pprint
from os import environ

from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
async def main():
  return {"text" : "Hello world!"}

@app.get("/sayhi")
async def sayhi():
  return {"text" : "Hi there !"}



if __name__ == "__main__":
  uvicorn.run(app, port=int(environ.get("PORT", 8181)), host="0.0.0.0")