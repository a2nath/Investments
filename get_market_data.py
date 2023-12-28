import sys
import requests
import json
import pdb
import csv
import argparse
from private_keys import headers
from datetime import datetime, timedelta
from math import ceil


default_file = "dividends_list.csv"
dividend_timespan = 365

# caches to speed up repeated query
ticker_costs = {}
dividend_cache = {}
dividend_state = {}

def getNames():
	names = []
	with open(default_file) as csv_file:
		csv_reader = csv.reader(csv_file)
		for row in csv_reader:
			names.append(row[0])
	return names, len(names)

def get_dividend_data(ticker_symbol, start_date, end_date):

	# Yahoo Finance API endpoint for dividends
	url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-historical-data?frequency=1d&filter=dividends&period1={start_date}&period2={end_date}&symbol={ticker_symbol}"

	# Make the request
	response = requests.get(url, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:

		# Assuming the API response is in JSON format
		data = response.json()

		# Extract dividend values from the API response
		dividends = [entry['amount'] for entry in data.get('eventsData', []) if 'type' in entry and entry['type'] == 'DIVIDEND']

		# Calculate the mean of dividends
		mean_dividend = 0

		#dsum = sum(dividends)
		#print (f"sum {dsum}")

		if len(dividends) > 0:
			mean_dividend = sum(dividends) / len(dividends)

		return len(dividends), mean_dividend
	else:
		print(f"Failed to fetch dividend data for {ticker_symbol}. Status code: {response.status_code}")
		return 0, 0


def print_dividend_data(ticker_symbol, start_date, end_date):

	if ticker_symbol not in dividend_cache:
		size, mean_dividend = get_dividend_data(ticker_symbol, start_date, end_date)
		dividend_cache[ticker_symbol] = mean_dividend
		dividend_state[ticker_symbol] = size

	print(f"{ticker_symbol}\t{round(dividend_cache[ticker_symbol],2)}")


def print_reinvestment_data(ticker_symbol, start_date, end_date):

	if ticker_symbol not in dividend_cache:
		size, mean_dividend = get_dividend_data(ticker_symbol, start_date, end_date)
		dividend_cache[ticker_symbol] = mean_dividend
		dividend_state[ticker_symbol] = size

	if dividend_state[ticker_symbol] > 0:
		mean_div = dividend_cache[ticker_symbol]

		if mean_div > 0:
			if ticker_symbol not in ticker_costs:
				ticker_costs[ticker_symbol] = getPrice(ticker_symbol)

			current_price = ticker_costs[ticker_symbol]
			share_count = current_price / mean_div
			drip_amount = ceil(share_count) * current_price

			print(f"{ticker_symbol}\t{round(drip_amount,2)}")
		else:
			print(f"{ticker_symbol}\tno dividends")
	else:
		print(f"{ticker_symbol}\tno dividend data")


def getPrice(ticker_symbol):

	# Yahoo Finance API endpoint for current price
	url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes?region=US&symbols={ticker_symbol}"

	# Make the request using requests.get
	response = requests.get(url, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Assuming the API response is in JSON format
		data = response.json()

		# Extract current price from the API response

		current_price = data.get('quoteResponse', {}).get('result', [])[0].get('regularMarketPrice', {})

		if type(current_price) == float and current_price > 0:
			return current_price
	else:
		print(f"Failed to fetch price data for {ticker_symbol}. Status code: {response.status_code}")

	return -1

def print_current_price(ticker_symbol):

	if ticker_symbol not in ticker_costs:
		ticker_costs[ticker_symbol] = getPrice(ticker_symbol)

	print(f"{ticker_symbol}\t{round(ticker_costs[ticker_symbol],2)}")


def main():

	# ticker symbols to work with
	symbols_list = []
	dividend_list = []
	reinvestment_list = []

	parser = argparse.ArgumentParser("Get market data")
	parser.add_argument("-t", "--ticker_symbol", help="list of ticker symbols to query prices", nargs="+", type=str)
	parser.add_argument("-d", "--dividends", help="list of ticker symbols to get mean dividends info for", nargs="+", type=str)
	parser.add_argument("-y", "--last_n_years", help="year in which to get mean dividends from, default [1] = last 365 days from today", type=int, default=1)
	parser.add_argument("-i", "--period_years", help="interval period to query. if interval is bigger than years, then it will query period length, default [1] = 365 days to average over since last_n_years", type=int, default=1)
	parser.add_argument("-r", "--drip_amount", help="amount needed to reinvest the dividend to buy more share(s)", nargs="+", type=str)

	args = parser.parse_args()

	print("\nSettings as follows:")
	print("-------------------------------------------------------")

	arguments = vars(args);
	for arg in arguments:
		print(arg, '\t', getattr(args, arg))


	if args.ticker_symbol is None and args.dividends is None and args.drip_amount is None:
		symbols_list, count = getNames()
		print("Found ", count, f" names from {default_file}")
	else:
		if args.ticker_symbol is not None:
			for symbol in args.ticker_symbol:
				symbols_list.append(symbol)

		if args.dividends is not None:
			for symbol in args.dividends:
				dividend_list.append(symbol)

		if args.drip_amount is not None:
			for symbol in args.drip_amount:
				reinvestment_list.append(symbol)

	if len(symbols_list) > 0:
		print("\nStock price now ", datetime.now())
		print("-------------------------------------------------------")

	# simple cost of the security now
	for ticker_symbol in symbols_list:
		print_current_price(ticker_symbol)

	# dividend information
	if len(dividend_list) > 0:
		# Set the time range for the past year
		start_date = datetime.now() - timedelta(days=dividend_timespan * max(args.last_n_years, args.period_years))
		end_date = start_date + timedelta(days=dividend_timespan * args.period_years)

		# Format dates for the Yahoo Finance API
		start_date_str = int(start_date.timestamp())
		end_date_str = int(end_date.timestamp())

		print(f"\nMean dividend over {args.period_years} year(s) since {args.last_n_years} year(s):")
		print("-------------------------------------------------------")

		for ticker_symbol in dividend_list:
			print_dividend_data(ticker_symbol, start_date_str, end_date_str)

	# how much capital to get drip going
	if len(reinvestment_list) > 0:
		end_date = datetime.now()
		start_date = datetime.now() - timedelta(days=dividend_timespan * 1)

		# Format dates for the Yahoo Finance API
		start_date_str = int(start_date.timestamp())
		end_date_str = int(end_date.timestamp())

		print(f"\nDrip amount from dividends over {args.period_years} year(s) since {args.last_n_years} year(s):")
		print("-------------------------------------------------------")

		for ticker_symbol in reinvestment_list:
			print_reinvestment_data(ticker_symbol, start_date_str, end_date_str)



if __name__ == "__main__":
	main()
