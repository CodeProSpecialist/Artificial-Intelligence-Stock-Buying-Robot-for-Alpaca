import yfinance as yf
import os
from transformers import pipeline
from datetime import datetime, timedelta
import re
import alpaca_trade_api as tradeapi
from pytz import timezone
from datetime import time as dt_time
import time
import requests
from bs4 import BeautifulSoup

# Load environment variables for Alpaca API
APIKEYID = os.getenv('APCA_API_KEY_ID')
APISECRETKEY = os.getenv('APCA_API_SECRET_KEY')
APIBASEURL = os.getenv('APCA_API_BASE_URL')

# Initialize the Alpaca API
api = tradeapi.REST(APIKEYID, APISECRETKEY, APIBASEURL)

global budget_per_stock

budget_per_stock = 275

# Function to get historical price data using yfinance
def get_historical_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

# Function to perform sentiment analysis using transformers library
# Function to perform sentiment analysis using transformers library
def analyze_sentiment(text):
    # Replace 'model_name' with the name of the sentiment analysis model you want to use
    model_name = 'nlptown/bert-base-multilingual-uncased-sentiment'
    sentiment_analyzer = pipeline('sentiment-analysis', model=model_name)
    result = sentiment_analyzer(text)
    return result[0]['label']

# Function to get stock symbols from a website
def get_stock_symbols_marketwatch(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        symbol_elements = soup.select('.element__symbol')
        symbols = [symbol.text.strip() for symbol in symbol_elements]
        return symbols
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None


# Extracted function for generating GPT-based internet searches
def generate_internet_search_with_symbols(query, stock_symbols):
    full_query = f"{query} {' '.join(stock_symbols)} 2023"
    gpt_search_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
    search_result = gpt_search_generator(full_query, max_length=160, num_return_sequences=1, temperature=0.7)
    return search_result[0]['generated_text']

# Function to get the price percentage change over the past two days
def get_price_change_percentage(symbol):
    stock_info = yf.Ticker(symbol)

    today_date = datetime.now().strftime('%Y-%m-%d')
    today_opening_price = stock_info.history(start=today_date, end=today_date)['Open'].iloc[0]
    current_price = stock_info.history(period='1d')['Close'].iloc[-1]
    price_change_percentage = ((current_price - today_opening_price) / today_opening_price) * 100

    return price_change_percentage

# Function to process GPT-generated search results, extract symbols, and filter by price change
def filter_symbols_by_price_change(search_result, percentage_threshold=0.35):
    relevant_symbols = extract_and_validate_symbols_from_gpt_result(search_result)

    symbols_with_increase = [symbol for symbol in relevant_symbols if
                             get_price_change_percentage(symbol) >= percentage_threshold]

    return symbols_with_increase

# Function to extract symbols from GPT search result using regex and validate them
def extract_and_validate_symbols_from_gpt_result(search_result):
    symbol_pattern = re.compile(r'\b[A-Z]+\b')
    result_lines = search_result.split('\n')
    extracted_symbols = set()

    for line in result_lines:
        symbols_in_line = symbol_pattern.findall(line)

        for symbol in symbols_in_line:
            if is_valid_stock_symbol(symbol):
                extracted_symbols.add(symbol)

    return list(extracted_symbols)

def is_valid_stock_symbol(symbol):
    try:
        stock_info = yf.Ticker(symbol)
        info = stock_info.info
        if info:
            return True
            time.sleep(0.5)
        else:
            return False
            time.sleep(0.5)
    except:
        return False

# Function to check if there's enough cash in the Alpaca account
def has_enough_cash(cash_required):
    account_info = api.get_account()
    cash_available = float(account_info.cash)
    return cash_available >= cash_required


# Function to check if the stock price is within the budget
def is_price_within_budget(symbol, budget_per_stock):
    current_price = get_current_price(symbol)
    return current_price <= budget_per_stock


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
            print("")
            print("The Program is running.....")
            print("")
            print("Checking the List of Stock Symbols.....")
            print("")
            # Read stock symbols from a local text file
            with open('list-of-stock-symbols-to-scan.txt', 'r') as file:
                stock_symbols = [symbol.strip() for symbol in file.readlines()]

            if stock_symbols:
                print("List of Valid Stock Symbols: ")
                print(', '.join(stock_symbols))
                print("\n")


                # Generate a query for GPT-based internet search using stock symbols
                gpt_search_query = f"Nasdaq strong buy {' '.join(stock_symbols)} buy now"
                print("Searching the internet for the latest news on the specified stocks with the GPT Artificial Intelligence robot.....")
                print("")

                # Get the generated search result
                gpt_search_result = generate_internet_search_with_symbols(gpt_search_query, stock_symbols)

                # Print the GPT-generated search result
                print(f"Results from GPT internet search:\n{gpt_search_result}\n")

                # Analyze sentiment and decide to buy stocks with positive sentiment
                sentiment = analyze_sentiment(gpt_search_result)
                if sentiment == 'POSITIVE':
                    print("Market sentiment is positive. Considering buying stocks.....")

                    # Buy stocks for each valid symbol
                    for symbol in stock_symbols:
                        if has_enough_cash(budget_per_stock) and is_price_within_budget(symbol, budget_per_stock):
                            print(f"Placing market order for {symbol}.....")
                            api.submit_order(
                                symbol=symbol,
                                qty=1,
                                side='buy',
                                type='market',
                                time_in_force='day',
                            )
                            print(f"Market order for {symbol} placed successfully.")
                        else:
                            print(f"Not enough cash or price not within budget for {symbol}. Skipping.....")

                else:
                    print("Market sentiment is not positive. Skipping stock purchase.")

            time.sleep(60)  # Sleep for 60 seconds before the next iteration

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Sleep for 60 seconds before the next iteration

if __name__ == "__main__":
    main()
