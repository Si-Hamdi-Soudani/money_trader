import numpy as np
import pandas as pd
from keras.src.models import Sequential
from keras.src.layers import LSTM, Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from sklearn.model_selection import train_test_split

from data_manager import DataManager

class ModelTrainer:
    """Trains the model using historical candlestick data."""
    def __init__(self, model_file='models/candlestick_model.h5'):  
            self.model_file = model_file
            self.timesteps = 20  
            self.input_shape = (self.timesteps, 6)
            self.model = self.create_model(self.input_shape)

    def create_model(self, input_shape):
        """Creates an LSTM + CNN hybrid model for candlestick pattern recognition."""
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(Conv1D(64, kernel_size=3, activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Flatten())
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))  # Binary classification
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
    def train_model(self, data_file='data/candlestick_data.csv'):
        """Trains the model using historical candlestick data with a sliding window."""
        # Load data
        data = pd.read_csv(data_file)

        # Prepare features using DataManager
        data_manager = DataManager()
        data_manager.load_candlestick_data()
        X = data_manager.prepare_features(data_manager.price_history)
        
        y = data['Target'].values

        # Create a sliding window to generate sequences
        X_sequences = []
        y_sequences = []
        for i in range(self.timesteps, len(X)):
            X_sequences.append(X[i-self.timesteps:i])
            y_sequences.append(y[i])

        X = np.array(X_sequences)
        y = np.array(y_sequences)

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model 
        self.model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

        # Save the model
        self.model.save(self.model_file)