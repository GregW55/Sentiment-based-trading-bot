from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta
from finbert_utils import estimate_sentiment
import time  # Using time module for synchronous sleep

API_KEY = "AKVNVTBJ85YWMXTO8YD2"
API_SECRET = "yWOfwxeZIYxbO9tl77vc0CXGdKjbZhtVZxjH1DZU"
BASE_URL = "https://api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET
}

class MLTrader(Strategy):
    def initialize(self, symbol: str = "NVDA", cash_at_risk: float = .95):
        self.symbol = symbol
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        self.stocks_bought = 0

    def position_sizing(self):
        cash = self.get_cash()
        print("Cash:", cash)
        last_price = self.get_last_price(self.symbol)
        quantity = cash * self.cash_at_risk / last_price
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        for ev in news:
            headline = [ev.__dict__["_raw"]["headline"]]
            probability, sentiment = estimate_sentiment(headline)
            print("Headline: ", headline, "Probability: ", probability, "Sentiment: ", sentiment)
        return probability, sentiment

    def on_trading_iteration(self):
        try:
            cash, last_price, quantity = self.position_sizing()
            probability, sentiment = self.get_sentiment()
            if sentiment == "positive" and probability > 0.65:
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price = last_price * 1.30,
                    stop_loss_price = last_price * 0.6
                )
                self.submit_order(order)
                self.stocks_bought += quantity
                print("Buy order placed successfully.")
                time.sleep(60*60*24)  # Sleep for 24 hours
            elif sentiment == "negative" and probability > 0.80 and self.stocks_bought > 0:
                    self.sell_all()
                    print("Sell order placed successfully.")
                    time.sleep(60*15)  # Sleep for 15 minutes
            else:
                print("No trading conditions met. Sleeping for 15 minutes.")
                time.sleep(60*15)  # Sleep for 15 minutes
        except Exception as e:
            print("Error occurred:", str(e))
            print("Sleeping for 15 minutes before trying again.")
            time.sleep(60*15)  # Sleep for 15 minutes before trying again

def main():
    start_date = datetime(2024, 3, 15)
    end_date = datetime(2024, 3, 22)
    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(name='mlstrat', broker=broker,
                        parameters={"symbol": "NVDA", "cash_at_risk": .95})

    trader = Trader()
    trader.add_strategy(strategy)

    while True:
        trader.run_all()
        time.sleep(10)

# Call the function to start the trading bot
if __name__ == "__main__":
    main()
