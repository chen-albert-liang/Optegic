import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from scipy.stats import norm
from Functions import OptionPricingModels as OP
from mpl_axes_aligner import align

# Create Class plot_template !!!


class option_visualization(object):
    """
    Visulize the difference between underyling and option returns
    """

    def __init__(self, trading_days, option_price, underlying_price, option_return, underlying_return,
                 implied_volatility, strike, expiry, entry_date, exit_date, lb, ub, option_type, resolution=1):
        self.trading_days = trading_days.index
        self.option_price = option_price
        self.underlying_price = underlying_price
        self.option_return = option_return * 100 # Multiply by 100 for pct. plot purpose
        self.underlying_return = underlying_return * 100 # Multiply by 100 for pct. plot purpose
        self.implied_volatility = implied_volatility
        self.option_type = option_type

        if strike:
            self.spot_plot = np.arange(lb, ub+1, resolution) # Create equal distant spot price value for payoff plot
            self.strike = strike
            self.payoff = pd.DataFrame()
            self.entry_date = entry_date
            self.exit_date = exit_date
            self.toe = (expiry - entry_date).days
            self.holding_period = (exit_date-entry_date).days
            self.strategy_summary = pd.DataFrame()

    # def plot_payoff_table(self):
    #     return

    def _expiry_payoff_calc(self):
        """
        Calculate payoff at expiration

        Returns
        -------

        """
        if self.option_type == 'C':
            payoff_exp = np.maximum(self.spot_plot - self.strike, 0) - self.option_price[0]
        if self.option_type == 'P':
            payoff_exp = np.maximum(self.strike - self.spot_plot, 0) - self.option_price[0]
        return payoff_exp

    def _current_payoff_calc(self):
        """
        Calculate payoff as of right now

        Returns
        -------

        """
        payoff_current = OP.european_vanilla_option(self.spot_plot, self.strike, self.toe,
                                                    self.implied_volatility.values[0, 0], 0.01,
                                                    self.option_type) - self.option_price[0]
        return payoff_current

    def _set_probability_of_profit(self):
        """
        Calculate probability of profit

        Returns
        -------
        Probability of profit
        """
        probability_of_below_strike = norm.cdf(
            np.log(self.strike / self.underlying_price.values[0, 0]) / self.implied_volatility.values[0, 0])

        if self.option_type == 'C':
            probability_of_profit = 1-probability_of_below_strike
        if self.option_type == 'P':
            probability_of_profit = probability_of_below_strike
        return probability_of_profit

    def _set_break_even(self):
        """
        Calculate break even points

        Returns
        -------
        Breakeven prices
        """
        if self.option_type == 'C':
            breakeven = self.strike + self.option_price[0]
        if self.option_type == 'P':
            breakeven = self.strike - self.option_price[0]
        return breakeven

    def plot_payoff(self):
        """
        Payoff plotting

        Returns
        -------

        """
        exp_payoff = self._expiry_payoff_calc()
        cur_payoff = self._current_payoff_calc()
        breakeven = self._set_break_even()
        probability_of_profit = self._set_probability_of_profit()

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.spot_plot,  exp_payoff, 'b', label='Expiration Day')
        ax1.plot(self.spot_plot, cur_payoff, 'r', label='Entry Day')
        ax1.axhline(0, color='k', linestyle=':')

        axis_ymin, axis_ymax = ax1.get_ylim()
        yaxis_breakeven = -axis_ymin/(axis_ymax-axis_ymin)
        ax1.axvline(breakeven, ymin=0, ymax=yaxis_breakeven, color='k', linestyle=':')
        ax1.legend(loc='best')
        ax1.set_xlabel("Spot Price ($)")
        ax1.set_ylabel("Payoff ($)")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        plt.title('Probability of Profit = ' + "{:.1%}".format(probability_of_profit))

    def plot_price_history(self):
        """
        Two scales for each instrument

        Returns
        -------

        """
        fig, ax1 = plt.subplots(2, figsize=(12, 6))
        ax1[0].plot(self.trading_days, self.option_price, 'r-^', label='Option')
        ax2 = ax1[0].twinx()
        ax2.plot(self.trading_days, self.underlying_price['close'], 'b-o', label='Underlying')
        ax1[0].legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1[0].spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1[0].set_xlabel("Date")
        ax1[0].set_ylabel("Option Price")
        ax2.set_ylabel("Underlying Price")
        ax1[1].plot(self.trading_days, self.implied_volatility, 'b-', label='Implied Volatility')
        ax1[1].set_xlabel("Date")
        ax1[1].set_ylabel("Implied Volatility (Call)")
        ax1[1].legend(loc="upper right")
        ax1[1].spines['top'].set_visible(False)
        ax1[1].spines['right'].set_visible(False)
        plt.title('Price and IV Move')

    def plot_option_pnl(self):
        """
        Plot holding period return

        Returns
        -------

        """
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.trading_days,  self.option_return, 'r-^', label='Option')
        ax1.axhline(0, color='k', linestyle=':')
        ax2 = ax1.twinx()
        ax2.plot(self.trading_days, self.underlying_return, 'b-o', label='Underlying')
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Option P&L")
        ax2.set_ylabel("Underlying P&L")
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

        # Align y-axes
        org1 = 0.0  # Origin of first axis
        org2 = 0.0  # Origin of second axis
        pos = 0.5  # Position the two origins are aligned
        align.yaxes(ax1, org1, ax2, org2, pos)
        plt.tight_layout()
        plt.title('Holding Period Return')

    def print_strategy_summary(self):
        """
        Strategy synthesis

        Returns
        -------

        """
        duration = self.holding_period
        cost = 100*self.option_price[0]
        residule = 100*self.option_price[-1]
        pnl = residule - cost
        pnl_per_day = pnl / duration
        roc = residule/cost - 1
        win = roc>0
        self.strategy_summary = pd.DataFrame([[self.entry_date.date(), "${:.2f}".format(cost),
                                               self.exit_date.date(), duration,
                                               "${:.2f}".format(residule), "${:.2f}".format(pnl),
                                               "${:.2f}".format(pnl_per_day), "{:.1%}".format(roc), win]],
                                             columns=['Entry Date', 'Cost Basis', 'Exit Date', 'Holding Period (Days)',
                                                      'Residual Value', 'P&L', 'PnL/Day', 'ROC', 'Win'])

    # def plot_option_drawdown(self):
    #     fig, ax = plt.subplots()
    #     ax_option, ax_underlying = ax.plot(self.trading_days, self.option_drawdown, 'r-^', self.trading_days,
    #                                        self.underlying_drawdown, 'b-o')
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.legend((ax_option, ax_underlying), ('Option Price', 'Underlying Price'))
    #     ax.yaxis.set_major_formatter(mtick.PercentFormatter())