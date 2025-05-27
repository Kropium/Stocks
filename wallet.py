import json
from logger import logger
from stock import Stock
import time
from datetime import datetime


class VirtualWallet:
    def __init__(self, initial_balance: float = 10000.0, filename: str = "wallet.json", trade_filename: str = "trade_history.json"):
        self.balance: float = initial_balance
        self.stocks: dict[str, dict] = {}
        self.filename = "wallet.json"
        self.trade_history = []  
        self.trade_filename = trade_filename  
        self.sell_cooldowns: dict[str, float] = {}  # New dictionary for sell cooldowns
        self.trailing_stoploss: dict[str, float] = {}  # New dictionary to track trailing stop loss for each stock
        self.load_wallet(filename)
        self.load_trade_history()

    def buy_stock(self, stock: Stock, minutes_ago: int):
        """Simulate buying stock with 15% of the wallet balance."""
        if len(stock.market_data) < minutes_ago + 1:
            logger.warning(f"Not enough market data for {stock.ticker} to retrieve price {minutes_ago} minutes ago.")
            return False

        amount_to_spend = self.balance * 0.15
        if amount_to_spend <= int(200):  
            return False
        current_price = round(stock.get_price("close"), 4)
        logger.info(f"current price is {current_price}")
        logger.debug(f"Price for {stock.ticker} at {minutes_ago} minutes ago: {current_price}")

        quantity = int(amount_to_spend // current_price)

        if quantity > 0:
            total_cost = current_price * quantity

            if total_cost <= self.balance:
                self.balance -= total_cost  
                if stock.ticker in self.stocks:
                    self.stocks[stock.ticker]["quantity"] += quantity
                else:
                    self.stocks[stock.ticker] = {"quantity": quantity, "buy_price": current_price}

                # Initialize or update trailing stop loss for this stock
                self.trailing_stoploss[stock.ticker] = current_price * 0.965 # Set stop loss as 3% below current price

                # Log the purchase
                logger.info(f"Bought {quantity} shares of {stock.ticker} at {current_price} per share.")

                # Record the trade
                trade_entry = {
                    "action": "BUY",
                    "ticker": stock.ticker,
                    "quantity": quantity,
                    "price_per_share": current_price,
                    "total_cost": total_cost,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.trade_history.append(trade_entry)
                self.save_wallet("wallet.json")  # Ensure wallet is saved with updated stoploss
                self.save_trade_history()
                return True
            else:
                logger.warning(f"Not enough balance to buy {quantity} shares of {stock.ticker}.")
                return False
        else:
            logger.warning(f"Insufficient funds to buy at least one share of {stock.ticker}.")
            return False


    def sell_stock(self, stock: Stock):
        if stock.ticker not in self.stocks:
            logger.warning(f"Stock {stock.ticker} not found in portfolio.")
            return False

        stock_data = self.stocks[stock.ticker]
        buy_price = round(stock_data["buy_price"], 3)
        quantity = stock_data["quantity"]
        current_price = stock.get_price("close")
        profit_loss_percentage = (current_price - buy_price) / buy_price

        # Calculate the new trailing stop loss
        new_trailing_stop = current_price * 0.97
        if new_trailing_stop > self.trailing_stoploss.get(stock.ticker, 0):
            self.trailing_stoploss[stock.ticker] = new_trailing_stop  # Update stop loss if the new one is higher
            self.save_wallet("wallet.json")  # Ensure wallet is saved with updated trailing stop loss
            logger.debug(f"Updated trailing stop loss for {stock.ticker} to {self.trailing_stoploss[stock.ticker]:.2f}")

        if current_price <= self.trailing_stoploss[stock.ticker]:
            # Execute the sale
            self.balance += current_price * quantity  
            del self.stocks[stock.ticker]  # Remove stock from portfolio
            del self.trailing_stoploss[stock.ticker]  # Remove the trailing stop loss for the sold stock
            self.sell_cooldowns[stock.ticker] = time.time()  
            logger.info(f"Sold {quantity} shares of {stock.ticker} at {current_price} for a loss of {profit_loss_percentage * 100:.2f}%.")
            
            # Record the trade
            trade_entry = {
                "action": "SELL",
                "ticker": stock.ticker,
                "quantity": quantity,
                "price_per_share": current_price,
                "total_revenue": current_price * quantity,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.trade_history.append(trade_entry)
            self.save_wallet("wallet.json")  # Ensure wallet is saved with updated trailing stop loss
            self.save_trade_history()
            return True

        return False


    def save_wallet(self, filename: str):
        """Save the wallet data to a JSON file."""
        wallet_data = {
            "balance": self.balance,
            "stocks": self.stocks,
            "sell_cooldowns": self.sell_cooldowns,
            "trailing_stoploss": self.trailing_stoploss  # This will now contain all stop losses for each stock
        }
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

            # Load the balance, stocks, and sell cooldowns with default values
            self.balance = wallet_data.get("balance", 10000.0)
            self.stocks = wallet_data.get("stocks", {})
            self.sell_cooldowns = wallet_data.get("sell_cooldowns", {})

            # Optionally, load any new fields (e.g., trailing stop losses) if added
            self.trailing_stoploss = wallet_data.get("trailing_stoploss", {})

            logger.info(f"Wallet loaded from {filename}.")
        
        except FileNotFoundError:
            logger.warning(f"Wallet file {filename} not found. Starting with default balance.")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {filename}. Wallet not loaded.")
        except Exception as e:
            logger.error(f"Error loading wallet: {e}")

    def save_trade_history(self):
        """Save the trade history to a JSON file."""
        try:
            with open(self.trade_filename, "w") as f:
                json.dump(self.trade_history, f, indent=4)
            logger.info(f"Trade history saved to {self.trade_filename}.")
        except Exception as e:
            logger.error(f"Error saving trade history: {e}")

    def check_balance(self):
        """Check current balance."""
        return self.balance

    def check_portfolio(self):
        """Display the current stock portfolio."""
        return self.stocks

    def load_trade_history(self):
        """Load the trade history from a JSON file."""
        try:
            with open(self.trade_filename, "r") as f:
                self.trade_history = json.load(f)
            logger.info(f"Trade history loaded from {self.trade_filename}.")
        except FileNotFoundError:
            logger.warning(f"Trade history file {self.trade_filename} not found. Starting with empty history.")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.trade_filename}. Trade history not loaded.")
        except Exception as e:
            logger.error(f"Error loading trade history: {e}")

    def __repr__(self):
        return f"VirtualWallet(balance={self.balance}, stocks={self.stocks}, trade_history={self.trade_history}, sell_cooldowns={self.sell_cooldowns})"
