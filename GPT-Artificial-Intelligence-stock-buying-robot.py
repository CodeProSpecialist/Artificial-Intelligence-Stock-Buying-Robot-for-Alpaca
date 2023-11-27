import yfinance as yf
import os
from transformers import pipeline
from datetime import datetime, timedelta
import re
import alpaca_trade_api as tradeapi
from pytz import timezone
from datetime import time as dt_time
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
    # Include site-specific queries and exclude certain non-stock symbols
    site_query = 'site:google.com'

    gpt_search_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
    print("Searching the internet for stock symbols...\n")

    # Append the site-specific query to the main query
    full_query = query + site_query

    # Set max_length back to the previous value
    search_result = gpt_search_generator(full_query, max_length=150, num_return_sequences=1, temperature=0.7)

    return search_result[0]['generated_text']

# Function to get the price percentage change over the past two days
# Function to get the price change percentage from today's opening price
def get_price_change_percentage(symbol):
    stock_info = yf.Ticker(symbol)

    # Get today's date in the format 'YYYY-MM-DD'
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Get today's opening price
    today_opening_price = stock_info.history(start=today_date, end=today_date)['Open'].iloc[0]

    # Get the current price
    current_price = stock_info.history(period='1d')['Close'].iloc[-1]

    # Calculate percentage change
    price_change_percentage = ((current_price - today_opening_price) / today_opening_price) * 100

    return price_change_percentage

# Function to process GPT-generated search results, extract symbols, and filter by price change
def filter_symbols_by_price_change(search_result, percentage_threshold=0.35):
    # Extract symbols from GPT result
    relevant_symbols = extract_and_validate_symbols_from_gpt_result(search_result)

    # Filter symbols by price change percentage
    symbols_with_increase = [symbol for symbol in relevant_symbols if
                             get_price_change_percentage(symbol) >= percentage_threshold]

    return symbols_with_increase

# Function to extract symbols from GPT search result using regex and validate them
def extract_and_validate_symbols_from_gpt_result(search_result):
    # Define a more specific regex pattern for extracting stock symbols
    symbol_pattern = re.compile(r'\b[A-Z]+\b')  # Adjust as needed

    result_lines = search_result.split('\n')
    extracted_symbols = set()

    for line in result_lines:
        # Find all matches in the line using the symbol_pattern
        symbols_in_line = symbol_pattern.findall(line)

        # Validate each symbol and add valid ones to the set
        for symbol in symbols_in_line:
            if is_valid_stock_symbol(symbol):
                extracted_symbols.add(symbol)

    return list(extracted_symbols)

def is_valid_stock_symbol(symbol):
    try:
        stock_info = yf.Ticker(symbol)
        # Fetch some information to verify if the symbol is valid
        info = stock_info.info
        if info:
            return True
        else:
            return False
    except:
        return False

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
    eastern = timezone('US/Eastern')
    current_time = datetime.now(eastern).time()
    market_open = dt_time(9, 30)
    market_close = dt_time(16, 0)

    return market_open <= current_time <= market_close

# Main trading function
def main():
    while True:
        try:
            # Check if the market is open during Eastern Time
            # comment out the if statement below to run the program outside of market hours
            #if not is_market_open():
            #    print(
            #        "This stock trading robot only works during stock market hours. Waiting for the stock market to open for trading….")
            #    time.sleep(60)
            #    continue

            # Define trading parameters
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            budget_per_stock = 275   # $275 budget per stock

            # Generate a query for GPT-based internet search
            gpt_search_query = "strong buy ETF fund stocks Nasdaq MarketWatch"
            #role_instruction = "Role: stock buyer of strong buy ETF funds or stocks\n"

            print("Searching the internet for successful ETF funds or stocks to purchase with the GPT Artificial Intelligence robot.....")

            # Get the generated search result
            gpt_search_result = generate_internet_search(gpt_search_query)

            # Extract and print all valid stock symbols
            print("List of Valid Stock Symbols:")
            valid_symbols_from_gpt = extract_and_validate_symbols_from_gpt_result(gpt_search_result)
            print(', '.join(valid_symbols_from_gpt))
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

                # Buy stocks for valid symbols within budget
                if has_enough_cash(budget_per_stock) and is_price_within_budget(symbol, budget_per_stock):
                    # Your logic for buying stocks goes here
                    print(f"Buying {symbol}...")
                else:
                    print(f"Not enough cash or price not within budget for {symbol}. Skipping...")

            time.sleep(60)  # Sleep for 60 seconds before the next iteration

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Sleep for 60 seconds before the next iteration

if __name__ == "__main__":
    main()
