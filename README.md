# Sentiment-based-trading-bot
Trading bot built around getting the sentiment of the news
uses position sizing function to determine how much of the stock it can buy, getting the cash, the last price of the symbol and then calculating the quantity off those numbers(and returning all of these variables)
uses Timedelta to get todays date to calculate the news for today and the days prior
uses the finbert utils model to get a sentiment(the tensor, and probability) of the news, for example it could be positive and 90% or neutral and 40%.

using the variables and sentiment before, the trading loop is very simple.
getting the variables needs, if the sentiment is postive and its 65% probably its positive(you can adjust this number to your liking 99% works but for small amounts of news on a single symbol like NNVDA it was taking a long time to see any actions, then you want to buy up as much stock as possible(95% of total cash can also lower this value to your liking)
it will do the same for negative sentiment except it will sell all of the stock it has purchased

this simple method proves very effective over the backtest period of 4 years, giving a total return of 1000% much higher than the base!
