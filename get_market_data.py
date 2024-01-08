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

default_file = "data/dividends_list.csv"
dividend_timespan = 365 # days

# caches to speed up repeated query
yf = yf()
ticker_cache = Ticker_Cache(yf)
dividend_cache = Dividend_Cache(yf)

def print_dividend_data(ticker_symbol, start_date, end_date):
	size, mean_dividend = dividend_cache.div(ticker_symbol, start_date, end_date)
	payout_amount = mean_dividend * size

	print(f"{ticker_symbol}\tper payout:{round(mean_dividend,2)},total payout:{round(payout_amount,2)}")


def print_reinvestment_data(ticker_symbol, start_date, end_date):
	# success: 0+ or failed: -1
	size, mean_dividend = dividend_cache.div(ticker_symbol, start_date, end_date)

	if size > 0:
		if mean_dividend > 0:
			current_price = ticker_cache.price(ticker_symbol)
			share_count = current_price / mean_dividend
			drip_amount = ceil(share_count) * current_price

			print(f"{ticker_symbol}\tdrip amount:{round(drip_amount,2)},buy shares:{ceil(share_count)},per payout:{round(mean_dividend, 2)},cost per share:{round(current_price, 2)} ")
		else:
			print(f"{ticker_symbol}\tno dividends")
	else:
		print(f"{ticker_symbol}\tno dividend data")


def print_current_price(ticker_symbol, query_date=datetime.now()):
	price = ticker_cache.price(ticker_symbol)
	print(f"{ticker_symbol}\t{round(price,2)}")


def main():

	parser = argparse.ArgumentParser("Get market data")
	parser.add_argument("-t", "--ticker_symbol", help="list of ticker symbols to query prices", nargs='*', type=str)
	parser.add_argument("-d", "--dividends", help="list of ticker symbols to get mean dividends info for", nargs='*', type=str)
	parser.add_argument("-y", "--last_n_years", help="year in which to get mean dividends from, default [1] = last 365 days from today", type=int, default=1)
	parser.add_argument("-i", "--period_years", help="interval period to query. if interval is bigger than years, then it will query period length, default [1] = 365 days to average over since last_n_years", type=int, default=-1)
	parser.add_argument("-r", "--drip_amount", help="amount needed to reinvest the dividend to buy more share(s)", nargs='*', type=str)
	parser.add_argument("-a", "--show_all", help="get all the values supported in the script for a list of ticker symbols or from a file", nargs='*', type=str)
	parser.add_argument("-b", "--breakdown", help="show itemized list of tickers from available cash to maximize growth or dividends", type=int, default=False)

	args = parser.parse_args()
	p_args = Process_Args(args, default_file)

	# get lists of data
	price_symbol_list, dividend_list, reinvestment_list = p_args.get_lists()

	if price_symbol_list:
		print(f"\n[Stock Price Now]\t\t{datetime.now().strftime('%d-%b-%Y')}",)
		print("-----------------------------------------------------------------------------------")

		# simple cost of the security now
		for ticker_symbol in price_symbol_list:
			print_current_price(ticker_symbol)

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

		for ticker_symbol in dividend_list:
			print_dividend_data(ticker_symbol, start_date_token, end_date_token)

	# how much capital to get drip going
	if reinvestment_list:
		# Set the time range for the past year
		start_date       = datetime.now() - timedelta(days=dividend_timespan * 1)
		end_date         = datetime.now()

		# Format dates for the Yahoo Finance API
		start_date_token = yf.get_time(start_date)
		end_date_token   = yf.get_time(end_date)

		dividend_cache.clear_except_dates(start_date, end_date)

		print(f"\n[Drip Amount From Dividends]\t{start_date.date().strftime('%d-%b-%Y')} over the next 1 year(s) or {end_date.date().strftime('%d-%b-%Y')}:")
		print("-----------------------------------------------------------------------------------")

		for ticker_symbol in reinvestment_list:
			print_reinvestment_data(ticker_symbol, start_date_token, end_date_token)



if __name__ == "__main__":
	main()
