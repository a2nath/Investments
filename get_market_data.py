import sys
import requests
import json
import pdb
import csv
import argparse
from private_keys import headers
from datetime import datetime, timedelta


default_file = "dividends_list.csv"
dividend_timespan = 365


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

		print(f"{ticker_symbol},{mean_dividend}")
		   
	else:
		print(f"Failed to fetch dividend data for {ticker_symbol}. Status code: {response.status_code}")
		return None

def getNames():
	names = []
	with open(default_file) as csv_file:
		csv_reader = csv.reader(csv_file)
		for row in csv_reader:
			names.append(row[0])
	return names, len(names)

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

		print(f"{ticker_symbol},{current_price}")
	else:
		print(f"Failed to fetch price data for {ticker_symbol}. Status code: {response.status_code}")

def main():

	# ticker symbols to work with
	symbols = []
	dividend_list = []

	parser = argparse.ArgumentParser("Get market data")
	parser.add_argument("-t", "--tickers", help="list of ticker symbols to query prices", nargs="+", type=str)
	parser.add_argument("-d", "--dividends", help="list of ticker symbols to get mean dividends info for", nargs="+", type=str)
	parser.add_argument("-y", "--last_n_years", help="year in which to get mean dividends from, default [1] = last 365 days from today", type=int, default=1)
	parser.add_argument("-i", "--interval_period_years", help="interval period to query. if interval is bigger than years, then it will query interval length, default [1] = 365 days to average over since last_n_years", type=int, default=1)

	args = parser.parse_args()
	
	print("\nSettings as follows:")
	print("-------------------------------------------------------")

	arguments = vars(args);
	for arg in arguments:
		print(arg, '\t', getattr(args, arg))


	if args.tickers is None and args.dividends is None:
		symbols, count = getNames()
		print("Found ", count, " names from default file")

	elif args.tickers is not None:
		for symbol in args.tickers:
			symbols.append(symbol)
	
	if args.dividends is not None:
		for symbol in args.dividends:
			dividend_list.append(symbol)
		
	
	if len(symbols) > 0:
		print("\nStock price now ", datetime.now())
		print("-------------------------------------------------------")
	
	for ticker_symbol in symbols:
		getPrice(ticker_symbol)

	# dividend information
	if len(dividend_list) > 0:
		# Set the time range for the past year
		start_date = datetime.now() - timedelta(days=dividend_timespan * max(args.last_n_years, args.interval_period_years))
		end_date = start_date + timedelta(days=dividend_timespan * args.interval_period_years)
	
		# Format dates for the Yahoo Finance API
		start_date_str = int(start_date.timestamp())
		end_date_str = int(end_date.timestamp())

		print(f"\nMean Dividend over {args.interval_period_years} years since {args.last_n_years}:")
		print("-------------------------------------------------------")
	
		for ticker_symbol in dividend_list:
			get_dividend_data(ticker_symbol, start_date_str, end_date_str)
	
if __name__ == "__main__":
	main()
