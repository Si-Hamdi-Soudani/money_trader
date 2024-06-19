import csv
import os
import datetime
import pytz

# Define Tunisian time zone
tunisia_tz = pytz.timezone('Africa/Tunis')

class TradeLogger:
    def __init__(self, log_file='logs/trade_log.csv'):
        self.log_file = log_file
        self._create_logs_directory()
        self._create_log_csv()

    def _create_logs_directory(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _create_log_csv(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Entry Time", "Win Rate Percentage", "Timeframe", "Action", "Outcome", "Exit Time", "Candlestick Pattern", "Model Accuracy", "Reason"])

    def log_trade(self, entry_time, win_rate_percentage, timeframe, action, outcome, exit_time, candlestick_pattern, model_accuracy):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                win_rate_percentage,
                timeframe,
                action,
                outcome,
                exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                candlestick_pattern,
                model_accuracy,
                'N/A'  # Placeholder for reason
            ])

    def analyze_trade_outcome(self, trade):
        """Analyzes the outcome of a trade based on entry/exit prices and predicted action."""
        entry_price = self.get_candle_by_time(trade['entry_time'])['close']  # Get entry price
        exit_time = trade['entry_time'] + datetime.timedelta(minutes=trade['timeframe'])
        exit_price = self.get_candle_by_time(exit_time)['close']  # Get exit price

        if trade['action'] == 'Up' and exit_price > entry_price:
            outcome = 'Win'
        elif trade['action'] == 'Down' and exit_price < entry_price:
            outcome = 'Win'
        else:
            outcome = 'Loss'

        return outcome

    def get_candle_by_time(self, timestamp):
        """Retrieves the candlestick data for a given timestamp."""
        timestamp_milliseconds = timestamp.timestamp() * 1000  # Convert to milliseconds
        for candle in self.data_manager.price_history:
            if abs(candle['timestamp'] - timestamp_milliseconds) < 60000:  # Allow a 1-minute tolerance
                return candle
        return None 

