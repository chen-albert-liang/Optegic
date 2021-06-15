# Strategic Options
### Use object composition instead of inheritance to reduce the number of data query.

This toolkit provides options traders an easy access to strategy backtesting.

## Basic Concept

### What are options
* Options： are financial derivatives that give buyers the right, but not the obligation, to buy or sell an underlying asset at an agreed-upon price and date.
* Call options： give the option buyer the right, but not the obligation, to buy an underlying security at a specified price within a specified time frame.
* Put options： give holders of the option the right, but not the obligation, to sell a specified amount of an underlying security at a specified price within a specified time frame.
* The stock, bond, or commodity is called the underlying asset.

### Options Value
* Options prices (premiums) = intrinsic value + extrinsic value.
* Intrinsic value: the price difference between the current stock price and the strike price.
* Extrinsic value (time value): the amount of premium above its intrinsic value, which is determined by the implied volatility and time to expiration

