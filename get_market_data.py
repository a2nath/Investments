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
			names.append(row[0].upper())
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

		if dividends:
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

	payout_amount = dividend_cache[ticker_symbol] * dividend_state[ticker_symbol]
	print(f"{ticker_symbol}\tper payout:{round(dividend_cache[ticker_symbol],2)},total payout:{round(payout_amount,2)}")


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

			print(f"{ticker_symbol}\tdrip amount:{round(drip_amount,2)},buy shares:{ceil(share_count)},per payout:{round(mean_div, 2)},cost per share:{round(current_price, 2)} ")
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
	parser.add_argument("-t", "--ticker_symbol", help="list of ticker symbols to query prices", nargs='*', type=str)
	parser.add_argument("-d", "--dividends", help="list of ticker symbols to get mean dividends info for", nargs='*', type=str)
	parser.add_argument("-y", "--last_n_years", help="year in which to get mean dividends from, default [1] = last 365 days from today", type=int, default=1)
	parser.add_argument("-i", "--period_years", help="interval period to query. if interval is bigger than years, then it will query period length, default [1] = 365 days to average over since last_n_years", type=int, default=1)
	parser.add_argument("-r", "--drip_amount", help="amount needed to reinvest the dividend to buy more share(s)", nargs='*', type=str)
	parser.add_argument("-a", "--show_all", help="get all the values supported in the script", default=False)
	parser.add_argument("-b", "--breakdown", help="show itemized list of tickers from available cash to maximize growth or dividends", type=int, default=False)

	args = parser.parse_args()

	if args.ticker_symbol is not None:
		for symbol in args.ticker_symbol :
			symbols_list.append(symbol.upper())

	if args.dividends is not None:
		for symbol in args.dividends:
			dividend_list.append(symbol.upper())

	if args.drip_amount is not None:
		for symbol in args.drip_amount:
			reinvestment_list.append(symbol.upper())


	# get names from the default file if no parameters passed
	if not symbols_list and not dividend_list and not reinvestment_list:
		symbols, count = getNames()

		if args.show_all:
			symbols_list        = symbols
			dividend_list       = symbols
			reinvestment_list   = symbols

		if args.ticker_symbol is not None:
			symbols_list        = symbols

		if args.dividends is not None:
			dividend_list       = symbols

		if args.drip_amount is not None:
			reinvestment_list   = symbols

		print("Found ", count, f" names from {default_file}")

	# only ticker is defined
	elif symbols_list and not dividend_list and not reinvestment_list:
		if args.dividends is not None:
			args.dividends      = symbols_list
			dividend_list       = symbols_list
		if args.drip_amount is not None:
			args.drip_amount    = symbols_list
			reinvestment_list   = symbols_list

	# only dividend is defined
	elif not symbols_list and dividend_list and not reinvestment_list:
		if args.ticker_symbol is not None:
			args.ticker_symbol  = dividend_list
			symbols_list        = dividend_list
		if args.drip_amount is not None:
			args.drip_amount    = dividend_list
			reinvestment_list   = dividend_list

	# only reinvestment is defined
	elif not symbols_list and not dividend_list and reinvestment_list:
		if args.ticker_symbol is not None:
			args.ticker_symbol  = reinvestment_list
			symbols_list        = reinvestment_list
		if args.dividends is not None:
			args.dividends      = reinvestment_list
			dividend_list       = reinvestment_list


	print("\nSettings as follows:")
	print("-----------------------------------------------------------------------------------")
	arguments = vars(args)
	list1 = []
	list2 = []

	for arg in arguments:
		value = getattr(args, arg)
		if arg and type(value) != list:
			list1.append([arg, value])
		elif arg:
			list2.append([arg, value])

	for arg in list1 :
		print(f"{arg[0]}\t{arg[1]}")

	for arg in list2:
		print(f"{arg[0]}\t{arg[1]}")

	#----------------------------------------------------------------

	if symbols_list:
		print(f"\n[Stock Price Now]\t\t{datetime.now().strftime('%d-%b-%Y')}",)
		print("-----------------------------------------------------------------------------------")

		# simple cost of the security now
		for ticker_symbol in symbols_list:
			print_current_price(ticker_symbol)

	# dividend information
	if dividend_list:
		# Set the time range for the past year
		start_date = datetime.now() - timedelta(days=dividend_timespan * max(args.last_n_years, args.period_years))
		end_date = start_date + timedelta(days=dividend_timespan * args.period_years)

		# Format dates for the Yahoo Finance API
		start_date_str = int(start_date.timestamp())
		end_date_str = int(end_date.timestamp())

		print(f"\n[Mean Dividend]\t\t\t{start_date.date().strftime('%d-%b-%Y')} over the next {args.period_years} year(s) or {end_date.date().strftime('%d-%b-%Y')}:")
		print("-----------------------------------------------------------------------------------")

		for ticker_symbol in dividend_list:
			print_dividend_data(ticker_symbol, start_date_str, end_date_str)

	# how much capital to get drip going
	if reinvestment_list:
		end_date = datetime.now()
		start_date = datetime.now() - timedelta(days=dividend_timespan * 1)

		# Format dates for the Yahoo Finance API
		start_date_str = int(start_date.timestamp())
		end_date_str = int(end_date.timestamp())

		dividend_cache.clear()

		print(f"\n[Drip Amount From Dividends]\t{start_date.date().strftime('%d-%b-%Y')} over the next 1 year(s) or {end_date.date().strftime('%d-%b-%Y')}:")
		print("-----------------------------------------------------------------------------------")

		for ticker_symbol in reinvestment_list:
			print_reinvestment_data(ticker_symbol, start_date_str, end_date_str)



if __name__ == "__main__":
	main()
