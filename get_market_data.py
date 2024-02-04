import sys
import json
import pdb
import argparse
from datetime import datetime, timedelta
from math import ceil
from utils.yahoo_finance import Api_Dojo as yf # yahoo finance api
#from utils.yahoo_finance import Yfinance as yf # yahoo finance api
from utils.process_args import Process_Args
from utils.caches import *
from data.breakdown import GenerateBreakdown as gb

default_file = "data/dividends_list.csv"
dividend_timespan = 365 # days

# caches to speed up repeated query
yf = yf()
ticker_cache = Ticker_Cache(yf)
dividend_cache = Dividend_Cache(yf)

def print_dividend_data(ticker_symbols, start_date, end_date):

	results = [dividend_cache.div(symbol, start_date, end_date) for symbol in ticker_symbols]

	# success: 0+ or failed: -1
	for symbol, (size, mean_dividend) in zip(ticker_symbols, results):
		payout_amount = mean_dividend * size
		print(f"{symbol}\tper payout:{round(mean_dividend,2)},total payout:{round(payout_amount,2)}")


def print_reinvestment_data(ticker_symbols, start_date, end_date):

	results = [dividend_cache.div(symbol, start_date, end_date) for symbol in ticker_symbols]

	# success: 0+ or failed: -1
	for symbol, (size, mean_dividend) in zip(ticker_symbols, results):
		if size > 0:
			if mean_dividend > 0:
				current_price = ticker_cache.price(symbol, date=None)
				share_count = current_price / mean_dividend
				drip_amount = ceil(share_count) * current_price

				print(f"{symbol}\tdrip amount:{round(drip_amount,2)},buy shares:{ceil(share_count)},per payout:{round(mean_dividend, 2)},cost per share:{round(current_price, 2)} ")
			else:
				print(f"{symbol}\tno dividends")
		else:
			print(f"{symbol}\tno dividend data")

# multiple ticker symbol query
def print_current_prices(ticker_symbols, query_date=None):

	prices_data = ticker_cache.prices(ticker_symbols, query_date)
	for symbol, value in prices_data.items():
		print(f"{symbol}\t{round(value,2)}")

# single ticker symbol query
def print_current_price(ticker_symbols, query_date=None):

	for symbol in ticker_symbols:
		price = ticker_cache.price(symbol, query_date)
		print(f"{symbol}\t{round(price,2)}")

def main():

	parser = argparse.ArgumentParser("Get market data")
	parser.add_argument("-t", "--ticker_symbol", help="list of ticker symbols to query prices", nargs='*', type=str)
	parser.add_argument("-d", "--dividends", help="list of ticker symbols to get mean dividends info for", nargs='*', type=str)
	parser.add_argument("-y", "--last_n_years", help="year in which to get mean dividends from, default [1] = last 365 days from today", type=int, default=1)
	parser.add_argument("-i", "--period_years", help="interval period to query. if interval is bigger than years, then it will query period length, default [1] = 365 days to average over since last_n_years", type=int, default=-1)
	parser.add_argument("-r", "--drip_amount", help="amount needed to reinvest the dividend to buy more share(s)", nargs='*', type=str)
	parser.add_argument("-a", "--show_all", help="get all the values supported in the script for a list of ticker symbols or from a file", nargs='*', type=str)
	parser.add_argument("-b", "--breakdown", help="show itemized list of tickers from available cash to maximize growth or dividends", nargs='+')

	args = parser.parse_args()
	p_args = Process_Args(args, default_file)

	if args.breakdown is not None and len(args.breakdown) > 1:
		bd = gb(yf, args.breakdown[0], args.breakdown[1:], ticker_cache, dividend_cache)
		bd.print()

	# get lists of data
	price_symbol_list, dividend_list, reinvestment_list = p_args.get_lists()

	if price_symbol_list:
		print(f"\n[Stock Price Now]\t\t{datetime.now().strftime('%d-%b-%Y')}",)
		print("-----------------------------------------------------------------------------------")
		#print_current_price(price_symbol_list, None)
		print_current_prices(price_symbol_list)

	# dividend information
	if dividend_list:
		# Set the time range for the past N years for the next PERIOD years
		start_date       = datetime.now() - timedelta(days=dividend_timespan * max(args.last_n_years, args.period_years))
		end_date         = start_date + timedelta(days=dividend_timespan * args.period_years)

		# Format dates for the Yahoo Finance API
		start_date_token =  yf.get_time(start_date)
		end_date_token   =  yf.get_time(end_date)

		print(f"\n[Mean Dividend]\t\t\t{start_date.date().strftime('%d-%b-%Y')} over the next {args.period_years} year(s) or {end_date.date().strftime('%d-%b-%Y')}:")
		print("-----------------------------------------------------------------------------------")
		print_dividend_data(dividend_list, start_date_token, end_date_token)

	# how much capital to get drip going
	if reinvestment_list:
		# Set the time range for the past year
		start_date       = datetime.now() - timedelta(days=dividend_timespan * 1)
		end_date         = datetime.now()

		# Format dates for the Yahoo Finance API
		start_date_token = yf.get_time(start_date)
		end_date_token   = yf.get_time(end_date)

		dividend_cache.clear_except_dates(start_date_token, end_date_token)

		print(f"\n[Drip Amount From Dividends]\t{start_date.date().strftime('%d-%b-%Y')} over the next 1 year(s) or {end_date.date().strftime('%d-%b-%Y')}:")
		print("-----------------------------------------------------------------------------------")
		print_reinvestment_data(reinvestment_list, start_date_token, end_date_token)

if __name__ == "__main__":
	main()
