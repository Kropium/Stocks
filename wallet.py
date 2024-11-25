import json
from logger import logger
from stock import Stock
import time


class VirtualWallet:
    def __init__(self, initial_balance: float = 10000.0, filename: str = "wallet.json"):
        self.balance: float = initial_balance
        self.stocks: dict[str, dict] = {}
        self.filename = "wallet.json"
        self.load_wallet(filename)

    def buy_stock(self, stock: Stock, minutes_ago: int):
        """Simulate buying stock with 10% of the wallet balance."""

        if len(stock.market_data) < minutes_ago + 1:
            logger.warning(
                f"Not enough market data for {stock.ticker} to retrieve price {minutes_ago} minutes ago."
            )
            return False

        amount_to_spend = self.balance * 0.15

        current_price = stock.get_price("Close")
        logger.info(f"current price is {current_price}")
        # Log the fetched price for debugging purposes
        logger.debug(f"Price for {stock.ticker} at {minutes_ago} minutes ago: {current_price}")

        # Calculate how many shares we can buy with the amount_to_spend
        quantity = int(amount_to_spend // current_price)

        if quantity > 0:
            total_cost = current_price * quantity

            # Check if we have enough balance to make the purchase
            if total_cost <= self.balance:
                self.balance -= total_cost  # Subtract the cost of the purchase

                # Add or update stock in the portfolio
                if stock.ticker in self.stocks:
                    self.stocks[stock.ticker]["quantity"] += quantity
                else:
                    self.stocks[stock.ticker] = {"quantity": quantity, "buy_price": current_price}

                # Log the purchase
                logger.info(
                    f"Bought {quantity} shares of {stock.ticker} at {current_price} per share."
                )

                self.save_wallet("wallet.json")
                return True
            else:
                logger.warning(f"Not enough balance to buy {quantity} shares of {stock.ticker}.")
                return False
        else:
            logger.warning(f"Insufficient funds to buy at least one share of {stock.ticker}.")
            return False

    def sell_stock(
        self, stock: Stock, profit_threshold: float = 0.1, loss_threshold: float = 0.05
    ):
        if stock.ticker not in self.stocks:
            logger.warning(f"Stock {stock.ticker} not found in portfolio.")
            return False

        stock_data = self.stocks[stock.ticker]
        buy_price = stock_data["buy_price"]
        quantity = stock_data["quantity"]

        current_price = stock.get_price("Close")
        profit_loss_percentage = (current_price - buy_price) / buy_price

        if profit_loss_percentage >= profit_threshold:
            self.balance += current_price * quantity
            del self.stocks[stock.ticker]
            logger.info(
                f"Sold {quantity} shares of {stock.ticker} at {current_price} for a profit."
            )
            self.save_wallet("wallet.json")
            return True

        elif profit_loss_percentage <= -loss_threshold:
            self.balance += current_price * quantity
            del self.stocks[stock.ticker]
            logger.info(f"Sold {quantity} shares of {stock.ticker} at {current_price} for a loss.")
            self.save_wallet("wallet.json")
            return True

        return False

    def check_balance(self):
        """Check current balance."""
        return self.balance

    def check_portfolio(self):
        """Display the current stock portfolio."""
        return self.stocks

    def calculate_total_value(self, stock: Stock):
        """Calculate the total value of the stocks owned in the portfolio."""
        total_value = 0
        for ticker, data in self.stocks.items():
            if ticker == stock.ticker:
                current_price = stock.raw_market_data["Close"].iloc[-1]
                total_value += current_price * data["quantity"]
        return total_value

    def save_wallet(self, filename: str):
        """Save the wallet data to a JSON file."""
        wallet_data = {"balance": self.balance, "stocks": self.stocks}
        try:
            with open(filename, "w") as f:
                json.dump(wallet_data, f, indent=4)
            logger.info(f"Wallet saved to {filename}.")
        except Exception as e:
            logger.error(f"Error saving wallet: {e}")

    def load_wallet(self, filename: str):
        """Load the wallet data from a JSON file."""
        try:
            with open(filename, "r") as f:
                wallet_data = json.load(f)
            self.balance = wallet_data.get("balance", 10000.0)
            self.stocks = wallet_data.get("stocks", {})
            logger.info(f"Wallet loaded from {filename}.")
        except FileNotFoundError:
            logger.warning(f"Wallet file {filename} not found. Starting with default balance.")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {filename}. Wallet not loaded.")
        except Exception as e:
            logger.error(f"Error loading wallet: {e}")

    def __repr__(self):
        return f"VirtualWallet(balance={self.balance}, stocks={self.stocks})"
