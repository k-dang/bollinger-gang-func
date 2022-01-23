import yfinance as yf
import pandas as pd
from datetime import datetime
# technical analyis library
from ta.volatility import BollingerBands

# internal modules
import discord_helpers as dh

class BollingerChecker:
    def __init__(self):
        self.list_of_potentials = []

    def check_ticker(self, ticker):
        ticker_data = yf.Ticker(ticker)
        df = pd.DataFrame(ticker_data.history(period="2mo"))
        # check if we have latest info
        # if ((df.iloc[-1].name.day != datetime.today().day) or (len(df) < 30)):
        if (len(df) < 30):
            # retry ? a few times?
            print(f'missing data from yahoo for {ticker}')
            return

        indicator_bb = BollingerBands(close=df["Close"], window=20, window_dev=2)

        # Add Bollinger Bands features
        df['bb_bbm'] = indicator_bb.bollinger_mavg()
        df['Upper Band'] = indicator_bb.bollinger_hband()
        df['Lower Band'] = indicator_bb.bollinger_lband()
        df.dropna(inplace=True)

        current_price = ticker_data.info['regularMarketPrice']
        upper_price = df.iloc[-1]['Upper Band']
        lower_price = df.iloc[-1]['Lower Band']

        # body = {'content': f'{ticker}: {current_price}, {upper_price}, {lower_price}'}

        if (self.is_past_upper_threshold(current_price, upper_price)):
            latest_option_date = ticker_data.options[0]
            opt = ticker_data.option_chain(latest_option_date)
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

        if (self.is_past_lower_threshold(current_price, lower_price)):
            latest_option_date = ticker_data.options[0]
            opt = ticker_data.option_chain(latest_option_date)
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

    def is_past_upper_threshold(self, price, upper_band_price):
        """
        checks if the price is past the upper band or is within 1% of the upper band
        """
        upper_current_threshold = price * 1.01
        return (price > upper_band_price) or (upper_current_threshold > upper_band_price)

    def is_past_lower_threshold(self, price, lower_band_price):
        """
        checks if the price is past the lower brand or is within 1% of the lower band 
        """
        lower_current_threshold = price * 0.99
        return (price < lower_band_price) or (lower_current_threshold < lower_band_price)