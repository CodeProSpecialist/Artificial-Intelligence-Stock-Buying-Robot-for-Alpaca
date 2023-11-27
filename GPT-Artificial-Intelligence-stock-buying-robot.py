import os
from transformers import pipeline
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime, timedelta, time as dt_time
import pytz
import time

# Load environment variables for Alpaca API
APIKEYID = os.getenv('APCA_API_KEY_ID')
APISECRETKEY = os.getenv('APCA_API_SECRET_KEY')
APIBASEURL = os.getenv('APCA_API_BASE_URL')

# Initialize the Alpaca API
api = tradeapi.REST(APIKEYID, APISECRETKEY, APIBASEURL)


# Function to get historical price data using yfinance
def get_historical_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data


# Function to perform sentiment analysis using transformers library
def analyze_sentiment(text):
    sentiment_analyzer = pipeline('sentiment-analysis')
    result = sentiment_analyzer(text)
    return result[0]['label']


# Function to generate GPT-based internet searches
def generate_internet_search(query, role_instruction):
    gpt_search_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
    print("Searching the internet for stock symbols...\n")
    search_result = gpt_search_generator(role_instruction + "\n" + query, max_length=150, num_return_sequences=1,
                                         temperature=0.7)
    return search_result[0]['generated_text']


# Function to get the price percentage change over the past two days
def get_price_change_percentage(symbol):
    stock_info = yf.Ticker(symbol)
    historical_data = stock_info.history(period='2d')['Close']

    # Calculate percentage change
    price_change_percentage = (historical_data.iloc[-1] - historical_data.iloc[0]) / historical_data.iloc[0] * 100

    return price_change_percentage


# Function to process GPT-generated search results, extract symbols, and filter by price change
def filter_symbols_by_price_change(search_result, percentage_threshold=1.0):
    # Extract symbols from GPT result
    relevant_symbols = extract_symbols_from_gpt_result(search_result)

    # Filter symbols by price change percentage
    symbols_with_increase = [symbol for symbol in relevant_symbols if
                             get_price_change_percentage(symbol) >= percentage_threshold]

    return symbols_with_increase


# Function to extract symbols from GPT search result
def extract_symbols_from_gpt_result(search_result):
    result_lines = search_result.split('\n')
    relevant_symbols = []

    for line in result_lines:
        if 'Symbol' in line:
            symbol = line.split('Symbol:')[1].split(',')[0].strip()
            relevant_symbols.append(symbol)

    return relevant_symbols


# Function to check if there's enough cash in the Alpaca account
def has_enough_cash(cash_required):
    account_info = api.get_account()
    cash_available = float(account_info.cash)
    return cash_available >= cash_required


# Function to check if the stock price is within the budget
def is_price_within_budget(symbol, budget):
    current_price = get_current_price(symbol)
    return current_price <= budget


# Function to get the current price of a stock symbol
def get_current_price(symbol):
    stock_info = yf.Ticker(symbol)
    current_price = stock_info.history(period='1d')['Close'].iloc[-1]
    return current_price


# Function to check if the current time is within stock market hours (Eastern Time)
def is_market_open():
    eastern = pytz.timezone('US/Eastern')
    current_time = datetime.now(eastern).time()
    market_open = dt_time(9, 30)
    market_close = dt_time(16, 0)

    return market_open <= current_time <= market_close


# Main trading function
def main():
    while True:
        try:
            # Check if the market is open during Eastern Time
            if not is_market_open():
                print(
                    "This stock trading robot only works during stock market hours. Waiting for the stock market to open for trading….")
                time.sleep(60)
                continue

            # Define trading parameters
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            budget_per_stock = 275   # $275 budget per stock

            # Generate a query for GPT-based internet search
            gpt_search_query = "strong buy ETF fund stocks Nasdaq MarketWatch"
            role_instruction = "Role: stock buyer of strong buy ETF funds or stocks\n"

            print("Searching the internet for successful ETF funds or stocks to purchase with the GPT Artificial Intelligence robot.....")

            # Get the generated search result
            gpt_search_result = generate_internet_search(gpt_search_query, role_instruction)

            # Extract and print all stock symbols
            print("List of Stock Symbols Extracted:")
            symbols_from_gpt = extract_symbols_from_gpt_result(gpt_search_result)
            print(', '.join(symbols_from_gpt))
            print("\n")

            # Print the GPT-generated search result
            print(f"Results from GPT internet search:\n{gpt_search_result}\n")

            # Process the search result to extract relevant stock symbols and filter by price change
            symbols_with_increase = filter_symbols_by_price_change(gpt_search_result)

            # Print the list of symbols with current price and percentage of price change for today
            print("\nList of Symbols with Increase:")
            for symbol in symbols_with_increase:
                current_price = get_current_price(symbol)
                price_change_percentage = get_price_change_percentage(symbol)
                print(
                    f"Symbol: {symbol}, Current Price: {current_price:.2f}, Percentage Change: {price_change_percentage:.2f}%")

            # Check if there are symbols with an increase
            if symbols_with_increase:
                for symbol in symbols_with_increase:
                    # Check if the stock price is within the budget and we have enough cash
                    if is_price_within_budget(symbol, budget_per_stock) and has_enough_cash(budget_per_stock):
                        # Implement your trading strategy based on the extracted information
                        # Example: Execute a buy order for each relevant symbol with a price increase
                        api.submit_order(
                            symbol=symbol,
                            qty=1,  # Buy only 1 share
                            side='buy',
                            type='market',
                            time_in_force='day'  # Set time_in_force to 'day'
                        )
                        print(f"Buy order placed for {symbol}.\n")
                    else:
                        print(f"Not enough cash or stock price exceeds the budget for {symbol}.\n")
            else:
                print("Not enough symbols with an increase. Waiting for the next iteration.\n")

        except Exception as e:
            print(f"An error occurred: {e}. Restarting in 5 seconds...\n")
            time.sleep(5)

        time.sleep(60)  # Repeat every 60 seconds


# Run the main function
if __name__ == "__main__":
    main()