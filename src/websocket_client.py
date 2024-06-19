# src/websocket_client.py

import websocket
import json
import datetime

class BinanceWebSocketClient:
    def __init__(self, symbol='btcusdt', interval='1m', data_manager=None):
        
        self.symbol = symbol
        self.interval = interval
        self.data_manager = data_manager
        self.ws = None
        self.last_saved_timestamp = None  # To track the last saved candlestick
        

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
        if kline['x']:  # Ensure the kline is closed
            candle = {
                'timestamp': kline['t'],
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v'])
            }
            if self.data_manager and (self.last_saved_timestamp != kline['t']):
                self.data_manager.save_candle(candle)
                self.last_saved_timestamp = kline['t']

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    def connect(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            
            
        )
        self.ws.run_forever()