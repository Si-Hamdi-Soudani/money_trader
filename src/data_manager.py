# src/data_manager.py

import csv
import os
import datetime
import numpy as np

class DataManager:
    """Manages candlestick data, including loading, saving, indexing, and target calculation."""

    def __init__(self, candlestick_file='data/candlestick_data.csv', prediction_timeframe=5):
        self.candlestick_file = candlestick_file
        self.price_history = []
        self.prediction_timeframe = prediction_timeframe  # Timeframe in minutes
        self._create_data_directory()  # Create the directory if it doesn't exist
        self._create_candlestick_csv()

    def _create_data_directory(self):
        """Creates the 'data' directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.candlestick_file), exist_ok=True)

    def _create_candlestick_csv(self):
        """Creates the CSV file for completed candlesticks with headers."""
        if not os.path.exists(self.candlestick_file):
            with open(self.candlestick_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Open", "High", "Low", "Close", "Volume", "Target"])  # Include 'Target' column

    def save_candle(self, candle):
        """Saves a completed candlestick to the CSV file."""
        with open(self.candlestick_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.datetime.fromtimestamp(candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume'],
                'N/A'  # Placeholder for the 'Target' value
            ])
        self.price_history.append(candle)
        self._update_targets()  # Update targets after saving a new candle

    def load_candlestick_data(self):
        """Loads historical candlestick data from the CSV file."""
        with open(self.candlestick_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.price_history.append({
                    'timestamp': datetime.datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S').timestamp() * 1000,  # Convert to timestamp in milliseconds
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                })

    def get_latest_candles(self, n=1):
        """Returns the latest n candlesticks."""
        return self.price_history[-n:]

    def _update_targets(self):
        """Updates the 'Target' values for candlesticks based on the previous candle's close price."""
        for i in range(len(self.price_history)):
            current_candle = self.price_history[i]

            # Handle the first candle
            """if i == 0:
                if()
                self._update_target_in_csv(i, 'N/A')  # Set target to 'N/A' for the first candle
                continue

            previous_candle = self.price_history[i - 1]

            if current_candle['close'] > previous_candle['close']:
                self._update_target_in_csv(i, 1)  # Update target to 1 (Up)
            else:
                self._update_target_in_csv(i, 0)  # Update target to 0 (Down)"""
            if current_candle['open'] > current_candle['close']:
                self._update_target_in_csv(i, 0)  # Update target to 1 (Up)
            else:
                self._update_target_in_csv(i, 1)

    def _update_target_in_csv(self, index, target):
        """Updates the 'Target' value for a specific row in the CSV file."""
        with open(self.candlestick_file, 'r+', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
            data[index + 1][6] = target  # Convert target to string to avoid any issues
            f.seek(0)  # Go back to the beginning of the file
            writer = csv.writer(f)
            writer.writerows(data)
            f.truncate()  # Truncate the file to the current size

    def identify_patterns(self, candles):
        """Identifies candlestick patterns based on custom logic."""
        patterns = {}

        # Example: Identify bullish engulfing pattern
        patterns['engulfing_bullish'] = self.is_bullish_engulfing(candles[-2], candles[-1])  # Check last two candles

        # Add more custom pattern recognition logic as needed

        return patterns
    
    def is_bullish_engulfing(self, prev_candle, current_candle):
        """Checks if the current and previous candles form a bullish engulfing pattern."""
        return (
            current_candle['close'] > current_candle['open'] and  # Current candle is bullish
            prev_candle['close'] < prev_candle['open'] and  # Previous candle is bearish
            current_candle['close'] > prev_candle['high'] and  # Current close is higher than previous high
            current_candle['open'] < prev_candle['low']  # Current open is lower than previous low
        )

    def prepare_features(self, candles):
        """Prepares features for the model, including candlestick patterns."""
        features = []
        all_pattern_names = ['engulfing_bullish']  # Define all possible pattern names

        for i in range(len(candles)):
            candle = candles[i]
            feature_row = [candle['open'], candle['high'], candle['low'], candle['close'], candle['volume']]

            # Add pattern values (or placeholders) for all patterns
            if i >= 1:  # Only check for patterns if there's a previous candle
                patterns = self.identify_patterns(candles[:i+1])
            else:
                patterns = {}  # No patterns for the first candle

            for pattern_name in all_pattern_names:
                if pattern_name in patterns:
                    feature_row.append(int(patterns[pattern_name]))
                else:
                    feature_row.append(0)  # Add placeholder if pattern not found

            features.append(feature_row)

        return features
        