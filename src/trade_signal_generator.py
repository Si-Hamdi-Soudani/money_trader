import os
import random
import numpy as np
import pandas as pd
from keras.src.saving import load_model
import datetime
import pytz

# Define Tunisian time zone
tunisia_tz = pytz.timezone('Africa/Tunis')
class TradeSignalGenerator:
    def __init__(self, model_file='models/candlestick_model.h5', data_manager=None):
        self.model = load_model(model_file) if os.path.exists(model_file) else None
        self.data_manager = data_manager
        self.q_table = {}  # Initialize the Q-table
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.1

    def generate_trade_signal(self):
        if self.model is None:
            print("Model is not loaded. Cannot generate trade signal.")
            return None

        # Get the latest candlestick data
        latest_candles = self.data_manager.get_latest_candles(n=20)  # Assuming a lookback period of 20 candles
        if not latest_candles:
            return None

        # Prepare data for prediction (assuming features are in data_manager)
        X = self.data_manager.prepare_features(latest_candles)
        num_features = len(X[0])  # Get the actual number of features
        X = np.array(X).reshape((1, 20, num_features))  

        # Predict the next movement
        prediction = self.model.predict(X)[0][0]  # Assuming binary classification (Up/Down)
        state = self.get_state(latest_candles)  # Define a method to get the state from candles
        
        # Set a confidence threshold
        confidence_threshold = 0.6  # Example threshold
        print("Prediction",prediction )
        if prediction > confidence_threshold:
            action = 'Up'
        elif prediction < (1 - confidence_threshold):
            action = 'Down'
        else:
            print("Confidence below threshold. No trade signal generated.")
            return None
        action = self.choose_action(state) 
        # Determine entry time and timeframe
        entry_time = datetime.datetime.now(tunisia_tz) + datetime.timedelta(minutes=1)
        entry_time = entry_time.replace(second=0, microsecond=0)  # Ensure whole minute
        timeframe = np.random.choice([1, 2, 5])  # Example timeframes in minutes

        return {
            'entry_time': entry_time,
            'win_rate_percentage': prediction * 100,  # Assuming prediction is the probability of 'Up'
            'timeframe': timeframe,
            'action': action
        }

    def get_state(self, candles):
        """Define a method to extract a state representation from candlestick data."""
        # Example: You could use the last closing price or a combination of features.
        return candles[-1]['close'] 
    
    def choose_action(self, state):
        """Chooses an action based on the Q-table and exploration rate."""
        if state not in self.q_table:
            self.q_table[state] = {'Up': 0, 'Down': 0}  # Initialize Q-values for new states

        if random.random() < self.exploration_rate:
            return random.choice(['Up', 'Down'])  # Explore
        else:
            return max(self.q_table[state], key=self.q_table[state].get)  
        
    def update_q_table(self, state, action, reward, next_state):
        """Updates the Q-table based on the reward received."""
        if next_state not in self.q_table:
            self.q_table[next_state] = {'Up': 0, 'Down': 0}

        best_next_action = max(self.q_table[next_state], key=self.q_table[next_state].get)
        self.q_table[state][action] += self.learning_rate * (
            reward + self.discount_factor * self.q_table[next_state][best_next_action] - self.q_table[state][action]
        )