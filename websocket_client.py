# websocket_client.py

import websocket
import json
import csv
import datetime

class BinanceWebSocketClient:
    def __init__(self, symbol='btcusdt', interval='1m'):
        self.symbol = symbol
        self.interval = interval
        self.ws = None

  # websocket_client.py (continued)

    def on_open(self, ws):
        subscribe_message = json.dumps({
            "method": "SUBSCRIBE",
            "params": [f"{self.symbol}@kline_{self.interval}"],
            "id": 1
        })
        ws.send(subscribe_message)

    def on_message(self, ws, message):
        data = json.loads(message)
        kline = data['k']
        if kline['x']:
            candle = {
                'timestamp': kline['t'],
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v'])
            }
            self.save_candle(candle)

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")
