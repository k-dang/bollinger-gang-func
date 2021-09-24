import yfinance as yf
import pandas as pd
from datetime import datetime

# internal modules
import discord_helpers as dh

class BollingerChecker:
    def __init__(self):
        self.list_of_potentials = []

    def check_ticker(self, ticker):
        myTicker = yf.Ticker(ticker)
        df = pd.DataFrame(myTicker.history(period="2mo"))
        # check if we have latest info
        # if ((df.iloc[-1].name.day != datetime.today().day) or (len(df) < 30)):
        if (len(df) < 30):
            # retry ? a few times?
            print(f'missing data from yahoo for {ticker}')
            return

        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['STD_20'] = df['Close'].rolling(window=20).std()
        df['Upper Band'] = df['SMA_20'] + (2 * df['STD_20'])
        df['Lower Band'] = df['SMA_20'] - (2 * df['STD_20'])
        df.dropna(inplace=True)

        current_price = myTicker.info['regularMarketPrice']
        upper_price = df.iloc[-1]['Upper Band']
        lower_price = df.iloc[-1]['Lower Band']

        # body = {'content': f'{ticker}: {current_price}, {upper_price}, {lower_price}'}

        # upper bound checks
        # upper_diff = current_price - upper_price
        # get 1% increase of current price
        upper_current_threshold = current_price * 1.01
        if ((current_price > upper_price) or (upper_current_threshold > upper_price)):
            latest_option_date = myTicker.options[0]
            opt = myTicker.option_chain(latest_option_date)
            calls_df = opt.calls
            top_10_calls_df = calls_df[calls_df['strike'] > upper_price].iloc[:10][['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility']]
            self.list_of_potentials.append([
                {
                    'name': ticker,
                    'value': 'Sell CALLS'
                },
                {
                    'name': 'Passed Upper band or within 1%',
                    'value': f'Current: {current_price} \n Upper: {upper_price}'
                },
                {
                    'name': dh.get_options_columns_string(top_10_calls_df.columns),
                    'value': dh.get_options_table_string(top_10_calls_df.values)
                }
            ])

        # lower bound checks
        # lower_diff = lower_price - current_price
        # get 1% drop of current price
        lower_current_threshold = current_price * 0.99
        if ((current_price < lower_price) or (lower_current_threshold < lower_price)):
            latest_option_date = myTicker.options[0]
            opt = myTicker.option_chain(latest_option_date)
            puts_df = opt.puts
            top_10_puts_df = puts_df[puts_df['strike'] < lower_price].iloc[-10:][['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility']]
            self.list_of_potentials.append([
                {
                    'name': ticker,
                    'value': 'Sell PUTS'
                },
                {
                    'name': 'Passed Lower band or within 1%',
                    'value': f'Current: {current_price} \n Lower: {lower_price}'
                },
                {
                    'name': dh.get_options_columns_string(top_10_puts_df.columns),
                    'value': dh.get_options_table_string(top_10_puts_df.values)
                }
            ])