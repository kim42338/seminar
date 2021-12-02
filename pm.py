import yahoo_fin.stock_info as si
import pandas as pd
import datetime as dt
import numpy as np
import streamlit as st


class PM:
    def __init__(self, tickers, start_date=None, end_date=None):
        self.tickers = [ticker.upper() for ticker in tickers]
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = 0.0125 #make this choosable
    

    @property
    @st.cache(ttl=86400, persist=False)
    def generate_price_df(self):
        price_df = pd.DataFrame()
        tickers = self.tickers
        for ticker in tickers:
            price = si.get_data(ticker, start_date=self.start_date, end_date=self.end_date)
            price_df = pd.concat([price_df, price['adjclose']], axis=1)
        price_df = price_df.set_axis(tickers, axis=1, inplace=False)
        return price_df

    @property
    @st.cache(ttl=86400, persist=False)
    def get_returns(self):
        return np.log(self.generate_price_df / self.generate_price_df.shift(1))

    @property
    @st.cache(ttl=86400, persist=False)
    def get_mean_returns(self):
        return self.get_returns.mean()
    
    @property
    @st.cache(ttl=86400, persist=False)
    def get_covariance(self):
        return self.get_returns.cov()
    
    @property
    @st.cache(ttl=86400, persist=False)
    def get_correlation(self):
        return self.get_returns.corr()

    @property
    @st.cache(ttl=86400, persist=False)
    def generate_random_weights(self):
        weights = np.random.random(len(self.tickers))
        weights /= np.sum(weights)
        return weights

    @property
    @st.cache(ttl=86400, persist=False)
    def calculate_return(self):
        return np.sum(self.generate_random_weights * self.get_mean_return()) * 252
    
    @property
    @st.cache(ttl=86400, persist=False)
    def calculate_volatility(self):
        return np.sqrt(np.dot(self.generate_random_weights.T, np.dot(self.get_covariance, self.generate_random_weights)))

    # @property
    @st.cache(ttl=86400, persist=False)
    def monte_carlo_simulation(self):
        accumulated_return = [] # Returns list
        accumulated_volatility = [] # Volatility list
        accumulated_SR = [] # Sharpe Ratio list
        accumulated_weight = [] # Stock weights list

        predicted_return = self.get_returns
        predicted_return_mean = predicted_return.mean() 
        covariance = predicted_return.cov() * 252
        for i in range(50000):
            # Generate random weights
            weights = np.random.random(len(self.tickers))
            weights /= np.sum(weights)
            
            # Add return using those weights to list
            ret_1 = np.sum(weights * predicted_return_mean) * 252
            accumulated_return.append(ret_1)
            
            # Add volatility or standard deviation to list
            vol_1 = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
            accumulated_volatility.append(vol_1)
            
            # Get Sharpe ratio
            SR_1 = (ret_1 - self.risk_free_rate) / vol_1
            accumulated_SR.append(SR_1)
            
            # Store the weights for each portfolio
            accumulated_weight.append(weights)

        accumulated_return = np.array(accumulated_return)
        accumulated_volatility = np.array(accumulated_volatility)
        accumulated_SR = np.array(accumulated_SR)
        accumulated_weight = np.array(accumulated_weight)
        
        volatility_idx = np.argsort(accumulated_volatility)
        idx = np.argmax(accumulated_SR)

        return accumulated_return.round(4), accumulated_volatility.round(4), accumulated_SR.round(4), accumulated_weight.round(4), volatility_idx, idx
    
