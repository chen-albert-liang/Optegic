# Import the client
import requests
from DataQuery.Config import TDSession
import pandas as pd

def get_underlying_price(ticker=None, periodType='year', frequencyType='daily', frequency='1', period='5'):
    """
    Example: For a 2 day / 1 min chart, the values would be:
    period: 2
    periodType: day
    frequency: 1
    frequencyType: min

    Valid periods by periodType (defaults marked with an asterisk):
    day: 1, 2, 3, 4, 5, 10*
    month: 1*, 2, 3, 6
    year: 1*, 2, 3, 5, 10, 15, 20
    ytd: 1*

    Valid frequencyTypes by periodType (defaults marked with an asterisk):
    day: minute*
    month: daily, weekly*
    year: daily, weekly, monthly*
    ytd: daily, weekly*

    Valid frequencies by frequencyType (defaults marked with an asterisk):
    minute: 1*, 5, 10, 15, 30
    daily: 1*
    weekly: 1*
    monthly: 1*
    """

    # Daily price endpoint
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker)

    # Define payload
    payload = {'apikey': TDSession.client_id,
               'periodType': periodType,
               'frequencyType': frequencyType,
               'frequency': frequency,
               'period': period,
               'needExtendedHourData':'true'
               }

    content = requests.get(url = endpoint, params = payload)
    candle_stick_raw = content.json().get('candles')
    candle_stick_df = pd.DataFrame.from_dict(candle_stick_raw)
    candle_stick_df['datetime'] = pd.to_datetime(candle_stick_df['datetime'],unit='ms')  # Data epoch size = 1 millisecond

    return candle_stick_df

def get_risk_free_rate():
    rf = 0
    return rf
# def get_implied_volatility_data():
#     return IV