import threading
import time
import datetime
import os
import pytz

from websocket_client import BinanceWebSocketClient
from data_manager import DataManager
from model_trainer import ModelTrainer
from trade_signal_generator import TradeSignalGenerator
from trade_logger import TradeLogger

# Define Tunisian time zone
tunisia_tz = pytz.timezone('Africa/Tunis')

def main():
    # Directory setup
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Initialize components
    data_manager = DataManager(candlestick_file='data/candlestick_data.csv')
    websocket_client = BinanceWebSocketClient(data_manager=data_manager)
    model_trainer = ModelTrainer(model_file='models/candlestick_model.h5')
    trade_signal_generator = TradeSignalGenerator(model_file='models/candlestick_model.h5', data_manager=data_manager)
    trade_logger = TradeLogger(log_file='logs/trade_log.csv')

    # Load initial data
    data_manager.load_candlestick_data()

    # Start WebSocket client in a separate thread
    ws_thread = threading.Thread(target=websocket_client.connect)
    ws_thread.start()

    # Check if there's enough data to train the initial model
    if len(data_manager.price_history) > 0:
        model_trainer.train_model()
    
    logged_trades = [] 
    previous_state = None
    previous_action = None
    while True:
        # Wait for the next minute to start
        now = datetime.datetime.now(tunisia_tz)
        next_minute = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        time.sleep((next_minute - now).total_seconds())

        # Generate trade signal
        signal = trade_signal_generator.generate_trade_signal()
        if signal:
            print(f"Trade Signal: {signal}")

            # Log the trade
            trade_logger.log_trade(
                entry_time=signal['entry_time'],
                win_rate_percentage=signal['win_rate_percentage'],
                timeframe=signal['timeframe'],
                action=signal['action'],
                outcome='Pending',
                exit_time=signal['entry_time'] + datetime.timedelta(minutes=signal['timeframe']),
                candlestick_pattern='N/A',  # Placeholder for now
                model_accuracy=signal['win_rate_percentage']  # Placeholder for now
            )
        for trade in logged_trades:
            if trade['outcome'] == 'Pending' and datetime.datetime.now(tunisia_tz) >= trade['exit_time']:
                trade['outcome'] = trade_logger.analyze_trade_outcome(trade)
                print(f"Trade Outcome: {trade}")

                # Reinforcement Learning update
                current_state = trade_signal_generator.get_state(data_manager.get_latest_candles(n=20))
                reward = 1 if trade['outcome'] == 'Win' else -1
                if previous_state is not None and previous_action is not None:
                    trade_signal_generator.update_q_table(previous_state, previous_action, reward, current_state)

                previous_state = current_state
                previous_action = trade['action']
        # Retrain the model every 20 minutes
        if now.minute % 20 == 0:
            model_trainer.train_model()

main()