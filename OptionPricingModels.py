"""
https://aaronschlegel.me/black-scholes-formula-python.html
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

def european_vanilla_option(p, s, T, sigma, r, option_type='C'):
    """
    Non-dividend paying stock option pricing model

    Parameters
    ----------
    p: spot price
    s: strike price
    T: days to expiration
    sigma: volatility of underlying asset
    r: short interest rate

    Returns
    -------
    option_price: theoretical price given implied volatility

    """

    t = T/365 # Convert DTE to % of a year
    d1 = (np.log(p / s) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
    d2 = (np.log(p / s) + (r - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))

    if option_type=='C':
        option_price = p * norm.cdf(d1, 0.0, 1.0) - s * np.exp(-r * t) * norm.cdf(d2, 0.0, 1.0)
    if option_type=='P':
        option_price = s * np.exp(-r * t) * norm.cdf(-d2, 0.0, 1.0) - p * norm.cdf(-d1, 0.0, 1.0)
    return option_price

def probability_of_profit(strike, spot, option_price, current_volatility, option_type='C'):
    if option_type=='C':
        pop = norm.cdf(np.log((strike + option_price) / spot) / current_volatility)
    if option_type == 'C':
        pop = norm.cdf(np.log((strike + option_price) / spot) / current_volatility)
    return pop
def greeks_calc():
    return

def european_vanilla_option_with_dividend(p, s, T, sigma, div, r, option_type='C'):
    """
    Non-dividend paying stock option pricing model

    Parameters
    ----------
    p: spot price
    s: strike price
    t: time to maturity
    nu: volatility of underlying asset
    div: dividend rate
    r: short interest rate

    Returns
    -------
    option_price: theoretical price given implied volatility

    """
    t = T/365

    d1 = (np.log(p / s) + (r - div + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
    d2 = (np.log(p / s) + (r - div - 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))

    if option_type == 'C':
        option_price = p * np.exp(-div * T) * norm.cdf(d1, 0.0, 1.0) - s * np.exp(-r * T) * norm.cdf(d2, 0.0, 1.0)

    if option_type == 'P':
        option_price = s * np.exp(-r * t) * norm.cdf(-d2, 0.0, 1.0) - p * np.exp(-div * t) * norm.cdf(-d1, 0.0, 1.0)

    return option_price


# def american_option()
# def american_option_with_dividend()