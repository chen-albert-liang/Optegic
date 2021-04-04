# Import the client
import requests
import logging
import quandl
import datetime
from DataQuery.Config import TDSession
import pandas as pd
import trading_calendars as tc
import pytz


def get_underlying_price(ticker=None, start_date=None, end_date=None, period_type=str, frequency_type=str, frequency=str, period=None):
    """
    Parameters
    ----------
    ticker
    start_date: datetime.datetime(yyyy, mm, dd)
    end_date: datetime.datetime(yyyy, mm, dd)

    Get underlying stock price from TD Ameritrade developer API

    Example: For a 2 day / 1 min chart, the values would be:
    period: 2
    periodType: day
    frequency: 1
    frequencyType: min

    Start/End date as milliseconds since epoch. If startDate and endDate are provided,
    period should not be provided. Default is previous trading day.

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

    Returns
    -------

    """

    # Daily price endpoint
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker)
    # Define payload
    # start_date = start_date - datetime.timedelta(days=730)  #Pull one additional year of data in order to calculate IV rank

    payload = {'apikey': TDSession.client_id,
               'periodType': period_type,
               'frequencyType': frequency_type,
               'frequency': frequency,
               'period': period,
               'startDate': int(1000 * pd.to_datetime(start_date).timestamp()),
               'endDate': int(1000 * pd.to_datetime(end_date + datetime.timedelta(1)).timestamp()) # Weird timedelta issue with TD query
               # 'needExtendedHourData':'true'
               }

    content = requests.get(url=endpoint, params=payload)
    candle_stick_raw = content.json().get('candles')
    candle_stick_df = pd.DataFrame.from_dict(candle_stick_raw)
    candle_stick_df['datetime'] = pd.to_datetime(candle_stick_df['datetime'], unit='ms')  # Data epoch size = 1 millisecond
    candle_stick_df['Date'] = candle_stick_df['datetime'].dt.date
    candle_stick_df.set_index("Date", inplace=True)
    return candle_stick_df

def get_volatility(ticker="VOL/MSFT", start_date=None, end_date=None, option_type='C'):
    """
    Query volatility data from Quandl API

    Parameters
    ----------
    ticker
    start_date
    end_date
    option_type

    Returns
    -------

    """
    all_vol = quandl.get("VOL/MSFT", authtoken="xUez_b5tyi1WQ8D_WDrh")
    historic_volatility = pd.DataFrame(all_vol['Hv10']).rename(columns={'Hv10':'HV'})

    if option_type == 'C':
        implied_volatility = pd.DataFrame(all_vol['IvCall10']).rename(columns={'IvCall10':'IV'})

    if option_type == 'P':
        implied_volatility = pd.DataFrame(all_vol['IvPut10']).rename(columns={'IvPut10':'IV'})

    historic_volatility = historic_volatility.reset_index(drop=False)
    historic_volatility['Date'] = pd.to_datetime(historic_volatility['Date'])
    historic_volatility.set_index('Date', inplace=True)

    implied_volatility = implied_volatility.reset_index(drop=False)
    implied_volatility['Date'] = pd.to_datetime(implied_volatility['Date'])
    implied_volatility.set_index('Date', inplace=True)
    return implied_volatility, historic_volatility


def get_treasury_rate(start_date=None, end_date=None):

    """
    Free data source from Quandl. No account needed for this data

    Parameters
    ----------
    option_available_date

    Returns
    -------
    risk_free_rate_history_df

    """
    ticker = 'DTB3'  # Default to 3-Month Treasury Rate
    risk_free_rate_history_df = quandl.get("FRED/" + ticker, start_date, end_date)

    if risk_free_rate_history_df.empty:
        logging.error("Unable to get Treasury Rates from Quandl. Please check connection")
        raise IOError("Unable to get Treasury Rate from Quandl")
    logging.info("### Successfully fetched data!!")

    risk_free_rate_history_df = risk_free_rate_history_df.rename(columns={"Value": "rf"})
    risk_free_rate_history_df = risk_free_rate_history_df.reset_index(drop=False)
    risk_free_rate_history_df['Date'] = risk_free_rate_history_df['Date'].dt.date
    risk_free_rate_history_df['rf'] = risk_free_rate_history_df['rf'] / 100.0
    risk_free_rate_history_df['Date'] = pd.to_datetime(risk_free_rate_history_df['Date'])
    risk_free_rate_history_df.set_index('Date', inplace=True)
    return risk_free_rate_history_df


def get_trading_dates(start_date=None, end_date=None):
    """
    Get NYSE trading days

    Parameters
    ----------
    start_date
    end_date

    Returns
    -------
    Trading days on NYSE
    """
    nyse_trading_days = tc.get_calendar('NYSE')
    trading_days_df = pd.DataFrame({'Date':nyse_trading_days.sessions_in_range(pd.Timestamp(start_date, tz=pytz.UTC), pd.Timestamp(end_date, tz=pytz.UTC))})
    trading_days_df['Date'] = pd.to_datetime(trading_days_df['Date']).dt.date
    return trading_days_df


def get_expiration_dates(start_date=None, end_date=None):
    """
    Monthlies expire at the 3rd friday each month on calendar
    Weeklies expire every friday

    Returns
    -------
    expiration_date: list of expiration dates within the start and end dates
    """
    nyse_trading_days = tc.get_calendar('NYSE')
    trading_days = pd.DataFrame({'Date':nyse_trading_days.sessions_in_range(pd.Timestamp(start_date, tz=pytz.UTC), pd.Timestamp(end_date, tz=pytz.UTC))})
    trading_days['Day of the Week'] = trading_days['Date'].dt.day_name()
    trading_days = trading_days[trading_days['Day of the Week']=='Friday'].reset_index(drop=True)
    trading_days['Year-Month'] = pd.to_datetime(trading_days['Date']).dt.to_period('M')
    trading_days['Date'] = pd.to_datetime(trading_days['Date']).dt.date
    trading_days['ind'] = 1
    trading_days['Count'] = trading_days.groupby('Year-Month')['ind'].cumsum()
    expiration_days = trading_days[trading_days['Count']==3].drop(columns=['Count', 'ind']).reset_index(drop=True)
    expiration_days['Expiration'] = 1
    expiration_days = expiration_days.rename(columns={'Date':'Expiration Date'})
    # expiration_days.rename(columns={'Business Day':'Date'}, inplace=True)
    return expiration_days

