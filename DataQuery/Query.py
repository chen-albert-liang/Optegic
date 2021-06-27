import requests
import logging
import quandl
import pandas as pd

TOKEN = 'Bearer 7Q7QAeBLQYOh1ukJwp50J9u64SAM'


def get_underlying_price(ticker=None, start_date=None, end_date=None, frequency='daily'):
    """
    Parameters
    ----------
    ticker
    start_date: yyyy-mm-dd
    end_date: yyyy-mm-dd
    Get underlying stock price from Tradier developer API

    Returns
    -------

    """
    ticker ='NIO'
    start_date = '2021-01-13'
    end_date = '2021-06-13'
    frequency = 'daily'
    response = requests.get('https://sandbox.tradier.com/v1/markets/history',
                                  params={'symbol': ticker, 'interval': frequency, 'start': start_date,
                                          'end': end_date},
                                  headers={'Authorization': TOKEN, 'Accept': 'application/json'}
                                  )

    if response.status_code == 200:
        market_history_response = response.json()
        market_history_df = pd.DataFrame(market_history_response['history']['day'])
        market_history_df = market_history_df.rename(columns={'date': 'Date'})
        market_history_df.set_index("Date", inplace=True)

        return market_history_df

    return "unable to acquire market history" + str(response.status_code)

# a = get_underlying_price(ticker='DTB3', start_date='2019-01-04', end_date='2021-06-14', frequency='daily')


def get_expiration_dates_strikes(ticker):
    """
    Get expiration dates from Tradier API
    Returns
    -------
    expiration_date: list of future expiration dates given ticker
    """
    response = requests.get('https://sandbox.tradier.com/v1/markets/options/expirations',
                                   params={'symbol': ticker, 'includeAllRoots': 'true', 'strikes': 'true'},
                                   headers={'Authorization': TOKEN, 'Accept': 'application/json'})
    if response.status_code == 200:
        expiration_json = response.json()
        expiration_df = pd.DataFrame(expiration_json['expirations']['expiration'])
        expiration_df = expiration_df.rename(columns={'date': 'Date'})
        expiration_dates = expiration_df['Date']
        strikes_df = pd.DataFrame(list(expiration_df['strikes']))
        expiration_df['strikes'] = strikes_df['strike'].values
        strike_prices = expiration_df.set_index('Date')
        return expiration_dates, strike_prices
    return "Unable to acquire expiration dates and strike prices" + str(response.status_code)

# exp_dates, strike_prices = get_expiration_dates('SPX')


def get_option_chains(ticker, expiration_date):
    response = requests.get('https://sandbox.tradier.com/v1/markets/options/chains',
                            params={'symbol': ticker, 'expiration': expiration_date, 'greeks': 'true'},
                            headers={'Authorization': TOKEN, 'Accept': 'application/json'}
                            )

    if response.status_code == 200:
        json_response = response.json()
        option_chains = pd.DataFrame(json_response['options']['option'])
        option_chains['ask_date'] = pd.to_datetime(option_chains['ask_date'], unit='ms')
        option_chains['bid_date'] = pd.to_datetime(option_chains['bid_date'], unit='ms')
        option_chains['trade_date'] = pd.to_datetime(option_chains['trade_date'], unit='ms')
        greeks = pd.DataFrame(list(option_chains['greeks']))
        option_chains = option_chains.join(greeks).drop(columns='greeks')
        return option_chains

    return "unable to acquire option chain" + str(response.status_code)


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

    
# Probably don't need this anymore
# def get_trading_dates(start_date=None, end_date=None):
#     """
#     Get NYSE trading days
# 
#     Parameters
#     ----------
#     start_date
#     end_date
# 
#     Returns
#     -------
#     Trading days on NYSE
#     """
#     nyse_trading_days = tc.get_calendar('NYSE')
#     trading_days_df = pd.DataFrame({'Date':nyse_trading_days.sessions_in_range(pd.Timestamp(start_date, tz=pytz.UTC), pd.Timestamp(end_date, tz=pytz.UTC))})
#     trading_days_df['Date'] = pd.to_datetime(trading_days_df['Date']).dt.date
#     return trading_days_df
# 

# def get_volatility(ticker="VOL/MSFT", start_date=None, end_date=None, option_type='C'):
#     """
#     Query volatility data from Quandl API
#
#     Parameters
#     ----------
#     ticker
#     start_date
#     end_date
#     option_type
#
#     Returns
#     -------
#
#     """
#     all_vol = quandl.get("VOL/MSFT", authtoken="xUez_b5tyi1WQ8D_WDrh")
#     historic_volatility = pd.DataFrame(all_vol['Hv10']).rename(columns={'Hv10':'HV'})
#
#     if option_type == 'C':
#         implied_volatility = pd.DataFrame(all_vol['IvCall10']).rename(columns={'IvCall10':'IV'})
#
#     if option_type == 'P':
#         implied_volatility = pd.DataFrame(all_vol['IvPut10']).rename(columns={'IvPut10':'IV'})
#
#     historic_volatility = historic_volatility.reset_index(drop=False)
#     historic_volatility['Date'] = pd.to_datetime(historic_volatility['Date'])
#     historic_volatility.set_index('Date', inplace=True)
#
#     implied_volatility = implied_volatility.reset_index(drop=False)
#     implied_volatility['Date'] = pd.to_datetime(implied_volatility['Date'])
#     implied_volatility.set_index('Date', inplace=True)
#     return implied_volatility, historic_volatility
