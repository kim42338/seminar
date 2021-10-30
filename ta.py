import yahoo_fin.stock_info as si
import streamlit as st

class TA:
    def __init__ (self, ticker, start_date=None, end_date=None, period=14):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
    
    @property
    @st.cache(ttl=86400, persist=False)
    def get_price_df(self):
        price_df = si.get_data(self.ticker, start_date=self.start_date, end_date=self.end_date)
        return price_df

    def calculate_rsi(self):
        price_df = self.get_price_df['adjclose'].diff(1)
        price_df = price_df.dropna()
        up = price_df.copy()
        down = price_df.copy()

        up[up<0] = 0
        down[down>0] = 0

        avg_gain = up.rolling(window=self.period).mean()
        avg_loss = abs(down.rolling(window=self.period).mean())

        rsi = 100 - (100 / (1 + (avg_gain/avg_loss)))

        return rsi
    


